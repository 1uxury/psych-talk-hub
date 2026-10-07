"""Step 11 acceptance: flat reading contract, preloading and safe API errors."""

import json
from datetime import datetime, timezone
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.db import DatabaseError
from django.http import HttpResponse
from django.test import RequestFactory, override_settings
from django.urls import reverse
from django.utils import timezone as django_timezone
from rest_framework.test import APITestCase

from config.api_errors import ApiErrorMiddleware
from events.models import Event, EventResource, Resource


class EventDetailAPITests(APITestCase):
    event_fields = {
        "id", "title", "description", "topic", "starts_at", "speaker",
        "is_example", "resource_count", "cover_image_url", "cover_image_alt",
    }
    reading_fields = {
        "association_id", "resource_id", "title", "authors", "year",
        "original_url", "doi", "resource_type", "metadata_source",
        "recommendation", "display_order",
    }

    def create_event(self, **fields):
        fields.setdefault("title", "Reading talk")
        fields.setdefault("starts_at", datetime(2026, 11, 3, 19, 30, tzinfo=timezone.utc))
        return Event.objects.create(**fields)

    def create_resource(self, **fields):
        fields.setdefault("title", "Reading fixture")
        fields.setdefault("original_url", "https://example.org/reading")
        return Resource.objects.create(**fields)

    def url(self, event):
        return reverse("events:event-detail", args=[event.pk])

    def assert_json_error(self, response, status):
        self.assertEqual(response.status_code, status)
        self.assertEqual(response["Content-Type"], "application/json")
        payload = json.loads(response.content)
        self.assertEqual(set(payload), {"detail"})
        self.assertIs(type(payload["detail"]), str)
        self.assertTrue(payload["detail"].strip())
        self.assertNotIn(b"<html", response.content.lower())
        return payload

    def test_complete_detail_reuses_list_fields_and_exposes_exact_flat_reading_types(self):
        event = self.create_event(
            description="A fictional talk.", topic="Memory", speaker="Alex (fictional)",
            is_example=True, seed_key="private-event-sentinel",
        )
        self.create_resource()  # Ensure association and resource identities differ.
        resource = self.create_resource(
            authors="First Author; Second Author", year=2024, doi="10.1234/test.paper",
            resource_type=Resource.ResourceType.RESEARCH_PAPER,
            metadata_source=Resource.MetadataSource.CROSSREF,
            seed_key="private-resource-sentinel",
        )
        link = EventResource.objects.create(
            event=event, resource=resource, recommendation="Read before the talk.",
            display_order=-2,
        )
        if link.pk == resource.pk:
            # Sequences are not reset between test cases; keep this fixture distinct.
            link.delete()
            link = EventResource.objects.create(
                event=event, resource=resource, recommendation="Read before the talk.",
                display_order=-2,
            )
        self.assertNotEqual(link.pk, resource.pk)
        response = self.client.get(self.url(event))
        self.assertEqual(self.url(event), f"/api/events/{event.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        payload = response.json()
        self.assertEqual(set(payload), self.event_fields | {"resources"})
        listed = self.client.get(reverse("events:event-list")).json()[0]
        self.assertEqual({key: payload[key] for key in self.event_fields}, listed)
        for key in ("id", "resource_count"):
            self.assertIs(type(payload[key]), int)
        for key in ("title", "description", "topic", "starts_at", "speaker"):
            self.assertIs(type(payload[key]), str)
        self.assertIs(type(payload["is_example"]), bool)
        self.assertIs(type(payload["resources"]), list)
        self.assertEqual(payload["resource_count"], 1)
        self.assertEqual(payload["starts_at"], "2026-11-03T19:30:00Z")
        row = payload["resources"][0]
        self.assertEqual(set(row), self.reading_fields)
        self.assertEqual(row, {
            "association_id": link.pk, "resource_id": resource.pk,
            "title": resource.title, "authors": resource.authors, "year": 2024,
            "original_url": resource.original_url, "doi": "10.1234/test.paper",
            "resource_type": "research_paper", "metadata_source": "crossref",
            "recommendation": "Read before the talk.", "display_order": -2,
        })
        for key in ("association_id", "resource_id", "year", "display_order"):
            self.assertIs(type(row[key]), int)
        for key in self.reading_fields - {
            "association_id", "resource_id", "year", "display_order"
        }:
            self.assertIs(type(row[key]), str)
        for private_value in (b"private-event-sentinel", b"private-resource-sentinel"):
            self.assertNotIn(private_value, response.content)

    def test_optional_fields_use_empty_strings_or_null_without_display_placeholders(self):
        event = self.create_event()
        resource = self.create_resource()
        EventResource.objects.create(event=event, resource=resource)
        payload = self.client.get(self.url(event)).json()
        for key in ("description", "topic", "speaker"):
            self.assertEqual(payload[key], "")
        self.assertIs(payload["is_example"], False)
        row = payload["resources"][0]
        self.assertEqual(set(row), self.reading_fields)
        self.assertEqual(row["authors"], "")
        self.assertEqual(row["recommendation"], "")
        self.assertIsNone(row["year"])
        self.assertIsNone(row["doi"])
        self.assertEqual(row["resource_type"], "article")
        self.assertEqual(row["metadata_source"], "manual")
        self.assertIs(type(row["display_order"]), int)
        self.assertEqual(row["display_order"], 0)

    def test_zero_resources_is_an_empty_array_with_count_zero(self):
        event = self.create_event()
        other = self.create_event()
        EventResource.objects.create(event=other, resource=self.create_resource())
        payload = self.client.get(self.url(event)).json()
        self.assertEqual(payload["id"], event.pk)
        self.assertEqual(payload["resources"], [])
        self.assertIs(type(payload["resource_count"]), int)
        self.assertEqual(payload["resource_count"], 0)

    def test_negative_and_tied_orders_use_association_identity_not_resource_identity(self):
        event = self.create_event()
        resources = [self.create_resource(title=f"Reading {index}") for index in range(4)]
        first = EventResource.objects.create(event=event, resource=resources[2])
        second = EventResource.objects.create(event=event, resource=resources[1])
        last = EventResource.objects.create(event=event, resource=resources[0], display_order=9)
        early = EventResource.objects.create(event=event, resource=resources[3], display_order=-5)
        expected = [early, first, second, last]
        payload = self.client.get(self.url(event), {"ordering": "resource_id"}).json()
        self.assertEqual(payload["resource_count"], 4)
        self.assertEqual([row["association_id"] for row in payload["resources"]],
                         [link.pk for link in expected])
        self.assertEqual([row["resource_id"] for row in payload["resources"]],
                         [link.resource_id for link in expected])
        second.display_order = -6
        second.save(update_fields=["display_order"])
        rows = self.client.get(self.url(event)).json()["resources"]
        self.assertEqual([row["association_id"] for row in rows],
                         [second.pk, early.pk, first.pk, last.pk])

    def test_shared_metadata_and_current_event_context_refresh_independently(self):
        first, second = self.create_event(), self.create_event()
        shared = self.create_resource()
        link = EventResource.objects.create(
            event=first, resource=shared, recommendation="First reason", display_order=-1
        )
        other = EventResource.objects.create(
            event=second, resource=shared, recommendation="Second reason", display_order=7
        )
        unrelated = self.create_resource(title="Another event only")
        EventResource.objects.create(event=second, resource=unrelated)
        self.create_resource(title="Unlinked reading")
        a, b = [self.client.get(self.url(event)).json() for event in (first, second)]
        self.assertEqual((a["resource_count"], b["resource_count"]), (1, 2))
        self.assertEqual(a["resources"][0]["recommendation"], "First reason")
        second_shared = next(row for row in b["resources"] if row["resource_id"] == shared.pk)
        self.assertEqual(second_shared["association_id"], other.pk)
        self.assertEqual(second_shared["recommendation"], "Second reason")
        self.assertEqual(second_shared["display_order"], 7)
        shared.title = "Edited shared title"
        shared.save(update_fields=["title"])
        link.recommendation = "Edited first reason"
        link.save(update_fields=["recommendation"])
        a, b = [self.client.get(self.url(event)).json() for event in (first, second)]
        self.assertEqual(a["resources"][0]["title"], shared.title)
        self.assertEqual(a["resources"][0]["recommendation"], "Edited first reason")
        second_shared = next(row for row in b["resources"] if row["resource_id"] == shared.pk)
        self.assertEqual(second_shared["title"], shared.title)
        self.assertEqual(second_shared["recommendation"], "Second reason")
        link.delete()
        self.assertEqual(self.client.get(self.url(first)).json()["resources"], [])
        self.assertEqual(self.client.get(self.url(first)).json()["resource_count"], 0)
        self.assertEqual(self.client.get(self.url(second)).json()["resource_count"], 2)
        self.assertTrue(Resource.objects.filter(pk=shared.pk).exists())

    def test_detail_time_remains_utc_for_winter_summer_and_active_timezone_changes(self):
        for month, expected in ((1, "2026-01-15T19:30:00Z"), (7, "2026-07-15T18:30:00Z")):
            event = self.create_event(
                starts_at=datetime(2026, month, 15, 19, 30, tzinfo=ZoneInfo("Europe/London"))
            )
            for zone in ("Europe/London", "UTC", "Asia/Tokyo"):
                with self.subTest(month=month, zone=zone), django_timezone.override(zone):
                    self.assertEqual(self.client.get(self.url(event)).json()["starts_at"], expected)

    def test_two_queries_for_zero_one_and_twenty_one_resources(self):
        event = self.create_event()
        for target_count in (0, 1, 21):
            while EventResource.objects.filter(event=event).count() < target_count:
                EventResource.objects.create(event=event, resource=self.create_resource())
            with self.subTest(count=target_count), self.assertNumQueries(2):
                response = self.client.get(self.url(event))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["resource_count"], target_count)
            self.assertEqual(len(response.json()["resources"]), target_count)

    def test_detail_read_does_not_call_external_services_or_change_business_records(self):
        event = self.create_event(seed_key="preserve-event")
        resource = self.create_resource(seed_key="preserve-resource")
        EventResource.objects.create(event=event, resource=resource, recommendation="Keep")

        def snapshot():
            return [list(model.objects.order_by("id").values())
                    for model in (Event, Resource, EventResource)]

        before = snapshot()
        with patch("requests.sessions.Session.request") as external_request:
            response = self.client.get(self.url(event))
        self.assertEqual(response.status_code, 200)
        external_request.assert_not_called()
        self.assertEqual(snapshot(), before)

    def test_missing_and_deleted_events_return_json_404_in_both_debug_modes(self):
        event = self.create_event()
        deleted_url = self.url(event)
        event.delete()
        for debug in (False, True):
            with self.subTest(debug=debug), override_settings(DEBUG=debug):
                for url in (deleted_url, "/api/events/0/", "/api/events/999999999/"):
                    self.assert_json_error(self.client.get(url), 404)

    def test_unknown_api_paths_are_json_404_even_when_html_is_requested(self):
        paths = (
            "/api", "/api/", "/api/missing", "/api/missing/deep/",
            "/api/events/not-an-id/", "/api/events/-1/", "/api/events/1/missing/",
            "/api/events",  # Only the specified trailing-slash API routes are valid.
        )
        for debug in (False, True):
            with override_settings(DEBUG=debug):
                for url in paths:
                    with self.subTest(debug=debug, url=url):
                        self.assert_json_error(self.client.get(url, HTTP_ACCEPT="text/html"), 404)

    def test_list_and_detail_query_failures_are_safe_json_500_in_both_debug_modes(self):
        event = self.create_event()
        sensitive = "private-password SQL SELECT FROM internal_table"
        targets = (
            ("events.views.EventListView.get_queryset", reverse("events:event-list")),
            ("events.views.EventDetailView.get_queryset", self.url(event)),
        )
        for debug in (False, True):
            with override_settings(DEBUG=debug):
                for target, url in targets:
                    with self.subTest(debug=debug, target=target), patch(
                        target, side_effect=DatabaseError(sensitive)
                    ), self.assertLogs("config.api_errors", level="ERROR") as logs:
                        response = self.client.get(url)
                    self.assertEqual(self.assert_json_error(response, 500),
                                     {"detail": "Internal server error."})
                    self.assertNotIn(sensitive.encode(), response.content)
                    self.assertNotIn(sensitive, " ".join(logs.output))
                    self.assertIn("DatabaseError", " ".join(logs.output))

    def test_serializer_failure_is_safe_json_500(self):
        event = self.create_event()
        with override_settings(DEBUG=True), patch(
            "events.serializers.EventDetailSerializer.to_representation",
            side_effect=ValueError("private-serialization-detail"),
        ), self.assertLogs("config.api_errors", level="ERROR"):
            response = self.client.get(self.url(event))
        self.assert_json_error(response, 500)
        self.assertNotIn(b"private-serialization-detail", response.content)

    def test_deferred_renderer_failure_is_safe_json_500(self):
        event = self.create_event()
        with override_settings(DEBUG=True), patch(
            "rest_framework.renderers.JSONRenderer.render",
            side_effect=RuntimeError("private-render-detail"),
        ), self.assertLogs("config.api_errors", level="ERROR"):
            response = self.client.get(self.url(event))
        self.assert_json_error(response, 500)
        self.assertNotIn(b"private-render-detail", response.content)

    def test_error_boundary_sanitises_api_500_and_preserves_non_api_responses(self):
        middleware = ApiErrorMiddleware(lambda request: HttpResponse())
        factory = RequestFactory()
        response = middleware.process_response(
            factory.get("/api/events/"), HttpResponse("private middleware fault", status=500)
        )
        self.assert_json_error(response, 500)
        for path in ("/admin/", "/healthz/", "/events/1", "/api-other/"):
            request = factory.get(path)
            self.assertIsNone(middleware.process_exception(request, RuntimeError("private")))
            original = HttpResponse("Non-API response", status=500)
            self.assertIs(middleware.process_response(request, original), original)
        with override_settings(DEBUG=False):
            response = self.client.get("/outside-api/")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(response["Content-Type"].startswith("text/html"))
