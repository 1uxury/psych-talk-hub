"""Step 25: actual Admin confirmation, replay and atomic result persistence."""

from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.sessions.models import Session
from django.db import OperationalError, connection
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape

from config.session_backend import PREVIEW_KEY, SessionStore
from events.doi_permissions import WRITE_PERMISSIONS
from events.models import Event, EventResource, Resource
from events.services.crossref_metadata import CrossrefMetadata


class DoiConfirmationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser("confirm-admin", password="test-only")
        cls.event = Event.objects.create(title="Confirmation target", starts_at=timezone.now())
        cls.other = Event.objects.create(title="Other target", starts_at=timezone.now())
        cls.resource = Resource.objects.create(
            title="Current saved book", authors="", year=None, doi="10.1234/saved",
            original_url="https://example.org/saved", metadata_source="manual", seed_key="keep",
        )
        cls.link = EventResource.objects.create(
            event=cls.other, resource=cls.resource, recommendation="Other reason", display_order=9,
        )

    def setUp(self):
        self.client.force_login(self.user)
        network = patch("requests.sessions.Session.request", side_effect=AssertionError("No real HTTP"))
        self.network = network.start()
        self.addCleanup(network.stop)
        self.addCleanup(self.network.assert_not_called)
        provider = patch("events.services.doi_preview.fetch_metadata", return_value=CrossrefMetadata(
            "Provider fixture", "Fixture author", 2020, "https://example.org/fixture",
            "10.1234/new", "research_paper",
        ))
        self.provider = provider.start()
        self.addCleanup(provider.stop)

    def snapshot(self):
        return [list(m.objects.order_by("pk").values()) for m in (Event, Resource, EventResource)]

    def states(self):
        return Session.objects.get(session_key=self.client.session.session_key).get_decoded()[PREVIEW_KEY]

    def fetch(self, doi="10.1234/new", event=None, client=None):
        response = (client or self.client).post(
            reverse("admin:events_event_doi_lookup", args=[(event or self.event).pk]),
            {"action": "fetch", "doi": doi},
        )
        self.assertEqual(response.status_code, 302)
        return response.url

    def submitted(self, **changes):
        return {
            "action": "save", "title": "Reviewed fixture", "authors": "", "year": "",
            "original_url": "https://example.org/reviewed", "resource_type": "article",
            "recommendation": "My recommendation", "display_order": "-5", **changes,
        }

    def save(self, url, **changes):
        return self.client.post(url, self.submitted(**changes))

    def staff(self):
        user = get_user_model().objects.create_user("confirmation-staff", is_staff=True)
        user.user_permissions.set(Permission.objects.filter(
            content_type__app_label="events", codename__in=[p.split(".")[1] for p in (*WRITE_PERMISSIONS, "events.add_resource")],
        ))
        self.client.force_login(user)
        return user

    def test_get_fetch_and_check_never_save_then_confirmation_is_public(self):
        before = self.snapshot()
        url = self.fetch(" HTTPS://DOI.ORG/10.1234/NEW ")
        self.assertContains(self.client.get(url), 'data-pending="Saving…"')
        self.client.post(url, self.submitted(action="review"))
        self.assertEqual(self.snapshot(), before)
        states = self.states()
        self.assertRedirects(self.save(url), url)
        page = self.client.get(url)
        self.assertContains(page, "Resource added to this talk.")
        self.assertContains(page, f'href="/events/{self.event.pk}"')
        resource = Resource.objects.get(doi="10.1234/new")
        link = EventResource.objects.get(event=self.event, resource=resource)
        self.assertEqual((resource.title, resource.authors, resource.year, resource.metadata_source), ("Reviewed fixture", "", None, "crossref"))
        self.assertEqual((link.recommendation, link.display_order), ("My recommendation", -5))
        identity = url.rstrip("/").split("/")[-1]
        state = self.states()[identity]
        self.assertEqual(state["status"], "saved")
        self.assertEqual(state["expires_at"], states[identity]["expires_at"])
        self.assertEqual(state["result"]["association_id"], link.pk)
        public = Client().get(reverse("events:event-detail", args=[self.event.pk]))
        self.assertEqual(public.json()["resource_count"], 1)
        reading = public.json()["resources"][0]
        self.assertEqual((reading["title"], reading["recommendation"], reading["display_order"]), (resource.title, link.recommendation, -5))
        self.assertNotIn(identity, public.content.decode())
        self.provider.assert_called_once_with("10.1234/new")

    def test_saved_doi_ignores_forged_shared_fields_and_only_creates_target_link(self):
        original = list(Resource.objects.values())
        url = self.fetch("10.1234/saved")
        self.assertRedirects(self.save(url, title="Forged", original_url="javascript:alert(1)", year="10000", resource_type="bad"), url)
        self.assertEqual(list(Resource.objects.values()), original)
        self.link.refresh_from_db()
        self.assertEqual((self.link.recommendation, self.link.display_order), ("Other reason", 9))
        self.assertEqual(EventResource.objects.filter(resource=self.resource).count(), 2)
        self.provider.assert_not_called()

    def test_already_linked_reports_duplicate_and_keeps_current_reason_order(self):
        url = self.fetch("10.1234/saved", event=self.other)
        before = self.snapshot()
        self.assertRedirects(self.save(url), url)
        self.assertContains(self.client.get(url), "This resource is already linked to this talk.")
        self.assertContains(self.client.get(url), reverse("admin:events_eventresource_change", args=[self.link.pk]))
        self.assertEqual(self.snapshot(), before)

    def test_repeat_confirmation_ignores_even_invalid_new_fields_and_keeps_edits(self):
        url = self.fetch()
        self.save(url)
        link = EventResource.objects.get(event=self.event)
        link.recommendation, link.display_order = "Later edited reason", 7
        link.save()
        before, states = self.snapshot(), self.states()
        self.assertRedirects(self.save(url, title="", original_url="", recommendation="Overwrite", display_order="invalid"), url)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.states(), states)
        self.provider.assert_called_once()

    def test_removed_success_result_rejects_old_confirmation_even_if_pair_recreated(self):
        url = self.fetch()
        self.save(url)
        old = EventResource.objects.get(event=self.event)
        resource = old.resource
        old.delete()
        before = self.snapshot()
        self.assertContains(self.save(url), "This preview is no longer valid.", status_code=400)
        self.assertEqual(self.snapshot(), before)
        replacement = EventResource.objects.create(event=self.event, resource=resource)
        before = self.snapshot()
        self.assertContains(self.client.get(url), "This preview is no longer valid.", status_code=400)
        self.assertEqual(self.save(url).status_code, 400)
        self.assertEqual(self.snapshot(), before)
        self.assertNotEqual(replacement.pk, old.pk)

    def test_current_bibliography_created_or_edited_after_fetch_wins(self):
        url = self.fetch()
        resource = Resource.objects.create(
            title="Saved after preview", doi="10.1234/new", original_url="https://example.org/current",
            authors="", year=None, metadata_source="manual", seed_key="current",
        )
        self.save(url, title="Discard")
        resource.refresh_from_db()
        self.assertEqual((resource.title, resource.metadata_source, resource.seed_key), ("Saved after preview", "manual", "current"))
        url2 = self.fetch("10.1234/new", event=self.other)
        resource.title = "Shared later edit"
        resource.save()
        self.save(url2)
        resource.refresh_from_db()
        self.assertEqual(resource.title, "Shared later edit")
        self.assertEqual(EventResource.objects.filter(resource=resource).count(), 2)

    def test_actual_save_requires_valid_fields_and_retains_input(self):
        url = self.fetch()
        before, states = self.snapshot(), self.states()
        for changes in ({"title": ""}, {"original_url": "ftp://example.org/a"}, {"year": "10000"}, {"display_order": "2147483648"}, {"resource_type": "bad"}):
            with self.subTest(changes=changes):
                response = self.save(url, **changes)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["review_form"].errors)
                self.assertEqual(response.context["review_form"].data["recommendation"], "My recommendation")
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.states(), states)

    def test_save_expiry_before_at_and_after_original_deadline(self):
        for seconds in (899, 900, 901):
            with self.subTest(seconds=seconds):
                instant = timezone.now()
                with patch("events.services.doi_preview.timezone.now", return_value=instant):
                    url = self.fetch(f"10.1234/expiry-{seconds}")
                original = self.states()
                with patch("events.services.doi_preview.timezone.now", return_value=instant + timedelta(seconds=seconds)):
                    self.client.post(url, self.submitted(action="review"))
                    response = self.save(url)
                self.assertEqual(response.status_code, 302 if seconds == 899 else 400)
                self.assertEqual(Resource.objects.filter(doi=f"10.1234/expiry-{seconds}").exists(), seconds == 899)
                identity = url.rstrip("/").split("/")[-1]
                self.assertEqual(self.states()[identity]["expires_at"], original[identity]["expires_at"])

    def test_saved_result_expires_and_does_not_renew_on_refresh_or_replay(self):
        instant = timezone.now()
        with patch("events.services.doi_preview.timezone.now", return_value=instant):
            url = self.fetch()
            self.save(url)
        before, state = self.snapshot(), self.states()
        with patch("events.services.doi_preview.timezone.now", return_value=instant + timedelta(seconds=900)):
            self.assertEqual(self.save(url).status_code, 400)
            self.assertEqual(self.client.get(url).status_code, 400)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.states(), state)

    def test_cancelled_missing_state_and_wrong_target_never_save(self):
        first, second = self.fetch(), self.fetch()
        self.client.post(first, {"action": "cancel"})
        before = self.snapshot()
        for url in (first, second.replace(f"/{self.event.pk}/doi/", f"/{self.other.pk}/doi/"), second.replace(second.rstrip("/").split("/")[-1], "missing")):
            self.assertEqual(self.save(url).status_code, 400)
            self.assertEqual(self.snapshot(), before)
        self.assertRedirects(self.save(second), second)

    def test_other_session_admin_logout_and_password_change_reject_save(self):
        url = self.fetch()
        before = self.snapshot()
        another = Client()
        another.force_login(self.user)
        self.assertEqual(another.post(url, self.submitted()).status_code, 400)
        admin2 = get_user_model().objects.create_superuser("confirm-other", password="test-only")
        another.force_login(admin2)
        self.assertEqual(another.post(url, self.submitted()).status_code, 400)
        self.client.logout()
        self.assertEqual(self.save(url).status_code, 302)
        self.client.force_login(self.user)
        url = self.fetch()
        self.user.set_password("changed-test-password")
        self.user.save()
        self.assertEqual(self.save(url).status_code, 302)
        self.assertEqual(self.snapshot(), before)

    def test_hidden_identities_never_select_target_doi_resource_or_source(self):
        url = self.fetch()
        self.save(url, event_id=self.other.pk, doi="10.1234/saved", resource_id=self.resource.pk,
                  user_id=999, preview_id="forged", metadata_source="manual", seed_key="forged")
        resource = Resource.objects.get(doi="10.1234/new")
        self.assertEqual((resource.metadata_source, resource.seed_key), ("crossref", None))
        self.assertTrue(EventResource.objects.filter(event=self.event, resource=resource).exists())
        self.assertFalse(EventResource.objects.filter(event=self.other, resource=resource).exists())

    def test_each_revoked_confirmation_permission_and_inactive_staff_are_rejected(self):
        user = self.staff()
        url = self.fetch()
        before = self.snapshot()
        for name in (*WRITE_PERMISSIONS, "events.add_resource"):
            permission = Permission.objects.get(content_type__app_label="events", codename=name.split(".")[1])
            user.user_permissions.remove(permission)
            self.assertEqual(self.save(url).status_code, 403)
            self.assertEqual(self.snapshot(), before)
            user.user_permissions.add(permission)
        for field in ("is_active", "is_staff"):
            setattr(user, field, False)
            user.save()
            self.assertEqual(self.save(url).status_code, 302)
            setattr(user, field, True)
            user.save()
            self.client.force_login(user)
            url = self.fetch()
        self.assertEqual(self.snapshot(), before)

    def test_no_resource_add_permission_needed_for_saved_resource_or_replay(self):
        user = self.staff()
        url = self.fetch("10.1234/saved")
        user.user_permissions.remove(Permission.objects.get(content_type__app_label="events", codename="add_resource"))
        self.assertRedirects(self.save(url), url)
        self.assertRedirects(self.save(url), url)
        self.provider.assert_not_called()

    def test_fresh_permissions_are_rechecked_inside_final_transaction(self):
        user = self.staff()
        url = self.fetch()
        from events.services import doi_confirmation
        actual = doi_confirmation.confirm_preview
        def revoke(request, *args):
            # The view has already checked a cached user permission set.
            user.user_permissions.remove(Permission.objects.get(content_type__app_label="events", codename="add_eventresource"))
            return actual(request, *args)
        before = self.snapshot()
        with patch("events.doi_admin.confirm_preview", side_effect=revoke):
            self.assertEqual(self.save(url).status_code, 403)
        self.assertEqual(self.snapshot(), before)

    def test_deleted_target_before_or_during_confirmation_has_safe_return(self):
        url = self.fetch()
        self.event.delete()
        before = self.snapshot()
        response = self.save(url)
        self.assertContains(response, "This talk is no longer available.", status_code=404)
        self.assertContains(response, reverse("admin:events_event_changelist"), status_code=404)
        self.assertEqual(self.snapshot(), before)

    def test_deleted_target_after_view_read_is_rechecked_by_transaction(self):
        url = self.fetch()
        from events.services.doi_confirmation import confirm_preview as actual
        def delete_then_confirm(request, *args):
            self.event.delete()
            return actual(request, *args)
        with patch("events.doi_admin.confirm_preview", side_effect=delete_then_confirm):
            self.assertContains(self.save(url), "This talk is no longer available.", status_code=404)
        self.assertFalse(Resource.objects.filter(doi="10.1234/new").exists())

    def test_result_write_failure_rolls_back_business_and_state_retains_values_retry(self):
        url = self.fetch()
        other_url = self.fetch("10.1234/saved", event=self.other)
        before, states = self.snapshot(), self.states()
        actual = Session.save
        def fail_result(row, *args, **kwargs):
            if any(s.get("status") == "saved" for s in row.get_decoded().get(PREVIEW_KEY, {}).values()):
                raise OperationalError("private database detail")
            return actual(row, *args, **kwargs)
        with patch.object(Session, "save", new=fail_result):
            response = self.save(url, title="Keep edited title")
        self.assertContains(response, escape("We couldn't save this resource. Please try again."))
        self.assertNotContains(response, "private database detail")
        self.assertContains(response, "Keep edited title")
        self.assertContains(response, "Save to event")
        self.assertEqual(response.context["review_form"].data["display_order"], "-5")
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.states(), states)
        self.assertFalse(connection.needs_rollback)
        self.assertEqual(self.client.get(other_url).status_code, 200)
        self.assertRedirects(self.save(url, title="Keep edited title"), url)
        self.assertEqual(Resource.objects.get(doi="10.1234/new").title, "Keep edited title")

    def test_real_database_link_failure_rolls_back_resource_and_can_retry(self):
        url = self.fetch()
        before, states = self.snapshot(), self.states()
        from django.db.models import Model
        def fail_link(link, *args, **kwargs):
            link.recommendation = None
            return Model.save(link, *args, **kwargs)
        with patch.object(EventResource, "save", new=fail_link):
            response = self.save(url)
        self.assertContains(response, escape("We couldn't save this resource. Please try again."))
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.states(), states)
        self.assertFalse(connection.needs_rollback)
        self.assertRedirects(self.save(url), url)

    def test_stale_session_and_save_every_request_preserve_completed_result(self):
        with self.settings(SESSION_SAVE_EVERY_REQUEST=True):
            url = self.fetch()
            stale = SessionStore(self.client.session.session_key)
            stale.items()
            self.save(url)
            completed = self.states()
            stale["ordinary"] = "late request"
            stale.save()
            self.assertEqual(self.states(), completed)
            self.assertRedirects(self.save(url), url)
            self.assertEqual(EventResource.objects.filter(event=self.event).count(), 1)

    def test_real_csrf_save_and_replay_require_valid_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        client.get(reverse("admin:events_event_doi_lookup", args=[self.event.pk]))
        token = client.cookies["csrftoken"].value
        response = client.post(reverse("admin:events_event_doi_lookup", args=[self.event.pk]),
                               {"action": "fetch", "doi": "10.1234/saved", "csrfmiddlewaretoken": token})
        url = response.url
        before = self.snapshot()
        for csrf in ({}, {"csrfmiddlewaretoken": "forged"}):
            self.assertEqual(client.post(url, {**self.submitted(), **csrf}).status_code, 403)
            self.assertEqual(self.snapshot(), before)
        self.assertEqual(client.post(url, {**self.submitted(), "csrfmiddlewaretoken": token}).status_code, 302)
        before = self.snapshot()
        self.assertEqual(client.post(url, self.submitted()).status_code, 403)
        self.assertEqual(self.snapshot(), before)

    def test_expiry_after_event_lock_or_business_insert_rolls_back(self):
        from events.services import doi_confirmation
        for expire_after_insert in (False, True):
            with self.subTest(expire_after_insert=expire_after_insert):
                instant = timezone.now()
                with patch("events.services.doi_preview.timezone.now", return_value=instant):
                    url = self.fetch("10.1234/late-expiry")
                before, states = self.snapshot(), self.states()
                original = doi_confirmation._get_state
                calls = 0
                def expire(request, data, event_id, preview_id, **kwargs):
                    nonlocal calls
                    calls += 1
                    threshold = 3 if expire_after_insert else 2
                    now = instant + timedelta(seconds=900 if calls >= threshold else 899)
                    with patch("events.services.doi_preview.timezone.now", return_value=now):
                        return original(request, data, event_id, preview_id, **kwargs)
                with patch("events.services.doi_confirmation._get_state", side_effect=expire):
                    self.assertEqual(self.save(url).status_code, 400)
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.states(), states)

    def test_result_failure_for_existing_shared_book_rolls_back_only_new_link(self):
        url = self.fetch("10.1234/saved")
        before, states = self.snapshot(), self.states()
        actual = Session.save
        def fail(row, *args, **kwargs):
            if any(s.get("status") == "saved" for s in row.get_decoded().get(PREVIEW_KEY, {}).values()):
                raise OperationalError("private result failure")
            return actual(row, *args, **kwargs)
        with patch.object(Session, "save", new=fail):
            self.assertEqual(self.save(url).status_code, 200)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.states(), states)

    def test_malformed_server_state_rejects_without_business_write(self):
        url = self.fetch()
        identity = url.rstrip("/").split("/")[-1]
        row = Session.objects.get(session_key=self.client.session.session_key)
        original = row.get_decoded()
        before = self.snapshot()
        from copy import deepcopy
        for field, value in (("expires_at", None), ("expires_at", float("nan")), ("doi", None), ("bibliography", None), ("status", "unknown")):
            data = deepcopy(original)
            data[PREVIEW_KEY][identity][field] = value
            row.session_data = self.client.session.encode(data)
            row.save(update_fields=["session_data"])
            self.assertEqual(self.save(url).status_code, 400)
            self.assertEqual(self.snapshot(), before)
