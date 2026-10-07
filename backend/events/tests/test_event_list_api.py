"""Step 10 acceptance: public list contract and constant query count."""

from datetime import datetime, timezone
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.urls import reverse
from django.utils import timezone as django_timezone
from rest_framework.test import APITestCase

from events.models import Event, EventResource, Resource


class EventListAPITests(APITestCase):
    url = reverse("events:event-list")
    public_fields = {
        "id", "title", "description", "topic", "starts_at", "speaker",
        "is_example", "resource_count",
    }

    def create_event(self, title="Reading talk", **fields):
        fields.setdefault("starts_at", datetime(2026, 11, 3, 19, 30, tzinfo=timezone.utc))
        return Event.objects.create(title=title, **fields)

    def create_resource(self, title="Reading fixture"):
        return Resource.objects.create(
            title=title, original_url="https://example.org/reading"
        )

    def test_anonymous_empty_list_is_unwrapped_json_array(self):
        self.assertEqual(self.url, "/api/events/")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json(), [])
        self.assertEqual(response.content, b"[]")

    def test_complete_event_matches_exact_public_fields_and_types(self):
        event = self.create_event(
            title="Example event: memory", description="A fictional talk.",
            topic="Memory", speaker="Alex Morgan (fictional)",
            is_example=True, seed_key="private-import-sentinel",
        )
        EventResource.objects.create(event=event, resource=self.create_resource())
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIsInstance(payload, list)
        self.assertEqual(len(payload), 1)
        row = payload[0]
        self.assertEqual(set(row), self.public_fields)
        self.assertEqual(row, {
            "id": event.pk, "title": event.title, "description": event.description,
            "topic": event.topic, "starts_at": "2026-11-03T19:30:00Z",
            "speaker": event.speaker, "is_example": True, "resource_count": 1,
        })
        for name in ("id", "resource_count"):
            self.assertIs(type(row[name]), int)
        for name in ("title", "description", "topic", "starts_at", "speaker"):
            self.assertIs(type(row[name]), str)
        self.assertIs(type(row["is_example"]), bool)
        self.assertNotIn(b"private-import-sentinel", response.content)

    def test_optional_text_defaults_are_empty_and_zero_reading_is_retained(self):
        event = self.create_event()
        row = self.client.get(self.url).json()[0]
        self.assertEqual(set(row), self.public_fields)
        self.assertEqual(row["id"], event.pk)
        for name in ("description", "topic", "speaker"):
            self.assertEqual(row[name], "")
        self.assertIs(row["is_example"], False)
        self.assertIs(type(row["resource_count"]), int)
        self.assertEqual(row["resource_count"], 0)

    def test_all_events_are_ordered_by_id_without_time_grouping_or_pagination(self):
        events = [self.create_event(starts_at=instant) for instant in (
            datetime(2027, 1, 1, tzinfo=timezone.utc),
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            datetime(2026, 1, 1, tzinfo=timezone.utc),
        )]
        response = self.client.get(self.url, {"page": 2, "ordering": "-starts_at"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [row["id"] for row in response.json()], [event.pk for event in events]
        )

    def test_counts_include_only_current_links_and_refresh_after_changes(self):
        first, second, empty = [self.create_event() for _ in range(3)]
        shared = self.create_resource("Shared")
        other = self.create_resource("First talk only")
        self.create_resource("Unlinked")
        EventResource.objects.create(event=first, resource=shared)
        removed = EventResource.objects.create(event=first, resource=other)
        EventResource.objects.create(event=second, resource=shared)

        def counts():
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            return {row["id"]: row["resource_count"] for row in response.json()}

        self.assertEqual(counts(), {first.pk: 2, second.pk: 1, empty.pk: 0})
        removed.delete()
        self.assertEqual(counts(), {first.pk: 1, second.pk: 1, empty.pk: 0})
        EventResource.objects.create(event=empty, resource=other)
        self.assertEqual(counts(), {first.pk: 1, second.pk: 1, empty.pk: 1})

    def test_winter_and_summer_times_remain_utc_under_different_active_timezones(self):
        winter = self.create_event(
            starts_at=datetime(2026, 1, 15, 19, 30, tzinfo=ZoneInfo("Europe/London"))
        )
        summer = self.create_event(
            starts_at=datetime(2026, 7, 15, 19, 30, 0, 123456,
                               tzinfo=ZoneInfo("Europe/London"))
        )
        for zone in ("Europe/London", "UTC", "Asia/Tokyo"):
            with self.subTest(zone=zone), django_timezone.override(zone):
                times = {row["id"]: row["starts_at"]
                         for row in self.client.get(self.url).json()}
                self.assertEqual(times, {
                    winter.pk: "2026-01-15T19:30:00Z",
                    summer.pk: "2026-07-15T18:30:00.123456Z",
                })

    def test_one_database_query_for_empty_single_and_many_populated_events(self):
        with self.assertNumQueries(1):
            response = self.client.get(self.url)
        self.assertEqual(response.json(), [])
        resource = self.create_resource()
        event = self.create_event()
        EventResource.objects.create(event=event, resource=resource)
        with self.assertNumQueries(1):
            response = self.client.get(self.url)
        self.assertEqual(len(response.json()), 1)
        for index in range(20):
            event = self.create_event(title=f"Talk {index}")
            EventResource.objects.create(event=event, resource=resource)
        with self.assertNumQueries(1):
            response = self.client.get(self.url)
        rows = response.json()
        self.assertEqual(len(rows), 21)
        self.assertTrue(all(row["resource_count"] == 1 for row in rows))

    def test_reading_neither_calls_external_services_nor_changes_business_records(self):
        event = self.create_event(seed_key="keep-event-identity")
        resource = self.create_resource()
        EventResource.objects.create(
            event=event, resource=resource, recommendation="Keep this.", display_order=-3
        )

        def snapshot():
            return [list(model.objects.order_by("id").values())
                    for model in (Event, Resource, EventResource)]

        before = snapshot()
        with patch("requests.sessions.Session.request") as external_request:
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        external_request.assert_not_called()
        self.assertEqual(snapshot(), before)
