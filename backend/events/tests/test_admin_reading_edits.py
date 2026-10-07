"""Step 26: native Admin edits followed by fresh anonymous API reads."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from events.models import Event, EventResource, Resource


class AdminReadingEditTests(TestCase):
    warning = "Changes to this resource will appear in every talk that uses it."

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            "reading-edit-test", password="test-only-password"
        )
        cls.event_a = Event.objects.create(title="Fixture talk A", starts_at=timezone.now())
        cls.event_b = Event.objects.create(title="Fixture talk B", starts_at=timezone.now())
        # Resource IDs deliberately oppose association IDs for tie-order checks.
        cls.other = Resource.objects.create(
            title="Other fixture reading", original_url="https://example.org/other"
        )
        cls.shared = Resource.objects.create(
            title="Shared fixture reading", authors="Fixture Author", year=2020,
            original_url="https://example.org/shared", doi="10.1234/edit-fixture",
            metadata_source="crossref", resource_type="research_paper", seed_key="edit-fixture",
        )
        cls.link_a = EventResource.objects.create(
            event=cls.event_a, resource=cls.shared, recommendation="Reason A"
        )
        cls.other_a = EventResource.objects.create(event=cls.event_a, resource=cls.other)
        cls.link_b = EventResource.objects.create(
            event=cls.event_b, resource=cls.shared, recommendation="Reason B", display_order=7
        )
        cls.other_b = EventResource.objects.create(event=cls.event_b, resource=cls.other)

    def setUp(self):
        self.client.force_login(self.user)
        self.visitor = Client()
        network = patch("requests.sessions.Session.request", side_effect=AssertionError("No HTTP"))
        self.network = network.start()
        self.addCleanup(network.stop)
        self.addCleanup(self.network.assert_not_called)

    def url(self, model, action, obj=None):
        return reverse(f"admin:events_{model}_{action}", args=[obj.pk] if obj else None)

    def detail(self, event):
        response = self.visitor.get(f"/api/events/{event.pk}/")
        self.assertEqual(response.status_code, 200)
        return response.json()

    def snapshot(self):
        return [list(model.objects.order_by("pk").values()) for model in (Event, Resource, EventResource)]

    def resource_data(self, **changes):
        return {
            "title": self.shared.title, "authors": self.shared.authors,
            "year": self.shared.year or "", "original_url": self.shared.original_url,
            "resource_type": self.shared.resource_type, "_save": "Save", **changes,
        }

    def edit_link(self, link, **changes):
        response = self.client.post(self.url("eventresource", "change", link), {
            "recommendation": link.recommendation, "display_order": link.display_order,
            "_save": "Save", **changes,
        })
        self.assertEqual(response.status_code, 302)

    def test_edit_warning_precedes_fields_and_get_does_not_write(self):
        before = self.snapshot()
        page = self.client.get(self.url("resource", "change", self.shared))
        self.assertContains(page, self.warning, count=1)
        self.assertTemplateUsed(page, "admin/events/resource/change_form.html")
        html = page.content.decode()
        self.assertLess(html.index(self.warning), html.index('id="id_title"'))
        self.assertContains(page, 'name="csrfmiddlewaretoken"')
        self.assertNotContains(self.client.get(self.url("resource", "add")), self.warning)
        self.assertEqual(self.snapshot(), before)

    def test_shared_bibliography_edit_updates_both_public_talks_and_preserves_links(self):
        for source, doi in (("crossref", "10.1234/edit-fixture"), ("manual", None)):
            with self.subTest(source=source):
                self.shared.metadata_source = source
                self.shared.doi = doi
                self.shared.save()
                before = self.snapshot()
                page = self.client.get(self.url("resource", "change", self.shared))
                self.assertContains(page, self.warning)
                response = self.client.post(self.url("resource", "change", self.shared), self.resource_data(
                    title="Reviewed shared fixture", authors="", year="",
                    original_url="https://example.org/reviewed", resource_type="article",
                    doi="10.1234/forged", metadata_source="manual", seed_key="forged",
                    recommendation="forged", display_order=-100,
                ))
                self.assertEqual(response.status_code, 302)
                self.shared.refresh_from_db()
                self.assertEqual((self.shared.doi, self.shared.metadata_source, self.shared.seed_key),
                                 (doi, source, "edit-fixture"))
                after = self.snapshot()
                self.assertEqual((after[0], after[2]), (before[0], before[2]))
                self.assertEqual(after[1][0], before[1][0])
                self.assertEqual(len(after[1]), 2)
                for event, link in ((self.event_a, self.link_a), (self.event_b, self.link_b)):
                    detail = self.detail(event)
                    self.assertEqual(detail["resource_count"], 2)
                    book = next(item for item in detail["resources"] if item["resource_id"] == self.shared.pk)
                    self.assertEqual((book["title"], book["authors"], book["year"], book["original_url"],
                                      book["resource_type"], book["doi"], book["metadata_source"]),
                                     ("Reviewed shared fixture", "", None, "https://example.org/reviewed",
                                      "article", doi, source))
                    self.assertEqual((book["association_id"], book["recommendation"], book["display_order"]),
                                     (link.pk, link.recommendation, link.display_order))

    def test_reason_only_edit_and_clearing_affect_only_target_association(self):
        before = self.snapshot()
        other_detail = self.detail(self.event_b)
        for reason in ("Reason A revised\nSecond line", ""):
            with self.subTest(reason=reason):
                self.edit_link(self.link_a, recommendation=reason, event=self.event_b.pk,
                               resource=self.other.pk, title="forged shared title")
                self.link_a.refresh_from_db()
                self.assertEqual((self.link_a.event_id, self.link_a.resource_id, self.link_a.display_order),
                                 (self.event_a.pk, self.shared.pk, 0))
                self.assertEqual(self.link_a.recommendation, reason)
                data = self.detail(self.event_a)["resources"][0]
                self.assertEqual(data["recommendation"], reason)
                self.assertEqual(self.detail(self.event_b), other_detail)
                after = self.snapshot()
                self.assertEqual(after[:2], before[:2])
                self.assertEqual(after[2][1:], before[2][1:])

    def test_order_only_edit_moves_target_reading_and_preserves_other_talk(self):
        before = self.snapshot()
        other_detail = self.detail(self.event_b)
        for order, ids in ((12, [self.other_a.pk, self.link_a.pk]),
                           (-4, [self.link_a.pk, self.other_a.pk])):
            with self.subTest(order=order):
                self.edit_link(self.link_a, display_order=order)
                self.link_a.refresh_from_db()
                detail = self.detail(self.event_a)
                self.assertEqual([item["association_id"] for item in detail["resources"]], ids)
                reading = next(item for item in detail["resources"] if item["association_id"] == self.link_a.pk)
                self.assertEqual((reading["display_order"], reading["recommendation"]), (order, "Reason A"))
                self.assertEqual(detail["resource_count"], 2)
                self.assertEqual(self.detail(self.event_b), other_detail)
                after = self.snapshot()
                self.assertEqual(after[:2], before[:2])
                self.assertEqual(after[2][1:], before[2][1:])

    def test_default_order_zero_and_ties_follow_association_ids(self):
        page = self.client.get(self.url("eventresource", "add"))
        self.assertEqual(page.context["adminform"].form["display_order"].value(), 0)
        self.assertGreater(self.shared.pk, self.other.pk)
        self.assertEqual([item["association_id"] for item in self.detail(self.event_a)["resources"]],
                         [self.link_a.pk, self.other_a.pk])
        resource = Resource.objects.create(title="Added fixture", original_url="https://example.org/added")
        response = self.client.post(self.url("eventresource", "add"), {
            "event": self.event_a.pk, "resource": resource.pk, "recommendation": "", "display_order": 0,
            "_save": "Save",
        })
        self.assertEqual(response.status_code, 302)
        link = EventResource.objects.get(event=self.event_a, resource=resource)
        detail = self.detail(self.event_a)
        self.assertEqual(detail["resource_count"], 3)
        self.assertEqual([item["association_id"] for item in detail["resources"]],
                         [self.link_a.pk, self.other_a.pk, link.pk])
        self.assertEqual([item["display_order"] for item in detail["resources"]], [0, 0, 0])

    def test_equal_custom_orders_remain_stable_after_native_admin_edits(self):
        other_detail = self.detail(self.event_b)
        for order in (-2, 9, 0):
            with self.subTest(order=order):
                # Save in reverse order; ties must not follow the last edit time.
                self.edit_link(self.other_a, display_order=order)
                self.edit_link(self.link_a, display_order=order)
                for _ in range(2):
                    items = self.detail(self.event_a)["resources"]
                    self.assertEqual([item["association_id"] for item in items],
                                     [self.link_a.pk, self.other_a.pk])
                    self.assertEqual([item["display_order"] for item in items], [order, order])
                self.assertEqual(self.detail(self.event_b), other_detail)

    def test_invalid_order_retains_input_without_partial_edits(self):
        before = self.snapshot()
        for order in ("1.5", "not-an-integer", "", "2147483648", "-2147483649"):
            with self.subTest(order=order):
                page = self.client.post(self.url("eventresource", "change", self.link_a), {
                    "recommendation": "Unsaved reason", "display_order": order, "_save": "Save",
                })
                self.assertEqual(page.status_code, 200)
                form = page.context["adminform"].form
                self.assertIn("display_order", form.errors)
                self.assertEqual(form["recommendation"].value(), "Unsaved reason")
                self.assertEqual(form["display_order"].value(), order)
                self.assertEqual(self.snapshot(), before)

    def test_invalid_shared_edit_retains_warning_and_both_public_talks(self):
        before = self.snapshot()
        details = [self.detail(event) for event in (self.event_a, self.event_b)]
        for changes, field in (({"title": "   "}, "title"),
                               ({"original_url": "ftp://example.org/bad"}, "original_url"),
                               ({"year": "10000"}, "year")):
            with self.subTest(field=field):
                page = self.client.post(self.url("resource", "change", self.shared),
                                        self.resource_data(**changes))
                self.assertContains(page, self.warning)
                self.assertIn(field, page.context["adminform"].form.errors)
                self.assertEqual(self.snapshot(), before)
                self.assertEqual([self.detail(event) for event in (self.event_a, self.event_b)], details)
