"""Step 24: real Admin requests and protected database preview state."""

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.sessions.backends.base import UpdateError
from django.contrib.sessions.backends.db import SessionStore as OriginalSessionStore
from django.contrib.sessions.models import Session
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape

from config.session_backend import PREVIEW_KEY, SessionStore
from events.doi_admin import VIEW_PERMISSIONS, WRITE_PERMISSIONS
from events.models import Event, EventResource, Resource
from events.services.crossref import CrossrefLookupError
from events.services.crossref_metadata import CrossrefMetadata


class DoiPreviewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser("preview-admin", password="test-only")
        cls.event = Event.objects.create(title="Target talk", starts_at=timezone.now())
        cls.other = Event.objects.create(title="Other talk", starts_at=timezone.now())
        cls.resource = Resource.objects.create(
            title="Current saved title", authors="", year=None,
            original_url="https://example.org/current", doi="10.1234/saved",
            metadata_source="manual", seed_key="preserved",
        )
        EventResource.objects.create(
            event=cls.other, resource=cls.resource, recommendation="Existing reason", display_order=-7,
        )

    def setUp(self):
        self.client.force_login(self.user)
        self.network = patch("requests.sessions.Session.request", side_effect=AssertionError("No real HTTP"))
        self.network_mock = self.network.start()
        self.addCleanup(self.network.stop)
        self.addCleanup(self.network_mock.assert_not_called)
        self.provider = patch(
            "events.services.doi_preview.fetch_metadata",
            return_value=CrossrefMetadata(
                "Fixture title", "Fixture author", 2020, "https://example.org/fixture",
                "10.1234/fixture", "research_paper",
            ),
        )
        self.lookup = self.provider.start()
        self.addCleanup(self.provider.stop)
        self.before = self.snapshot()

    def snapshot(self):
        return [list(model.objects.order_by("pk").values()) for model in (Event, Resource, EventResource)]

    def lookup_url(self, event=None):
        return reverse("admin:events_event_doi_lookup", args=[(event or self.event).pk])

    def fetch(self, doi="10.1234/fixture", event=None, client=None):
        response = (client or self.client).post(self.lookup_url(event), {"action": "fetch", "doi": doi})
        self.assertEqual(response.status_code, 302)
        return response.url

    def states(self):
        return Session.objects.get(session_key=self.client.session.session_key).get_decoded().get(PREVIEW_KEY, {})

    def review_data(self, **changes):
        return {
            "action": "review", "title": "Reviewed fixture", "authors": "", "year": "",
            "original_url": "https://example.org/reviewed", "resource_type": "article",
            "recommendation": "Reason entered", "display_order": "-3", **changes,
        }

    def staff(self, permissions):
        user = get_user_model().objects.create_user("staff-preview", is_staff=True)
        user.user_permissions.set(Permission.objects.filter(
            content_type__app_label="events", codename__in=[p.split(".")[1] for p in permissions],
        ))
        self.client.force_login(user)
        return user

    def test_entry_target_label_and_get_does_not_fetch_or_create_state(self):
        change = self.client.get(reverse("admin:events_event_change", args=[self.event.pk]))
        self.assertContains(change, self.lookup_url())
        response = self.client.get(self.lookup_url())
        self.assertContains(response, "Target talk: Target talk")
        self.assertContains(response, "DOI or DOI link")
        self.assertContains(response, "Fetch metadata")
        self.assertContains(response, "Add manually")
        self.assertContains(response, "data-pending=\"Fetching…\"")
        self.assertFalse(self.states())
        self.lookup.assert_not_called()
        self.assertEqual(self.snapshot(), self.before)

    def test_new_success_stores_only_bound_random_preview_and_no_business_write(self):
        url = self.fetch(" HTTPS://DOI.ORG/10.1234/FiXtUrE ")
        page = self.client.get(url)
        self.assertContains(page, "DOI: 10.1234/fixture")
        self.assertContains(page, "Fixture title")
        self.assertContains(page, "Save to event")
        states = self.states()
        self.assertEqual(len(states), 1)
        identity, state = next(iter(states.items()))
        self.assertRegex(identity, r"^[0-9a-f]{48}$")
        self.assertEqual(state["session_key"], self.client.session.session_key)
        self.assertEqual(state["user_id"], self.user.pk)
        self.assertEqual(state["event_id"], self.event.pk)
        self.assertEqual(state["expires_at"] - state["loaded_at"], 900)
        self.assertEqual(state["doi"], "10.1234/fixture")
        self.lookup.assert_called_once_with("10.1234/fixture")
        public = self.client.get(reverse("events:event-detail", args=[self.event.pk]))
        self.assertNotIn(identity, public.content.decode())
        self.assertNotIn(state["session_key"], public.content.decode())
        self.assertNotIn(PREVIEW_KEY, public.content.decode())
        self.assertEqual(self.snapshot(), self.before)

    def test_existing_saved_bibliography_readonly_and_never_calls_provider(self):
        self.resource.title = "<script>alert(1)</script> " + "long title " * 30
        self.resource.save()
        self.before = self.snapshot()
        url = self.fetch("https://doi.org/10.1234/SAVED")
        response = self.client.post(url, self.review_data(title="Forged shared title", doi="10.1234/replaced"))
        self.assertContains(response, "Saved bibliography is read-only")
        self.assertContains(response, escape(self.resource.title))
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertNotContains(response, 'id="id_title"')
        self.assertTrue(response.context["checked"])
        form = response.context["review_form"]
        for field in ("title", "authors", "year", "original_url", "resource_type"):
            self.assertTrue(form.fields[field].disabled)
        self.assertEqual(form.cleaned_data["title"], self.resource.title)
        self.assertEqual(form.cleaned_data["authors"], "")
        self.assertIsNone(form.cleaned_data["year"])
        self.lookup.assert_not_called()
        self.assertEqual(self.snapshot(), self.before)

    def test_existing_preview_rereads_current_edited_bibliography(self):
        url = self.fetch("10.1234/saved")
        self.resource.title = "Later shared edit"
        self.resource.save()
        current = self.snapshot()
        response = self.client.get(url)
        self.assertContains(response, "Later shared edit")
        self.assertEqual(self.snapshot(), current)
        self.lookup.assert_not_called()

    def test_preview_then_another_request_creates_same_doi_switches_to_readonly(self):
        url = self.fetch()
        Resource.objects.create(title="Concurrent saved fixture", original_url="https://example.org/new", doi="10.1234/fixture")
        current = self.snapshot()
        response = self.client.post(url, self.review_data(title="Discarded preview title"))
        self.assertTrue(response.context["existing"])
        self.assertEqual(response.context["review_form"].cleaned_data["title"], "Concurrent saved fixture")
        self.assertEqual(self.snapshot(), current)

    def test_invalid_doi_retains_raw_input_no_network_state_or_business_write(self):
        response = self.client.post(self.lookup_url(), {"action": "fetch", "doi": " invalid input "})
        self.assertContains(response, "Enter a valid DOI or DOI link.")
        self.assertEqual(response.context["lookup_form"].data["doi"], " invalid input ")
        self.assertFalse(self.states())
        self.lookup.assert_not_called()
        self.assertEqual(self.snapshot(), self.before)

    def test_all_safe_failures_keep_input_and_other_tab_and_no_business_write(self):
        old = self.fetch("10.1234/saved")
        original_states = self.states()
        for code in ("not_found", "rate_limited", "upstream_error", "invalid_response", "connection_failed", "timeout", "provider_unavailable"):
            with self.subTest(code=code):
                self.lookup.side_effect = CrossrefLookupError(code, "ignored")
                raw = " 10.1234/Failure "
                response = self.client.post(self.lookup_url(), {"action": "fetch", "doi": raw})
                self.assertContains(response, escape(CrossrefLookupError(code, raw).message))
                self.assertContains(response, "Add manually")
                self.assertEqual(response.context["lookup_form"].data["doi"], raw)
                self.assertEqual(response.context["can_retry"], code != "not_found")
                self.assertEqual(self.states(), original_states)
                self.assertEqual(self.snapshot(), self.before)
        self.assertEqual(self.client.get(old).status_code, 200)
        self.assertEqual(self.lookup.call_count, 7)

    def test_incomplete_metadata_requires_title_and_http_url_optional_fields_allowed(self):
        self.lookup.return_value = CrossrefMetadata("", "", None, "", "10.1234/fixture", "article")
        url = self.fetch()
        self.assertContains(self.client.get(url), "Some details are missing. Review before saving.")
        for edits in ({"title": "", "original_url": ""}, {"original_url": "ftp://example.org/file"}, {"year": "10000"}, {"display_order": "2147483648"}):
            with self.subTest(edits=edits):
                page = self.client.post(url, self.review_data(**edits))
                self.assertTrue(page.context["review_form"].errors)
                self.assertNotIn("checked", page.context)
        page = self.client.post(url, self.review_data())
        self.assertTrue(page.context["checked"])
        self.assertEqual(page.context["review_form"].cleaned_data["authors"], "")
        self.assertIsNone(page.context["review_form"].cleaned_data["year"])
        self.assertEqual(self.snapshot(), self.before)

    def test_review_preserves_inputs_and_fixed_deadline_without_state_write(self):
        url = self.fetch()
        states = self.states()
        response = self.client.post(url, self.review_data(title="Keep entered title", original_url="invalid"))
        self.assertContains(response, "Keep entered title")
        self.assertEqual(response.context["review_form"].data["recommendation"], "Reason entered")
        self.client.post(url, self.review_data())
        self.assertEqual(self.states(), states)
        self.assertEqual(self.snapshot(), self.before)

    def test_hidden_identity_values_cannot_change_trusted_doi_target_or_source(self):
        url = self.fetch()
        original = self.states()
        page = self.client.post(url, self.review_data(
            doi="10.1234/replaced", event_id=self.other.pk, user_id=999, resource_id=self.resource.pk,
            metadata_source="manual", preview_id="replacement",
        ))
        self.assertTrue(page.context["checked"])
        self.assertEqual(page.context["doi"], "10.1234/fixture")
        self.assertEqual(page.context["event"].pk, self.event.pk)
        self.assertEqual(self.states(), original)
        swapped = url.replace(f"/{self.event.pk}/doi/", f"/{self.other.pk}/doi/")
        self.assertContains(self.client.post(swapped, self.review_data()), "This preview is no longer valid.", status_code=400)
        self.assertEqual(self.snapshot(), self.before)

    def test_two_tabs_have_independent_ids_and_cancel_only_one(self):
        first = self.fetch()
        second = self.fetch(event=self.other)
        original = self.states()
        self.assertEqual(len(original), 2)
        self.assertNotEqual(first, second)
        response = self.client.post(first, {"action": "cancel"})
        self.assertRedirects(response, reverse("admin:events_event_change", args=[self.event.pk]))
        self.assertContains(self.client.get(first), "This preview is no longer valid.", status_code=400)
        self.assertEqual(self.client.get(second).status_code, 200)
        second_id = second.rstrip("/").split("/")[-1]
        self.assertEqual(self.states()[second_id], original[second_id])
        self.assertEqual(self.snapshot(), self.before)

    def test_expiry_boundary_and_invalid_missing_state_reject_review(self):
        instant = timezone.now()
        with patch("events.services.doi_preview.timezone.now", return_value=instant):
            url = self.fetch()
        for seconds, status in ((899, 200), (900, 400), (901, 400)):
            with self.subTest(seconds=seconds), patch("events.services.doi_preview.timezone.now", return_value=instant + timedelta(seconds=seconds)):
                response = self.client.post(url, self.review_data())
                self.assertEqual(response.status_code, status)
        self.assertEqual(self.client.get(url.replace(url.rstrip("/").split("/")[-1], "missing")).status_code, 400)
        self.assertEqual(self.snapshot(), self.before)

    def test_other_session_same_admin_other_admin_and_logged_out_cannot_use_preview(self):
        url = self.fetch()
        other = Client()
        other.force_login(self.user)
        self.assertEqual(other.get(url).status_code, 400)
        admin2 = get_user_model().objects.create_superuser("other-preview-admin", password="test-only")
        other.force_login(admin2)
        self.assertEqual(other.post(url, self.review_data()).status_code, 400)
        self.client.logout()
        self.assertEqual(self.client.post(url, self.review_data()).status_code, 302)
        self.assertEqual(self.snapshot(), self.before)

    def test_deleted_event_shows_missing_target_no_fetch(self):
        url = self.fetch()
        self.event.delete()
        current = self.snapshot()
        self.assertContains(self.client.get(url), "This talk is no longer available.", status_code=404)
        self.assertEqual(self.snapshot(), current)
        self.assertEqual(self.lookup.call_count, 1)

    def test_unknown_action_and_unsupported_methods_do_not_write(self):
        url = self.fetch()
        self.assertEqual(self.client.post(url, self.review_data(action="unknown")).status_code, 400)
        self.assertEqual(self.client.put(url).status_code, 405)
        self.assertEqual(self.client.delete(url).status_code, 405)
        self.assertEqual(self.snapshot(), self.before)

    def test_anonymous_nonstaff_and_each_missing_view_permission_are_rejected(self):
        self.client.logout()
        self.assertEqual(self.client.get(self.lookup_url()).status_code, 302)
        nonstaff = get_user_model().objects.create_user("not-staff")
        self.client.force_login(nonstaff)
        self.assertEqual(self.client.post(self.lookup_url(), {"action": "fetch", "doi": "10.1234/saved"}).status_code, 302)
        user = self.staff(WRITE_PERMISSIONS)
        for permission in VIEW_PERMISSIONS:
            with self.subTest(permission=permission):
                denied = Permission.objects.get(content_type__app_label="events", codename=permission.split(".")[1])
                user.user_permissions.remove(denied)
                self.assertEqual(self.client.get(self.lookup_url()).status_code, 403)
                user.user_permissions.add(denied)
        self.lookup.assert_not_called()
        self.assertEqual(self.snapshot(), self.before)

    def test_fetch_requires_write_permissions_and_new_resource_add_before_http(self):
        user = self.staff(WRITE_PERMISSIONS)
        for permission in ("events.change_event", "events.add_eventresource"):
            with self.subTest(permission=permission):
                denied = Permission.objects.get(content_type__app_label="events", codename=permission.split(".")[1])
                user.user_permissions.remove(denied)
                self.assertEqual(self.client.post(self.lookup_url(), {"action": "fetch", "doi": "10.1234/saved"}).status_code, 403)
                user.user_permissions.add(denied)
        self.assertEqual(self.client.post(self.lookup_url(), {"action": "fetch", "doi": "10.1234/new"}).status_code, 403)
        self.fetch("10.1234/saved")
        self.lookup.assert_not_called()
        self.assertEqual(self.snapshot(), self.before)

    def test_revoked_permissions_reject_review_and_cancel(self):
        user = self.staff((*WRITE_PERMISSIONS, "events.add_resource"))
        url = self.fetch()
        user.user_permissions.remove(Permission.objects.get(content_type__app_label="events", codename="add_resource"))
        self.assertEqual(self.client.post(url, self.review_data()).status_code, 403)
        user.user_permissions.remove(Permission.objects.get(content_type__app_label="events", codename="add_eventresource"))
        self.assertEqual(self.client.post(url, {"action": "cancel"}).status_code, 403)
        self.assertEqual(self.snapshot(), self.before)

    def test_real_csrf_fetch_review_cancel_require_valid_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        client.get(self.lookup_url())
        self.assertEqual(client.post(self.lookup_url(), {"action": "fetch", "doi": "10.1234/saved"}).status_code, 403)
        self.assertEqual(client.post(self.lookup_url(), {"action": "fetch", "doi": "10.1234/saved", "csrfmiddlewaretoken": "forged"}).status_code, 403)
        token = client.cookies["csrftoken"].value
        response = client.post(self.lookup_url(), {"action": "fetch", "doi": "10.1234/saved", "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 302)
        url = response.url
        for action in ("review", "cancel"):
            self.assertEqual(client.post(url, {"action": action}).status_code, 403)
        self.assertEqual(client.post(url, {**self.review_data(), "csrfmiddlewaretoken": token}).status_code, 200)
        self.assertEqual(client.post(url, {"action": "cancel", "csrfmiddlewaretoken": token}).status_code, 302)
        self.lookup.assert_not_called()
        self.assertEqual(self.snapshot(), self.before)

    def test_stale_default_middleware_save_preserves_new_and_cancelled_previews(self):
        key = self.client.session.session_key
        stale_before_fetch = SessionStore(key)
        stale_before_fetch.items()
        first = self.fetch()
        stale_before_cancel = SessionStore(key)
        stale_before_cancel.items()
        second = self.fetch(event=self.other)
        self.client.post(first, {"action": "cancel"})
        expected = self.states()
        for stale in (stale_before_fetch, stale_before_cancel):
            stale["unrelated"] = "ordinary middleware save"
            stale[PREVIEW_KEY] = {"forged": {"status": "active"}}
            stale.save()
            self.assertEqual(self.states(), expected)
        self.assertEqual(self.client.get(second).status_code, 200)
        self.assertEqual(self.client.get(first).status_code, 400)

    def test_save_every_request_preserves_tabs_and_cancelled_state(self):
        with self.settings(SESSION_SAVE_EVERY_REQUEST=True):
            first = self.fetch()
            second = self.fetch()
            self.client.post(first, {"action": "cancel"})
            self.assertEqual(self.client.get(second).status_code, 200)
            self.assertEqual(self.client.get(first).status_code, 400)
            self.assertEqual(len(self.states()), 2)
        self.assertEqual(self.snapshot(), self.before)

    def test_session_compatibility_and_logout_deleted_row_cannot_be_resurrected(self):
        original = OriginalSessionStore()
        original["legacy"] = "compatible"
        original.save()
        custom = SessionStore(original.session_key)
        self.assertEqual(custom["legacy"], "compatible")
        custom["ordinary"] = "changed"
        custom.save()
        self.assertEqual(OriginalSessionStore(original.session_key)["ordinary"], "changed")
        stale = SessionStore(self.client.session.session_key)
        stale.items()
        self.fetch()
        self.client.logout()
        stale["unrelated"] = "late"
        with self.assertRaises(UpdateError):
            stale.save()
        self.assertFalse(Session.objects.filter(session_key=stale.session_key).exists())

    def test_preview_session_write_failure_rolls_back_and_preserves_other_preview(self):
        self.fetch("10.1234/saved")
        expected = self.states()
        with patch.object(Session, "save", side_effect=RuntimeError("State write failed")):
            with self.assertRaisesMessage(RuntimeError, "State write failed"):
                self.fetch()
        self.assertEqual(self.states(), expected)
        self.assertEqual(self.snapshot(), self.before)
