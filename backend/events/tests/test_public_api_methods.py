"""Step 12: public endpoints stay read-only, even with an Admin session."""

import json
from datetime import datetime, timezone
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from events.models import Event, EventResource, Resource


class PublicAPIMethodTests(APITestCase):
    allowed_methods = {"GET", "HEAD", "OPTIONS"}
    rejected_methods = ("POST", "PUT", "PATCH", "DELETE", "TRACE", "CONNECT", "PURGE")

    @classmethod
    def setUpTestData(cls):
        cls.admin_user = get_user_model().objects.create_superuser(
            username="public-method-admin", email="admin@example.org",
            password="test-only-password",
        )
        cls.event = Event.objects.create(
            title="Preserve this talk", description="Keep the description.",
            topic="Memory", speaker="Test speaker", is_example=True,
            starts_at=datetime(2026, 11, 3, 19, 30, tzinfo=timezone.utc),
            seed_key="method-event-identity",
        )
        cls.other_event = Event.objects.create(
            title="Keep the other talk", starts_at=cls.event.starts_at
        )
        cls.resource = Resource.objects.create(
            title="Preserve shared reading", authors="Test author", year=2024,
            original_url="https://example.org/reading", doi="10.1234/method-fixture",
            resource_type=Resource.ResourceType.RESEARCH_PAPER,
            metadata_source=Resource.MetadataSource.CROSSREF,
        )
        cls.unlinked_resource = Resource.objects.create(
            title="Preserve unlinked reading", original_url="https://example.org/unlinked",
            seed_key="method-resource-identity",
        )
        cls.link = EventResource.objects.create(
            event=cls.event, resource=cls.resource,
            recommendation="Keep this recommendation.", display_order=-3,
        )
        EventResource.objects.create(
            event=cls.other_event, resource=cls.resource,
            recommendation="Keep the other recommendation.", display_order=7,
        )

    def endpoints(self):
        return (
            reverse("events:event-list"),
            reverse("events:event-detail", args=[self.event.pk]),
        )

    def client_for(self, administrator=False):
        client = APIClient(enforce_csrf_checks=True)
        if administrator:
            # A real database session, not DRF force_authenticate or a fake header.
            client.force_login(self.admin_user)
            response = client.get(reverse("admin:index"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.wsgi_request.user.pk, self.admin_user.pk)
            self.assertTrue(response.wsgi_request.user.is_superuser)
        return client

    def snapshot(self):
        # Compare every stored field, including private identities and shared links.
        return [list(model.objects.order_by("id").values())
                for model in (Event, Resource, EventResource)]

    def assert_allow_header(self, response):
        methods = [method.strip() for method in response["Allow"].split(",")]
        self.assertEqual(set(methods), self.allowed_methods)
        self.assertEqual(len(methods), len(self.allowed_methods))

    def assert_method_rejected(self, response, method):
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response["Content-Type"], "application/json")
        payload = response.json()
        self.assertEqual(set(payload), {"detail"})
        self.assertIsInstance(payload["detail"], str)
        self.assertTrue(payload["detail"].strip())
        self.assertIn(method, payload["detail"])
        self.assert_allow_header(response)

    def write_payload(self):
        return {
            "id": self.event.pk, "title": "Attempted replacement",
            "description": "Attempted change", "topic": "Changed topic",
            "starts_at": "2027-01-01T00:00:00Z", "speaker": "Changed speaker",
            "is_example": False, "seed_key": "attempted-identity",
            "resources": [{
                "association_id": self.link.pk, "resource_id": self.resource.pk,
                "title": "Attempted bibliography change", "authors": "Changed author",
                "year": 2025, "original_url": "https://example.org/replacement",
                "doi": "10.1234/replacement", "resource_type": "article",
                "metadata_source": "manual", "recommendation": "Changed reason",
                "display_order": 100,
            }],
        }

    def assert_gets(self, administrator):
        client = self.client_for(administrator)
        before = self.snapshot()
        with patch("requests.sessions.Session.request") as external_request:
            for url in self.endpoints():
                with self.subTest(url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response["Content-Type"], "application/json")
                    self.assert_allow_header(response)
                    if url == self.endpoints()[0]:
                        self.assertEqual(
                            [row["id"] for row in response.json()],
                            [self.event.pk, self.other_event.pk],
                        )
                    else:
                        payload = response.json()
                        self.assertEqual(payload["id"], self.event.pk)
                        self.assertEqual(payload["resources"][0]["association_id"], self.link.pk)
                    self.assertEqual(self.snapshot(), before)
            external_request.assert_not_called()

    def test_anonymous_gets_remain_public_and_preserve_records(self):
        self.assert_gets(administrator=False)

    def test_logged_in_administrator_gets_remain_read_only(self):
        self.assert_gets(administrator=True)

    def assert_heads(self, administrator):
        client = self.client_for(administrator)
        before = self.snapshot()
        with patch("requests.sessions.Session.request") as external_request:
            for url in self.endpoints():
                with self.subTest(url=url):
                    get_response = client.get(url)
                    head_response = client.head(url)
                    self.assertEqual(get_response.status_code, 200)
                    self.assertEqual(head_response.status_code, get_response.status_code)
                    self.assertEqual(head_response.content, b"")
                    for header in ("Content-Type", "Content-Length", "Allow"):
                        self.assertEqual(head_response[header], get_response[header])
                    self.assert_allow_header(head_response)
                    self.assertEqual(self.snapshot(), before)
            external_request.assert_not_called()

    def test_anonymous_heads_return_get_status_and_headers_without_body(self):
        self.assert_heads(administrator=False)

    def test_administrator_heads_return_get_status_and_headers_without_body(self):
        self.assert_heads(administrator=True)

    def assert_options(self, administrator):
        client = self.client_for(administrator)
        before = self.snapshot()
        with (
            patch("events.views.EventListView.get_queryset") as list_query,
            patch("events.views.EventDetailView.get_queryset") as detail_query,
            patch("requests.sessions.Session.request") as external_request,
        ):
            for url in self.endpoints():
                with self.subTest(url=url):
                    response = client.options(url)
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response["Content-Type"], "application/json")
                    self.assert_allow_header(response)
                    metadata = response.json()
                    self.assertEqual(metadata["renders"], ["application/json"])
                    self.assertNotIn("actions", metadata)
                    self.assertEqual(self.snapshot(), before)
            list_query.assert_not_called()
            detail_query.assert_not_called()
            external_request.assert_not_called()

    def test_anonymous_options_advertise_only_read_methods_without_write_actions(self):
        self.assert_options(administrator=False)

    def test_administrator_options_do_not_advertise_extra_capabilities(self):
        self.assert_options(administrator=True)

    def assert_rejected_methods(self, administrator):
        client = self.client_for(administrator)
        before = self.snapshot()
        with (
            patch("events.views.EventListView.get_queryset") as list_query,
            patch("events.views.EventDetailView.get_queryset") as detail_query,
            patch("requests.sessions.Session.request") as external_request,
        ):
            for url in self.endpoints():
                for method in self.rejected_methods:
                    with self.subTest(url=url, method=method):
                        response = client.generic(
                            method, url, data=json.dumps(self.write_payload()),
                            content_type="application/json",
                        )
                        self.assert_method_rejected(response, method)
                        self.assertEqual(self.snapshot(), before)
            list_query.assert_not_called()
            detail_query.assert_not_called()
            external_request.assert_not_called()

    def test_anonymous_write_and_other_methods_return_json_405_without_changes(self):
        self.assert_rejected_methods(administrator=False)

    def test_administrator_write_and_other_methods_return_json_405_without_changes(self):
        self.assert_rejected_methods(administrator=True)

    def test_write_methods_on_missing_event_are_rejected_before_object_lookup(self):
        url = reverse("events:event-detail", args=[0])
        for administrator in (False, True):
            client = self.client_for(administrator)
            before = self.snapshot()
            with patch("events.views.EventDetailView.get_queryset") as detail_query:
                for method in ("POST", "PUT", "PATCH", "DELETE"):
                    with self.subTest(administrator=administrator, method=method):
                        response = client.generic(
                            method, url, data=json.dumps(self.write_payload()),
                            content_type="application/json",
                        )
                        self.assert_method_rejected(response, method)
                        self.assertEqual(self.snapshot(), before)
                detail_query.assert_not_called()

    def test_rejected_methods_do_not_parse_invalid_or_unsupported_request_bodies(self):
        for administrator in (False, True):
            client = self.client_for(administrator)
            before = self.snapshot()
            for url in self.endpoints():
                for method in ("POST", "PUT", "PATCH", "DELETE"):
                    for content_type, body in (
                        ("application/json", "{"),
                        ("application/octet-stream", "not a supported document"),
                    ):
                        with self.subTest(
                            administrator=administrator, url=url,
                            method=method, content_type=content_type,
                        ):
                            response = client.generic(
                                method, url, data=body, content_type=content_type
                            )
                            self.assert_method_rejected(response, method)
                            self.assertEqual(self.snapshot(), before)

    def test_method_override_hints_cannot_enable_writes_or_turn_post_into_get(self):
        for administrator in (False, True):
            client = self.client_for(administrator)
            before = self.snapshot()
            for url in self.endpoints():
                for method in ("POST", "PUT", "PATCH", "DELETE"):
                    with self.subTest(administrator=administrator, url=url, hint=method):
                        response = client.get(
                            url, {"_method": method}, HTTP_X_HTTP_METHOD_OVERRIDE=method
                        )
                        self.assertEqual(response.status_code, 200)
                        self.assert_allow_header(response)
                        self.assertEqual(self.snapshot(), before)
                response = client.post(
                    url, {**self.write_payload(), "_method": "GET"}, format="json",
                    HTTP_X_HTTP_METHOD_OVERRIDE="GET",
                )
                self.assert_method_rejected(response, "POST")
                self.assertEqual(self.snapshot(), before)

    def test_missing_event_head_keeps_json_404_headers_without_body(self):
        url = reverse("events:event-detail", args=[0])
        for administrator in (False, True):
            with self.subTest(administrator=administrator):
                client = self.client_for(administrator)
                before = self.snapshot()
                get_response = client.get(url)
                head_response = client.head(url)
                self.assertEqual(get_response.status_code, 404)
                self.assertEqual(head_response.status_code, 404)
                self.assertEqual(head_response.content, b"")
                for header in ("Content-Type", "Content-Length", "Allow"):
                    self.assertEqual(head_response[header], get_response[header])
                self.assert_allow_header(head_response)
                self.assertEqual(self.snapshot(), before)
