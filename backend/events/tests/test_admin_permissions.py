"""Step 28: model permission matrix and real CSRF across Admin operations."""

from unittest.mock import patch

from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.sessions.models import Session
from django.core.exceptions import PermissionDenied
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from config.session_backend import PREVIEW_KEY
from events.models import Event, EventResource, Resource
from events.services.crossref_metadata import CrossrefMetadata
from events.services.doi_confirmation import confirm_preview


class AdminPermissionMatrixTests(TestCase):
    import_permissions = (
        "view_event", "view_resource", "view_eventresource",
        "change_event", "add_eventresource",
    )
    view_permissions = import_permissions[:3]
    event_warning = "Delete this talk and its reading links? Shared resources will be kept."

    @classmethod
    def setUpTestData(cls):
        cls.permissions = list(Permission.objects.filter(content_type__app_label="events"))
        cls.staff = get_user_model().objects.create_user("matrix-staff", is_staff=True)
        cls.staff.user_permissions.set(cls.permissions)
        cls.superuser = get_user_model().objects.create_superuser("matrix-admin", password="test-only")
        cls.event = Event.objects.create(title="Matrix talk A", starts_at=timezone.now(), seed_key="matrix-a")
        cls.other = Event.objects.create(title="Matrix talk B", starts_at=cls.event.starts_at)
        cls.empty = Event.objects.create(title="Empty matrix talk", starts_at=cls.event.starts_at)
        cls.resource = Resource.objects.create(
            title="Shared matrix reading", authors="", year=None, doi="10.1234/matrix-saved",
            original_url="https://example.org/shared", metadata_source="crossref", seed_key="matrix-book",
        )
        cls.exclusive = Resource.objects.create(title="Only A", original_url="https://example.org/a")
        cls.unlinked = Resource.objects.create(title="Unlinked", original_url="https://example.org/unlinked")
        cls.link = EventResource.objects.create(
            event=cls.event, resource=cls.resource, recommendation="Reason A", display_order=-3,
        )
        cls.other_link = EventResource.objects.create(
            event=cls.other, resource=cls.resource, recommendation="Reason B", display_order=8,
        )
        EventResource.objects.create(event=cls.event, resource=cls.exclusive)

    def setUp(self):
        self.client.force_login(self.staff)
        network = patch("requests.sessions.Session.request", side_effect=AssertionError("No real HTTP"))
        network_mock = network.start()
        self.addCleanup(network.stop)
        self.addCleanup(network_mock.assert_not_called)
        provider = patch("events.services.doi_preview.fetch_metadata", return_value=CrossrefMetadata(
            "Provider fixture", "Fixture author", 2020, "https://example.org/fixture",
            "10.1234/matrix-new", "research_paper",
        ))
        self.provider = provider.start()
        self.addCleanup(provider.stop)

    def url(self, model, action, obj=None):
        return reverse(f"admin:events_{model}_{action}", args=[obj.pk] if obj else None)

    def lookup_url(self, event=None):
        return reverse("admin:events_event_doi_lookup", args=[(event or self.event).pk])

    def snapshot(self):
        return [list(model.objects.order_by("pk").values()) for model in (Event, Resource, EventResource, LogEntry)]

    def states(self, client=None):
        session_key = (client or self.client).session.session_key
        return Session.objects.get(session_key=session_key).get_decoded().get(PREVIEW_KEY, {})

    def grant(self, *codenames):
        self.staff.user_permissions.set([p for p in self.permissions if p.codename in codenames])

    def revoke(self, codename):
        self.staff.user_permissions.remove(next(p for p in self.permissions if p.codename == codename))

    def restore_permissions(self):
        self.staff.user_permissions.set(self.permissions)

    def event_data(self):
        return {
            "title": "New matrix talk", "description": "", "topic": "", "speaker": "",
            "starts_at_0": "2026-12-01", "starts_at_1": "18:00:00", "_save": "Save",
        }

    def book_data(self):
        return {
            "title": "Edited matrix book", "authors": "", "year": "",
            "original_url": "https://example.org/edited", "resource_type": "article", "_save": "Save",
        }

    def link_data(self):
        return {"event": self.empty.pk, "resource": self.unlinked.pk, "recommendation": "New reason", "display_order": "-9", "_save": "Save"}

    def review_data(self, action="save"):
        return {
            **self.book_data(), "action": action, "recommendation": "Reviewed reason", "display_order": "-5",
        }

    def batch_data(self):
        return {"action": "delete_selected", ACTION_CHECKBOX_NAME: [self.event.pk, self.empty.pk]}

    def fetch(self, doi="10.1234/matrix-new", *, client=None, event=None, token=None):
        data = {"action": "fetch", "doi": doi}
        if token:
            data["csrfmiddlewaretoken"] = token
        response = (client or self.client).post(self.lookup_url(event), data)
        self.assertEqual(response.status_code, 302)
        return response.url

    def operations(self, preview_url):
        return [
            (self.url("event", "add"), self.event_data()),
            (self.url("event", "change", self.event), self.event_data()),
            (self.url("resource", "add"), self.book_data()),
            (self.url("resource", "change", self.resource), self.book_data()),
            (self.url("eventresource", "add"), self.link_data()),
            (self.url("eventresource", "change", self.link), self.link_data()),
            (self.url("eventresource", "delete", self.link), {"post": "yes"}),
            (self.url("event", "delete", self.event), {"post": "yes"}),
            (self.url("event", "changelist"), {**self.batch_data(), "post": "yes"}),
            (self.url("resource", "delete", self.unlinked), {"post": "yes"}),
            (self.url("resource", "changelist"), {"action": "delete_selected", ACTION_CHECKBOX_NAME: [self.unlinked.pk], "post": "yes"}),
            (self.lookup_url(), {"action": "fetch", "doi": "10.1234/matrix-new"}),
            *[(preview_url, self.review_data(action)) for action in ("review", "save", "cancel")],
        ]

    def test_anonymous_nonstaff_and_inactive_sessions_cannot_reach_any_operation(self):
        preview = self.fetch()
        before, states = self.snapshot(), self.states()
        for identity in ("anonymous", "nonstaff", "inactive"):
            client = Client()
            if identity != "anonymous":
                user = get_user_model().objects.create_user(
                    f"matrix-{identity}", is_staff=identity == "inactive", is_active=identity != "inactive",
                )
                user.user_permissions.set(self.permissions)
                client.force_login(user)
            for url, data in self.operations(preview):
                with self.subTest(identity=identity, url=url, action=data.get("action")):
                    for response in (client.get(url), client.post(url, data)):
                        self.assertEqual(response.status_code, 302)
                        self.assertIn("/admin/login/", response.url)
                    self.assertEqual(self.snapshot(), before)
                    self.assertEqual(self.states(), states)
        self.assertEqual(self.provider.call_count, 1)

    def test_staff_without_model_permissions_cannot_write_any_operation(self):
        preview = self.fetch()
        self.grant()
        before, states = self.snapshot(), self.states()
        for url, data in self.operations(preview):
            with self.subTest(url=url, action=data.get("action")):
                self.assertEqual(self.client.post(url, data).status_code, 403)
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.states(), states)

    def test_event_creation_requires_add_event_and_no_unrelated_permission(self):
        self.revoke("add_event")
        before = self.snapshot()
        url = self.url("event", "add")
        self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.post(url, self.event_data()).status_code, 403)
        self.assertEqual(self.snapshot(), before)
        self.grant("add_event")
        self.assertEqual(self.client.post(url, self.event_data()).status_code, 302)
        self.assertTrue(Event.objects.filter(title="New matrix talk").exists())

    def test_manual_creation_requires_add_resource_and_preserves_manual_identity(self):
        self.revoke("add_resource")
        before = self.snapshot()
        url = self.url("resource", "add")
        self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.post(url, self.book_data()).status_code, 403)
        self.assertEqual(self.snapshot(), before)
        self.grant("add_resource")
        self.assertEqual(self.client.post(url, {**self.book_data(), "doi": "10.1234/forged", "metadata_source": "crossref"}).status_code, 302)
        book = Resource.objects.get(title="Edited matrix book")
        self.assertEqual((book.doi, book.metadata_source, book.seed_key), (None, "manual", None))

    def test_event_change_permission_is_rechecked_after_edit_page(self):
        url = self.url("event", "change", self.event)
        self.assertEqual(self.client.get(url).status_code, 200)
        self.revoke("change_event")
        before = self.snapshot()
        self.assertEqual(self.client.post(url, self.event_data()).status_code, 403)
        self.assertEqual(self.snapshot(), before)

    def test_each_native_association_add_permission_is_required(self):
        required = ("add_eventresource", "change_event", "view_resource")
        url = self.url("eventresource", "add")
        before = self.snapshot()
        for missing in required:
            with self.subTest(missing=missing):
                self.restore_permissions()
                self.revoke(missing)
                self.assertEqual(self.client.get(url).status_code, 403)
                self.assertEqual(self.client.post(url, self.link_data()).status_code, 403)
                self.assertEqual(self.snapshot(), before)
        self.grant(*required)
        self.assertEqual(self.client.post(url, self.link_data()).status_code, 302)
        link = EventResource.objects.get(event=self.empty, resource=self.unlinked)
        self.assertEqual((link.recommendation, link.display_order), ("New reason", -9))

    def test_each_import_view_permission_is_required_on_lookup_and_preview(self):
        preview = self.fetch()
        before, states = self.snapshot(), self.states()
        for missing in self.view_permissions:
            self.restore_permissions()
            self.revoke(missing)
            for url in (self.lookup_url(), preview):
                with self.subTest(missing=missing, url=url):
                    self.assertEqual(self.client.get(url).status_code, 403)
                    self.assertEqual(self.snapshot(), before)
                    self.assertEqual(self.states(), states)

    def test_each_fetch_permission_is_required_before_provider_or_state_write(self):
        before, states = self.snapshot(), self.states()
        for missing in (*self.import_permissions, "add_resource"):
            with self.subTest(missing=missing):
                self.restore_permissions()
                self.revoke(missing)
                response = self.client.post(self.lookup_url(), {"action": "fetch", "doi": "10.1234/matrix-new"})
                self.assertEqual(response.status_code, 403)
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.states(), states)
        self.provider.assert_not_called()

    def test_existing_doi_import_needs_no_resource_add_or_change_permission(self):
        self.grant(*self.import_permissions)
        books = list(Resource.objects.order_by("pk").values())
        preview = self.fetch(self.resource.doi, event=self.empty)
        self.assertContains(self.client.get(preview), "Shared matrix reading")
        self.assertEqual(self.client.post(preview, self.review_data()).status_code, 302)
        self.assertTrue(EventResource.objects.filter(event=self.empty, resource=self.resource).exists())
        self.assertEqual(list(Resource.objects.order_by("pk").values()), books)
        self.provider.assert_not_called()

    def test_new_doi_preview_with_exact_permissions_is_not_business_creation(self):
        self.grant(*self.import_permissions, "add_resource")
        before = self.snapshot()
        preview = self.fetch()
        self.assertEqual(self.client.get(preview).status_code, 200)
        self.assertEqual(self.snapshot(), before)
        self.provider.assert_called_once_with("10.1234/matrix-new")

    def test_each_permission_revoked_after_preview_blocks_review_and_confirmation(self):
        preview = self.fetch()
        before, states = self.snapshot(), self.states()
        for missing in (*self.import_permissions, "add_resource"):
            self.restore_permissions()
            self.revoke(missing)
            for action in ("review", "save"):
                with self.subTest(missing=missing, action=action):
                    self.assertEqual(self.client.post(preview, self.review_data(action)).status_code, 403)
                    self.assertEqual(self.snapshot(), before)
                    self.assertEqual(self.states(), states)
        self.assertEqual(self.provider.call_count, 1)

    def test_view_only_can_read_preview_but_cannot_check_save_or_cancel(self):
        preview = self.fetch()
        self.grant(*self.view_permissions)
        before, states = self.snapshot(), self.states()
        self.assertEqual(self.client.get(self.lookup_url()).status_code, 200)
        self.assertEqual(self.client.get(preview).status_code, 200)
        for action in ("review", "save", "cancel"):
            self.assertEqual(self.client.post(preview, self.review_data(action)).status_code, 403)
            self.assertEqual(self.snapshot(), before)
            self.assertEqual(self.states(), states)

    def test_cancel_requires_import_permissions_but_not_resource_creation(self):
        preview = self.fetch()
        before, states = self.snapshot(), self.states()
        for missing in self.import_permissions:
            self.restore_permissions()
            self.revoke(missing)
            self.assertEqual(self.client.post(preview, {"action": "cancel"}).status_code, 403)
            self.assertEqual(self.snapshot(), before)
            self.assertEqual(self.states(), states)
        self.grant(*self.import_permissions)
        self.assertEqual(self.client.post(preview, {"action": "cancel"}).status_code, 302)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(next(iter(self.states().values()))["status"], "cancelled")

    def test_saved_confirmation_replay_still_checks_each_current_import_permission(self):
        preview = self.fetch(self.resource.doi, event=self.empty)
        self.assertEqual(self.client.post(preview, self.review_data()).status_code, 302)
        before, states = self.snapshot(), self.states()
        for missing in self.import_permissions:
            self.restore_permissions()
            self.revoke(missing)
            self.assertEqual(self.client.post(preview, self.review_data()).status_code, 403)
            self.assertEqual(self.snapshot(), before)
            self.assertEqual(self.states(), states)

    def test_resource_add_revoked_after_view_check_is_rechecked_in_final_transaction(self):
        preview = self.fetch()
        before, states = self.snapshot(), self.states()

        def revoke_before_transaction(request, *args):
            # The view already cached an allowed permission set for this request.
            self.revoke("add_resource")
            return confirm_preview(request, *args)

        with patch("events.doi_admin.confirm_preview", side_effect=revoke_before_transaction):
            self.assertEqual(self.client.post(preview, self.review_data()).status_code, 403)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.states(), states)

    def test_shared_edit_requires_resource_change_without_event_permissions(self):
        url = self.url("resource", "change", self.resource)
        self.assertEqual(self.client.get(url).status_code, 200)
        self.revoke("change_resource")
        before = self.snapshot()
        self.assertEqual(self.client.post(url, self.book_data()).status_code, 403)
        self.assertEqual(self.snapshot(), before)
        self.grant("change_resource")
        self.assertEqual(self.client.post(url, self.book_data()).status_code, 302)
        self.resource.refresh_from_db()
        self.assertEqual((self.resource.doi, self.resource.metadata_source, self.resource.seed_key), ("10.1234/matrix-saved", "crossref", "matrix-book"))
        for event in (self.event, self.other):
            readings = Client().get(reverse("events:event-detail", args=[event.pk])).json()["resources"]
            shared = next(row for row in readings if row["resource_id"] == self.resource.pk)
            self.assertEqual(shared["title"], "Edited matrix book")

    def test_reason_and_order_edit_requires_only_association_change(self):
        url = self.url("eventresource", "change", self.link)
        self.assertEqual(self.client.get(url).status_code, 200)
        self.revoke("change_eventresource")
        before = self.snapshot()
        self.assertEqual(self.client.post(url, self.link_data()).status_code, 403)
        self.assertEqual(self.snapshot(), before)
        self.grant("change_eventresource")
        self.assertEqual(self.client.post(url, self.link_data()).status_code, 302)
        self.link.refresh_from_db()
        self.assertEqual((self.link.event_id, self.link.resource_id, self.link.recommendation, self.link.display_order), (self.event.pk, self.resource.pk, "New reason", -9))
        self.other_link.refresh_from_db()
        self.assertEqual((self.other_link.recommendation, self.other_link.display_order), ("Reason B", 8))

    def test_removal_requires_only_association_delete_permission(self):
        self.revoke("delete_eventresource")
        before = self.snapshot()
        url = self.url("eventresource", "delete", self.link)
        self.assertNotContains(self.client.get(self.url("eventresource", "change", self.link)), "Remove from this talk")
        self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.post(url, {"post": "yes"}).status_code, 403)
        self.assertEqual(self.snapshot(), before)
        self.grant("delete_eventresource")
        self.assertEqual(self.client.post(url, {"post": "yes"}).status_code, 302)
        self.assertFalse(EventResource.objects.filter(pk=self.link.pk).exists())
        self.assertTrue(EventResource.objects.filter(pk=self.other_link.pk).exists())
        self.assertTrue(Resource.objects.filter(pk=self.resource.pk).exists())

    def test_each_single_event_delete_permission_required_even_without_links(self):
        before = self.snapshot()
        for missing in ("delete_event", "delete_eventresource"):
            self.restore_permissions()
            self.revoke(missing)
            for event in (self.event, self.empty):
                with self.subTest(missing=missing, event=event.pk):
                    url = self.url("event", "delete", event)
                    self.assertEqual(self.client.get(url).status_code, 403)
                    self.assertEqual(self.client.post(url, {"post": "yes"}).status_code, 403)
                    self.assertEqual(self.snapshot(), before)

    def test_each_bulk_event_delete_permission_removes_action_and_blocks_forged_post(self):
        before = self.snapshot()
        url = self.url("event", "changelist")
        for missing in ("delete_event", "delete_eventresource"):
            self.restore_permissions()
            self.revoke(missing)
            with self.subTest(missing=missing):
                self.assertNotContains(self.client.get(url), 'value="delete_selected"')
                for data in (self.batch_data(), {**self.batch_data(), "post": "yes"}):
                    self.assertEqual(self.client.post(url, data).status_code, 200)
                    self.assertEqual(self.snapshot(), before)

    def test_single_and_bulk_event_confirmation_recheck_both_permissions(self):
        before = self.snapshot()
        for missing in ("delete_event", "delete_eventresource"):
            self.restore_permissions()
            single = self.url("event", "delete", self.event)
            bulk = self.url("event", "changelist")
            self.assertContains(self.client.get(single), self.event_warning)
            self.assertContains(self.client.post(bulk, self.batch_data()), self.event_warning)
            self.revoke(missing)
            self.assertEqual(self.client.post(single, {"post": "yes"}).status_code, 403)
            self.assertEqual(self.client.post(bulk, {**self.batch_data(), "post": "yes"}).status_code, 200)
            self.assertEqual(self.snapshot(), before)

    def assert_resources_and_b_retained(self, books, other_links):
        self.assertEqual(list(Resource.objects.order_by("pk").values()), books)
        self.assertEqual(list(EventResource.objects.filter(event=self.other).values()), other_links)
        self.assertTrue(Event.objects.filter(pk=self.other.pk, title="Matrix talk B").exists())

    def test_single_event_requires_confirmation_then_retains_every_resource(self):
        self.grant("delete_event", "delete_eventresource")
        before = self.snapshot()
        url = self.url("event", "delete", self.event)
        self.assertContains(self.client.get(url), self.event_warning)
        self.assertContains(self.client.post(url, {}), self.event_warning)
        self.assertEqual(self.snapshot(), before)
        books, other_links = before[1], list(EventResource.objects.filter(event=self.other).values())
        self.assertEqual(self.client.post(url, {"post": "yes"}).status_code, 302)
        self.assertFalse(Event.objects.filter(pk=self.event.pk).exists())
        self.assertFalse(EventResource.objects.filter(event_id=self.event.pk).exists())
        self.assert_resources_and_b_retained(books, other_links)

    def test_bulk_event_requires_confirmation_then_retains_every_resource(self):
        self.grant("view_event", "delete_event", "delete_eventresource")
        before = self.snapshot()
        url = self.url("event", "changelist")
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertContains(self.client.post(url, self.batch_data()), self.event_warning)
        self.assertEqual(self.snapshot(), before)
        books, other_links = before[1], list(EventResource.objects.filter(event=self.other).values())
        self.assertEqual(self.client.post(url, {**self.batch_data(), "post": "yes"}).status_code, 302)
        self.assertEqual(list(Event.objects.values_list("pk", flat=True)), [self.other.pk])
        self.assert_resources_and_b_retained(books, other_links)

    def test_resource_delete_disabled_for_explicit_staff_and_superuser_all_paths(self):
        before = self.snapshot()
        resource_admin = admin.site.get_model_admin(Resource)
        for user in (self.staff, self.superuser):
            self.client.force_login(user)
            request = RequestFactory().post("/admin/")
            request.user = user
            self.assertFalse(resource_admin.has_delete_permission(request))
            self.assertEqual(resource_admin.get_actions(request), {})
            for book in (self.resource, self.exclusive, self.unlinked):
                with self.subTest(user=user.pk, book=book.pk):
                    self.assertNotContains(self.client.get(self.url("resource", "change", book)), 'class="deletelink"')
                    url = self.url("resource", "delete", book)
                    self.assertEqual(self.client.get(url).status_code, 403)
                    self.assertEqual(self.client.post(url, {"post": "yes"}).status_code, 403)
                    with self.assertRaises(PermissionDenied):
                        resource_admin.delete_model(request, book)
                    self.assertEqual(self.snapshot(), before)
            data = {"action": "delete_selected", ACTION_CHECKBOX_NAME: [self.resource.pk, self.exclusive.pk, self.unlinked.pk]}
            for submitted in (data, {**data, "post": "yes"}):
                response = self.client.post(self.url("resource", "changelist"), submitted)
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, 'name="post"')
                self.assertEqual(self.snapshot(), before)
            with self.assertRaises(PermissionDenied):
                resource_admin.delete_queryset(request, Resource.objects.all())

    def test_get_with_write_action_parameters_never_changes_business_or_preview(self):
        preview = self.fetch()
        before, states = self.snapshot(), self.states()
        for url, data in self.operations(preview):
            with self.subTest(url=url, action=data.get("action")):
                response = self.client.get(url, data)
                if url in (self.url("event", "changelist"), self.url("resource", "changelist")):
                    # Native changelists treat action GET parameters as invalid
                    # filters and redirect; they never execute a POST action.
                    self.assertRedirects(response, url + "?e=1")
                else:
                    self.assertIn(response.status_code, (200, 403))
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.states(), states)
        self.assertEqual(self.provider.call_count, 1)

    def test_real_csrf_rejects_untrusted_origin_even_with_a_valid_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.staff)
        client.get(self.lookup_url())
        token = client.cookies["csrftoken"].value
        preview = self.fetch(client=client, token=token)
        before, states = self.snapshot(), self.states(client)
        for url, data in self.operations(preview):
            with self.subTest(url=url, action=data.get("action")):
                response = client.post(
                    url, {**data, "csrfmiddlewaretoken": token}, HTTP_ORIGIN="https://untrusted.example.org",
                )
                self.assertEqual(response.status_code, 403)
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(self.states(client), states)

    def test_real_csrf_missing_and_forged_tokens_block_every_post_before_side_effects(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.staff)
        self.assertEqual(client.get(self.lookup_url()).status_code, 200)
        token = client.cookies["csrftoken"].value
        preview = self.fetch(client=client, token=token)
        before, states = self.snapshot(), self.states(client)
        for url, data in self.operations(preview):
            for csrf in ({}, {"csrfmiddlewaretoken": "a" * 64}):
                with self.subTest(url=url, action=data.get("action"), csrf=bool(csrf)):
                    self.assertEqual(client.post(url, {**data, **csrf}).status_code, 403)
                    self.assertEqual(self.snapshot(), before)
                    self.assertEqual(self.states(client), states)
        self.assertEqual(self.provider.call_count, 1)

    def test_valid_csrf_allows_authorized_create_edit_review_save_cancel_and_deletion(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.staff)
        client.get(self.lookup_url())
        token = client.cookies["csrftoken"].value

        def post(url, data, status=302):
            response = client.post(url, {**data, "csrfmiddlewaretoken": token})
            self.assertEqual(response.status_code, status)
            return response

        post(self.url("event", "add"), self.event_data())
        post(self.url("event", "change", self.event), self.event_data())
        post(self.url("resource", "add"), self.book_data())
        post(self.url("resource", "change", self.resource), self.book_data())
        post(self.url("eventresource", "add"), self.link_data())
        post(self.url("eventresource", "change", self.link), self.link_data())
        preview = self.fetch(client=client, token=token)
        post(preview, self.review_data("review"), 200)
        self.assertFalse(Resource.objects.filter(doi="10.1234/matrix-new").exists())
        post(preview, self.review_data())
        self.assertTrue(EventResource.objects.filter(event=self.event, resource__doi="10.1234/matrix-new").exists())
        cancelled = self.fetch(self.resource.doi, client=client, token=token)
        before = self.snapshot()
        post(cancelled, {"action": "cancel"})
        self.assertEqual(self.snapshot(), before)
        post(self.url("eventresource", "delete", self.link), {"post": "yes"})
        books = list(Resource.objects.order_by("pk").values())
        single = self.url("event", "delete", self.event)
        self.assertContains(client.get(single), self.event_warning)
        post(single, {"post": "yes"})
        bulk = self.url("event", "changelist")
        selection = {"action": "delete_selected", ACTION_CHECKBOX_NAME: [self.empty.pk]}
        self.assertContains(post(bulk, selection, 200), self.event_warning)
        post(bulk, {**selection, "post": "yes"})
        self.assertEqual(list(Resource.objects.order_by("pk").values()), books)
        self.assertTrue(EventResource.objects.filter(pk=self.other_link.pk).exists())
