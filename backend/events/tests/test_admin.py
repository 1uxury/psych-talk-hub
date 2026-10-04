"""Step 08: real Admin requests, London forms and safe deletion."""

from datetime import datetime, timezone as datetime_timezone
from unittest.mock import patch

from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.messages import get_messages
from django.core.exceptions import PermissionDenied
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from events.models import Event, EventResource, Resource


class AdminManagementTests(TestCase):
    event_confirmation = "Delete this talk and its reading links? Shared resources will be kept."

    @classmethod
    def setUpTestData(cls):
        cls.admin_user = get_user_model().objects.create_superuser(
            username="admin-test", email="admin@example.org", password="test-only-password"
        )
        cls.event = Event.objects.create(
            title="Test talk", starts_at=datetime(2026, 12, 1, 18, tzinfo=datetime_timezone.utc)
        )
        cls.other_event = Event.objects.create(
            title="Other test talk", starts_at=cls.event.starts_at
        )
        cls.resource = Resource.objects.create(
            title="Test reading", original_url="https://example.org/reading"
        )
        cls.unlinked_resource = Resource.objects.create(
            title="Unlinked reading", original_url="https://example.org/unlinked"
        )
        cls.link = EventResource.objects.create(event=cls.event, resource=cls.resource)
        cls.other_link = EventResource.objects.create(event=cls.other_event, resource=cls.resource)

    def setUp(self):
        self.client.force_login(self.admin_user)

    def url(self, model, action, obj=None):
        args = [obj.pk] if obj is not None else None
        return reverse(f"admin:events_{model}_{action}", args=args)

    def event_data(self, **overrides):
        data = {
            "title": "Added talk", "description": "", "topic": "",
            "starts_at_0": "2026-07-01", "starts_at_1": "16:00:00",
            "speaker": "", "_save": "Save",
        }
        return {**data, **overrides}

    def resource_data(self, **overrides):
        data = {
            "title": "Manual reading", "authors": "", "year": "",
            "original_url": "https://example.org/manual", "resource_type": "article",
            "_save": "Save",
        }
        return {**data, **overrides}

    def staff_with(self, *codenames):
        user = get_user_model().objects.create_user(username="staff-test", is_staff=True)
        for codename in codenames:
            user.user_permissions.add(Permission.objects.get(
                content_type__app_label="events", codename=codename
            ))
        self.client.force_login(user)
        return user

    def assert_original_records_exist(self):
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(Resource.objects.count(), 2)
        self.assertEqual(EventResource.objects.count(), 2)

    def test_models_are_registered_and_management_pages_render(self):
        for model in (Event, Resource, EventResource):
            with self.subTest(model=model.__name__):
                self.assertTrue(admin.site.is_registered(model))
                self.assertEqual(self.client.get(self.url(model._meta.model_name, "changelist")).status_code, 200)
                self.assertEqual(self.client.get(self.url(model._meta.model_name, "add")).status_code, 200)

    def test_create_event_has_public_address_in_save_message_and_edit_page(self):
        with patch("requests.sessions.Session.request") as network:
            response = self.client.post(self.url("event", "add"), self.event_data())
        self.assertEqual(response.status_code, 302)
        event = Event.objects.get(title="Added talk")
        self.assertFalse(event.is_example)
        self.assertIsNone(event.seed_key)
        address = f"/events/{event.pk}"
        messages = " ".join(str(message) for message in get_messages(response.wsgi_request))
        self.assertIn(f'href="{address}"', messages)
        page = self.client.get(self.url("event", "change", event))
        self.assertContains(page, f'href="{address}"')
        self.assertContains(page, "View public talk")
        network.assert_not_called()
        # Only the address is verified: the public React route is not implemented.

    def test_edit_event_preserves_identifier_and_offers_public_address(self):
        response = self.client.post(self.url("event", "change", self.event), self.event_data(
            title="Edited talk", topic="Memory", description="Reading before the talk", speaker="Speaker"
        ))
        self.assertEqual(response.status_code, 302)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Edited talk")
        self.assertEqual(self.event.topic, "Memory")
        self.assertEqual(self.event.speaker, "Speaker")
        self.assertEqual(self.event.description, "Reading before the talk")
        self.assertIn(f"/events/{self.event.pk}", " ".join(
            str(message) for message in get_messages(response.wsgi_request)
        ))

    def test_london_form_label_winter_summer_storage_and_display(self):
        add_url = self.url("event", "add")
        for month, expected_hour in ((1, 16), (7, 15)):
            with self.subTest(month=month), timezone.override("UTC"):
                page = self.client.get(add_url)
                self.assertContains(page, "Start time (Europe/London)")
                self.assertContains(page, "GMT in winter, BST in summer")
                response = self.client.post(add_url, self.event_data(
                    title=f"London {month}", starts_at_0=f"2026-{month:02d}-01"
                ))
                self.assertEqual(response.status_code, 302)
                event = Event.objects.get(title=f"London {month}")
                self.assertEqual(event.starts_at, datetime(
                    2026, month, 1, expected_hour, tzinfo=datetime_timezone.utc
                ))
                edit = self.client.get(self.url("event", "change", event))
                self.assertContains(edit, 'value="16:00:00"')

    def test_invalid_event_and_dst_times_show_field_errors_without_saving(self):
        for data, field in (
            (self.event_data(title="   "), "title"),
            (self.event_data(starts_at_0=""), "starts_at"),
            (self.event_data(starts_at_0="2026-03-29", starts_at_1="01:30:00"), "starts_at"),
            (self.event_data(starts_at_0="2026-10-25", starts_at_1="01:30:00"), "starts_at"),
        ):
            with self.subTest(data=data), timezone.override("UTC"):
                response = self.client.post(self.url("event", "add"), data)
                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context["adminform"].form.errors)
                self.assert_original_records_exist()

    def test_manual_creation_preserves_optional_nulls_and_ignores_forged_metadata(self):
        with patch("requests.sessions.Session.request") as network:
            response = self.client.post(self.url("resource", "add"), self.resource_data(
                metadata_source="crossref", doi="10.1234/forged", seed_key="forged"
            ))
        self.assertEqual(response.status_code, 302)
        resource = Resource.objects.get(title="Manual reading")
        self.assertEqual(resource.authors, "")
        self.assertIsNone(resource.year)
        self.assertIsNone(resource.doi)
        self.assertIsNone(resource.seed_key)
        self.assertEqual(resource.metadata_source, "manual")
        network.assert_not_called()

    def test_manual_same_title_or_url_creates_independent_records(self):
        for _ in range(2):
            response = self.client.post(self.url("resource", "add"), self.resource_data(
                resource_type="research_paper", authors="Test Author", year="2020"
            ))
            self.assertEqual(response.status_code, 302)
        resources = Resource.objects.filter(title="Manual reading")
        self.assertEqual(resources.count(), 2)
        self.assertEqual(resources.filter(resource_type="research_paper", year=2020).count(), 2)

    def test_invalid_manual_resource_has_field_errors_and_no_write(self):
        for overrides, field in (
            ({"title": ""}, "title"), ({"original_url": "ftp://example.org/file"}, "original_url"),
            ({"year": "10000"}, "year"), ({"resource_type": "unknown"}, "resource_type"),
        ):
            with self.subTest(field=field):
                response = self.client.post(self.url("resource", "add"), self.resource_data(**overrides))
                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context["adminform"].form.errors)
                self.assert_original_records_exist()

    def test_select_existing_resource_reuses_book_and_rejects_duplicate_link(self):
        data = {
            "event": self.event.pk, "resource": self.unlinked_resource.pk,
            "recommendation": "Read before the talk", "display_order": "-2", "_save": "Save",
        }
        response = self.client.post(self.url("eventresource", "add"), data)
        self.assertEqual(response.status_code, 302)
        link = EventResource.objects.get(event=self.event, resource=self.unlinked_resource)
        self.assertEqual(link.recommendation, "Read before the talk")
        self.assertEqual(link.display_order, -2)
        self.assertEqual(Resource.objects.count(), 2)
        response = self.client.post(self.url("eventresource", "add"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["adminform"].form.non_field_errors())
        self.assertEqual(EventResource.objects.count(), 3)

    def test_invalid_link_fields_are_rejected_without_writing(self):
        data = {"event": self.event.pk, "resource": self.unlinked_resource.pk, "display_order": "0"}
        for overrides, field in (
            ({"event": ""}, "event"), ({"resource": "999999999"}, "resource"),
            ({"display_order": "not-an-integer"}, "display_order"),
        ):
            with self.subTest(field=field):
                response = self.client.post(self.url("eventresource", "add"), {**data, **overrides})
                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context["adminform"].form.errors)
                self.assert_original_records_exist()

    def test_shared_resource_edit_preserves_readonly_doi_and_source(self):
        self.resource.doi = "10.1234/test-fixture"
        self.resource.metadata_source = "crossref"
        self.resource.save()
        response = self.client.post(self.url("resource", "change", self.resource), self.resource_data(
            title="Edited shared reading", metadata_source="manual", doi="10.1234/forged"
        ))
        self.assertEqual(response.status_code, 302)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.title, "Edited shared reading")
        self.assertEqual(self.resource.doi, "10.1234/test-fixture")
        self.assertEqual(self.resource.metadata_source, "crossref")
        self.link.refresh_from_db()
        self.other_link.refresh_from_db()
        self.assertEqual(self.link.resource.title, "Edited shared reading")
        self.assertEqual(self.other_link.resource.title, "Edited shared reading")
        self.assertEqual(EventResource.objects.count(), 2)

    def test_link_context_edits_cannot_move_identity_or_change_other_talk(self):
        response = self.client.post(self.url("eventresource", "change", self.link), {
            "event": self.other_event.pk, "resource": self.unlinked_resource.pk,
            "recommendation": "Changed reason", "display_order": "-3", "_save": "Save",
        })
        self.assertEqual(response.status_code, 302)
        self.link.refresh_from_db()
        self.other_link.refresh_from_db()
        self.assertEqual(self.link.event_id, self.event.pk)
        self.assertEqual(self.link.resource_id, self.resource.pk)
        self.assertEqual(self.link.recommendation, "Changed reason")
        self.assertEqual(self.link.display_order, -3)
        self.assertEqual(self.other_link.recommendation, "")
        self.assertEqual(self.other_link.display_order, 0)

    def test_anonymous_and_nonstaff_cannot_read_or_write_management(self):
        nonstaff = get_user_model().objects.create_user(username="nonstaff-test")
        for user in (None, nonstaff):
            self.client.logout()
            if user:
                self.client.force_login(user)
            for model, obj, data in (
                ("event", self.event, self.event_data()),
                ("resource", self.resource, self.resource_data()),
                ("eventresource", self.link, {"recommendation": "forged", "display_order": 0}),
            ):
                for action in ("add", "change", "delete"):
                    with self.subTest(user=user, model=model, action=action):
                        url = self.url(model, action, None if action == "add" else obj)
                        for response in (self.client.get(url), self.client.post(url, data)):
                            self.assertEqual(response.status_code, 302)
                            self.assertIn("/admin/login/", response["Location"])
        self.assert_original_records_exist()

    def test_staff_permissions_are_required_for_management_and_link_creation(self):
        user = self.staff_with("add_eventresource", "view_resource")
        self.assertEqual(self.client.post(self.url("event", "add"), self.event_data()).status_code, 403)
        self.assertEqual(self.client.post(self.url("resource", "add"), self.resource_data()).status_code, 403)
        data = {"event": self.event.pk, "resource": self.unlinked_resource.pk, "display_order": 0}
        self.assertEqual(self.client.post(self.url("eventresource", "add"), data).status_code, 403)
        user.user_permissions.add(Permission.objects.get(
            content_type__app_label="events", codename="change_event"
        ))
        self.assertEqual(self.client.post(self.url("eventresource", "add"), data).status_code, 302)
        self.assertEqual(Resource.objects.count(), 2)

    def test_single_event_delete_requires_confirmation_and_preserves_all_resources(self):
        exclusive = Resource.objects.create(title="Exclusive reading", original_url="https://example.org/exclusive")
        EventResource.objects.create(event=self.event, resource=exclusive)
        url = self.url("event", "delete", self.event)
        response = self.client.get(url)
        self.assertContains(response, self.event_confirmation)
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertTrue(Event.objects.filter(pk=self.event.pk).exists())
        self.assertEqual(EventResource.objects.count(), 3)
        self.assertEqual(self.client.post(url, {"post": "yes"}).status_code, 302)
        self.assertFalse(Event.objects.filter(pk=self.event.pk).exists())
        self.assertEqual(EventResource.objects.count(), 1)
        self.assertTrue(EventResource.objects.filter(pk=self.other_link.pk).exists())
        self.assertEqual(Resource.objects.count(), 3)

    def test_bulk_event_delete_confirms_then_preserves_resources(self):
        third = Event.objects.create(title="Third talk", starts_at=self.event.starts_at)
        EventResource.objects.create(event=third, resource=self.resource)
        url = self.url("event", "changelist")
        data = {"action": "delete_selected", ACTION_CHECKBOX_NAME: [self.event.pk, third.pk]}
        response = self.client.post(url, data)
        self.assertContains(response, self.event_confirmation)
        self.assertEqual(Event.objects.count(), 3)
        self.assertEqual(EventResource.objects.count(), 3)
        self.assertEqual(self.client.post(url, {**data, "post": "yes"}).status_code, 302)
        self.assertEqual(list(Event.objects.values_list("pk", flat=True)), [self.other_event.pk])
        self.assertEqual(list(EventResource.objects.values_list("pk", flat=True)), [self.other_link.pk])
        self.assertEqual(Resource.objects.count(), 2)

    def test_event_delete_needs_both_model_permissions_even_when_no_links(self):
        user = self.staff_with("view_event", "delete_event")
        empty = Event.objects.create(title="No readings", starts_at=self.event.starts_at)
        for event in (self.event, empty):
            url = self.url("event", "delete", event)
            self.assertEqual(self.client.get(url).status_code, 403)
            self.assertEqual(self.client.post(url, {"post": "yes"}).status_code, 403)
        request = RequestFactory().get("/admin/")
        request.user = user
        self.assertNotIn("delete_selected", admin.site.get_model_admin(Event).get_actions(request))
        user.user_permissions.add(Permission.objects.get(
            content_type__app_label="events", codename="delete_eventresource"
        ))
        url = self.url("event", "delete", empty)
        self.assertContains(self.client.get(url), self.event_confirmation)
        self.assertEqual(self.client.post(url, {"post": "yes"}).status_code, 302)

    def test_resource_single_direct_and_forged_bulk_deletion_are_blocked_for_superuser(self):
        resource_admin = admin.site.get_model_admin(Resource)
        request = RequestFactory().post("/admin/")
        request.user = self.admin_user
        self.assertFalse(resource_admin.has_delete_permission(request))
        self.assertEqual(resource_admin.get_actions(request), {})
        for resource in (self.resource, self.unlinked_resource):
            with self.subTest(resource=resource.title):
                change = self.client.get(self.url("resource", "change", resource))
                self.assertNotContains(change, 'class="deletelink"')
                url = self.url("resource", "delete", resource)
                self.assertEqual(self.client.get(url).status_code, 403)
                self.assertEqual(self.client.post(url, {"post": "yes"}).status_code, 403)
                with self.assertRaises(PermissionDenied):
                    resource_admin.delete_model(request, resource)
        self.client.post(self.url("resource", "changelist"), {
            "action": "delete_selected", ACTION_CHECKBOX_NAME: [self.resource.pk, self.unlinked_resource.pk],
            "post": "yes",
        })
        with self.assertRaises(PermissionDenied):
            resource_admin.delete_queryset(request, Resource.objects.all())
        self.assert_original_records_exist()

    def test_resource_deletion_also_denies_staff_with_explicit_delete_permission(self):
        self.staff_with("view_resource", "change_resource", "delete_resource")
        for resource in (self.resource, self.unlinked_resource):
            url = self.url("resource", "delete", resource)
            self.assertEqual(self.client.get(url).status_code, 403)
            self.assertEqual(self.client.post(url, {"post": "yes"}).status_code, 403)
        self.client.post(self.url("resource", "changelist"), {
            "action": "delete_selected", ACTION_CHECKBOX_NAME: [self.unlinked_resource.pk], "post": "yes",
        })
        self.assert_original_records_exist()

    def test_remove_link_confirmation_preserves_shared_resource_and_other_talk(self):
        url = self.url("eventresource", "delete", self.link)
        response = self.client.get(url)
        self.assertContains(response, "Remove this reading from this talk? Other talks will keep it.")
        self.assert_original_records_exist()
        self.assertEqual(self.client.post(url, {"post": "yes"}).status_code, 302)
        self.assertFalse(EventResource.objects.filter(pk=self.link.pk).exists())
        self.assertTrue(EventResource.objects.filter(pk=self.other_link.pk).exists())
        self.assertEqual(Resource.objects.count(), 2)
        self.assertEqual(Event.objects.count(), 2)

    def test_real_csrf_rejects_missing_and_forged_tokens_and_allows_valid_confirmation(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin_user)
        delete_url = self.url("event", "delete", self.event)
        self.assertEqual(client.get(delete_url).status_code, 200)
        token = client.cookies["csrftoken"].value
        for supplied in (None, "a" * 64):
            for url, data in (
                (self.url("event", "add"), self.event_data()),
                (self.url("resource", "add"), self.resource_data()),
                (self.url("eventresource", "add"), {"event": self.event.pk, "resource": self.unlinked_resource.pk, "display_order": 0}),
                (delete_url, {"post": "yes"}),
                (self.url("event", "changelist"), {"action": "delete_selected", ACTION_CHECKBOX_NAME: [self.event.pk], "post": "yes"}),
            ):
                with self.subTest(url=url, token=supplied):
                    data = {**data, **({"csrfmiddlewaretoken": supplied} if supplied else {})}
                    self.assertEqual(client.post(url, data).status_code, 403)
        self.assert_original_records_exist()
        response = client.post(delete_url, {"post": "yes", "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Resource.objects.count(), 2)
        self.assertEqual(EventResource.objects.count(), 1)
