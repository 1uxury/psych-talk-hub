"""Step 27: native Admin removal preserves shared bibliography and other talks."""

from unittest.mock import patch

from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape

from events.models import Event, EventResource, Resource


class AdminReadingRemovalTests(TestCase):
    confirmation = "Remove this reading from this talk? Other talks will keep it."

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser("removal-admin", password="test-only")
        cls.event_a = Event.objects.create(title='Talk A <script> & "target"', starts_at=timezone.now())
        cls.event_b = Event.objects.create(title="Talk B", starts_at=timezone.now())
        cls.shared = Resource.objects.create(
            title='Shared reading <script> & "target"', authors="Fixture Author", year=2020,
            original_url="https://example.org/shared", doi="10.1234/removal",
            metadata_source="crossref", seed_key="removal-fixture",
        )
        cls.other = Resource.objects.create(title="Other reading", original_url="https://example.org/other")
        cls.link_a = EventResource.objects.create(
            event=cls.event_a, resource=cls.shared, recommendation="Reason A", display_order=-3,
        )
        cls.other_a = EventResource.objects.create(event=cls.event_a, resource=cls.other)
        cls.link_b = EventResource.objects.create(
            event=cls.event_b, resource=cls.shared, recommendation="Reason B", display_order=8,
        )

    def setUp(self):
        self.client.force_login(self.user)
        self.visitor = Client()
        network = patch("requests.sessions.Session.request", side_effect=AssertionError("No HTTP"))
        self.network = network.start()
        self.addCleanup(network.stop)
        self.addCleanup(self.network.assert_not_called)

    def url(self, action, link=None):
        return reverse(f"admin:events_eventresource_{action}", args=[link.pk] if link else None)

    def snapshot(self):
        return [list(model.objects.order_by("pk").values()) for model in (Event, Resource, EventResource)]

    def detail(self, event):
        response = self.visitor.get(reverse("events:event-detail", args=[event.pk]))
        self.assertEqual(response.status_code, 200)
        return response.json()

    def staff(self, *permissions, is_staff=True):
        user = get_user_model().objects.create_user(
            f"removal-staff-{get_user_model().objects.count()}", is_staff=is_staff,
        )
        user.user_permissions.set(Permission.objects.filter(
            content_type__app_label="events", codename__in=permissions,
        ))
        self.client.force_login(user)
        return user

    def assert_only_link_removed(self, before, link):
        expected = [before[0], before[1], [row for row in before[2] if row["id"] != link.pk]]
        self.assertEqual(self.snapshot(), expected)

    def test_native_remove_entry_and_save_controls_preserve_event_filter(self):
        before = self.snapshot()
        query = f"?_changelist_filters=event__id__exact%3D{self.event_a.pk}"
        page = self.client.get(self.url("change", self.link_a) + query)
        self.assertTemplateUsed(page, "admin/events/eventresource/submit_line.html")
        self.assertContains(page, "Remove from this talk", count=1)
        self.assertContains(page, self.url("delete", self.link_a) + query)
        self.assertNotContains(page, '>Delete</a>')
        for name in ("_save", "_continue", "csrfmiddlewaretoken"):
            self.assertContains(page, f'name="{name}"')
        self.assertNotContains(self.client.get(self.url("add")), "Remove from this talk")
        self.assertEqual(self.snapshot(), before)

    def test_confirmation_target_is_escaped_and_cancel_does_not_write(self):
        before = self.snapshot()
        url = self.url("delete", self.link_a)
        for page in (self.client.get(url), self.client.post(url, {})):
            self.assertContains(page, self.confirmation, count=1)
            self.assertContains(page, f'Talk: <strong>{escape(self.event_a.title)}</strong>')
            self.assertContains(page, f'Reading: <strong>{escape(self.shared.title)}</strong>')
            self.assertNotContains(page, "<script> &")
            self.assertContains(page, 'class="button cancel-link"')
            self.assertContains(page, 'name="csrfmiddlewaretoken"')
            self.assertEqual(dict(page.context["model_count"]), {"event resources": 1})
            self.assertEqual(self.snapshot(), before)
        # Native cancel.js navigates back without submitting the confirmation.
        self.assertEqual(self.client.get(self.url("change", self.link_a)).status_code, 200)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(LogEntry.objects.filter(action_flag=DELETION).exists())

    def test_confirm_removes_only_current_link_and_updates_anonymous_counts(self):
        before, other_talk = self.snapshot(), self.detail(self.event_b)
        response = self.client.post(self.url("delete", self.link_a), {"post": "yes"})
        self.assertRedirects(response, self.url("changelist"))
        self.assert_only_link_removed(before, self.link_a)
        current = self.detail(self.event_a)
        self.assertEqual(current["resource_count"], 1)
        self.assertEqual([row["association_id"] for row in current["resources"]], [self.other_a.pk])
        self.assertEqual(self.detail(self.event_b), other_talk)
        counts = {row["id"]: row["resource_count"] for row in self.visitor.get("/api/events/").json()}
        self.assertEqual(counts, {self.event_a.pk: 1, self.event_b.pk: 1})
        log = LogEntry.objects.get(action_flag=DELETION)
        self.assertEqual(log.object_id, str(self.link_a.pk))
        self.assertEqual(log.content_type.model, "eventresource")

    def test_removing_last_reference_keeps_unlinked_resource_and_empty_talk(self):
        before = self.snapshot()
        response = self.client.post(self.url("delete", self.other_a), {"post": "yes"})
        self.assertEqual(response.status_code, 302)
        self.assert_only_link_removed(before, self.other_a)
        self.assertTrue(Resource.objects.filter(pk=self.other.pk).exists())
        self.client.post(self.url("delete", self.link_b), {"post": "yes"})
        empty = self.detail(self.event_b)
        self.assertEqual((empty["resource_count"], empty["resources"]), (0, []))
        self.assertTrue(Event.objects.filter(pk=self.event_b.pk).exists())
        self.assertEqual(list(Resource.objects.order_by("pk").values()), before[1])

    def test_posted_identities_cannot_retarget_the_link_in_the_url(self):
        before = self.snapshot()
        response = self.client.post(self.url("delete", self.link_a), {
            "post": "yes", "event": self.event_b.pk, "resource": self.other.pk,
            "association_id": self.link_b.pk, "_selected_action": self.link_b.pk,
        })
        self.assertEqual(response.status_code, 302)
        self.assert_only_link_removed(before, self.link_a)

    def test_unauthorised_removal_is_rejected_and_no_public_delete_is_added(self):
        before = self.snapshot()
        url = self.url("delete", self.link_a)
        self.client.logout()
        for method in ("get", "post"):
            self.assertEqual(getattr(self.client, method)(url, {"post": "yes"}).status_code, 302)
        self.staff("delete_eventresource", is_staff=False)
        self.assertEqual(self.client.post(url, {"post": "yes"}).status_code, 302)
        self.client.logout()
        self.staff("view_eventresource", "change_eventresource")
        self.assertNotContains(self.client.get(self.url("change", self.link_a)), "Remove from this talk")
        self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.post(url, {"post": "yes"}).status_code, 403)
        for client in (self.client, self.visitor):
            self.assertEqual(client.delete(f"/api/events/{self.event_a.pk}/").status_code, 405)
            self.assertEqual(client.post(f"/api/events/{self.event_a.pk}/remove/", {"association_id": self.link_a.pk}).status_code, 404)
        self.assertEqual(self.snapshot(), before)

    def test_delete_permission_is_sufficient_and_rechecked_after_confirmation_get(self):
        user = self.staff("view_eventresource", "delete_eventresource")
        before = self.snapshot()
        self.assertContains(self.client.get(self.url("change", self.link_a)), "Remove from this talk")
        self.assertContains(self.client.get(self.url("delete", self.link_a)), self.confirmation)
        user.user_permissions.remove(Permission.objects.get(
            content_type__app_label="events", codename="delete_eventresource",
        ))
        self.assertEqual(self.client.post(self.url("delete", self.link_a), {"post": "yes"}).status_code, 403)
        self.assertEqual(self.snapshot(), before)
        user.user_permissions.add(Permission.objects.get(
            content_type__app_label="events", codename="delete_eventresource",
        ))
        self.assertEqual(self.client.post(self.url("delete", self.link_a), {"post": "yes"}).status_code, 302)
        self.assert_only_link_removed(before, self.link_a)

    def test_removal_uses_real_csrf_and_preserves_records_on_rejected_posts(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        url, before = self.url("delete", self.link_a), self.snapshot()
        self.assertEqual(client.get(url).status_code, 200)
        token = client.cookies["csrftoken"].value
        for extra in ({}, {"csrfmiddlewaretoken": "a" * 64}):
            self.assertEqual(client.post(url, {"post": "yes", **extra}).status_code, 403)
            self.assertEqual(self.snapshot(), before)
        self.assertEqual(client.post(url, {"post": "yes", "csrfmiddlewaretoken": token}).status_code, 302)
        self.assert_only_link_removed(before, self.link_a)

    def test_repeated_confirmation_cannot_remove_another_link(self):
        url = self.url("delete", self.link_a)
        self.assertEqual(self.client.post(url, {"post": "yes"}).status_code, 302)
        before = self.snapshot()
        self.assertEqual(self.client.get(url).status_code, 302)
        self.assertEqual(self.client.post(url, {"post": "yes"}).status_code, 302)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(LogEntry.objects.filter(action_flag=DELETION).count(), 1)

    def test_removed_admin_link_cannot_be_recreated_by_old_doi_confirmation(self):
        lookup = reverse("admin:events_event_doi_lookup", args=[self.event_a.pk])
        preview = self.client.post(lookup, {"action": "fetch", "doi": self.shared.doi})
        self.assertEqual(preview.status_code, 302)
        self.assertEqual(self.client.post(preview.url, {
            "action": "save", "recommendation": "Ignored duplicate", "display_order": 0,
        }).status_code, 302)
        self.assertEqual(self.client.post(self.url("delete", self.link_a), {"post": "yes"}).status_code, 302)
        before = self.snapshot()
        self.assertContains(self.client.post(preview.url, {"action": "save"}),
                            "This preview is no longer valid. Fetch metadata again.", status_code=400)
        self.assertEqual(self.snapshot(), before)
