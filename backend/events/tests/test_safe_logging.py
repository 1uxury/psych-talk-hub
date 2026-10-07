"""Failures remain diagnosable without logging secrets or preview identifiers."""

import logging
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.db import OperationalError
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from config.health import healthz
from config.safe_logging import SafeRequestFilter
from events.models import Event, EventResource, Resource
from events.services.crossref import CrossrefLookupError
from events.services.crossref_metadata import CrossrefMetadata

SENSITIVE = "private-password-cookie-provider-body-preview-id"


class SafeRequestLogTests(SimpleTestCase):
    def test_request_and_csrf_logs_remove_paths_query_and_exception_values(self):
        for name in ("django.request", "django.security.csrf", "django.security.DisallowedHost"):
            with self.subTest(name=name):
                try:
                    raise OperationalError(SENSITIVE)
                except OperationalError:
                    import sys
                    record = logging.LogRecord(name, logging.ERROR, __file__, 1, "Rejected %s", (SENSITIVE,), sys.exc_info())
                record.status_code = 403
                record.exc_text = SENSITIVE
                record.stack_info = SENSITIVE
                self.assertTrue(SafeRequestFilter().filter(record))
                rendered = logging.Formatter("%(name)s %(message)s").format(record)
                self.assertNotIn(SENSITIVE, rendered)
                self.assertIn("403", rendered)
                self.assertIsNone(record.exc_info)

    def test_health_failure_is_safe_and_never_calls_crossref(self):
        failed_connection = Mock()
        failed_connection.cursor.side_effect = OperationalError(SENSITIVE)
        with patch("config.health.connection", failed_connection), \
             patch("requests.sessions.Session.request") as external, \
             self.assertLogs("config.health", level="WARNING") as logs:
            response = healthz(RequestFactory().get("/healthz/"))
        self.assertEqual(response.status_code, 503)
        self.assertNotIn(SENSITIVE.encode(), response.content)
        self.assertNotIn(SENSITIVE, " ".join(logs.output))
        self.assertIn("OperationalError", " ".join(logs.output))
        external.assert_not_called()


class SafeImportLogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser("safe-log-admin", password="test-only")
        cls.event = Event.objects.create(title="Safe log fixture", starts_at=timezone.now())

    def setUp(self):
        self.client.force_login(self.user)
        network = patch("requests.sessions.Session.request", side_effect=AssertionError("No real HTTP"))
        network.start()
        self.addCleanup(network.stop)

    def snapshot(self):
        return [list(model.objects.values()) for model in (Event, Resource, EventResource)]

    def test_lookup_failure_logs_only_category_and_preserves_input_and_business(self):
        before = self.snapshot()
        with patch("events.services.doi_preview.fetch_metadata", side_effect=CrossrefLookupError("timeout", "10.1234/" + SENSITIVE)), \
             self.assertLogs("events.doi_admin", level="WARNING") as logs:
            response = self.client.post(reverse("admin:events_event_doi_lookup", args=[self.event.pk]),
                                        {"action": "fetch", "doi": "10.1234/" + SENSITIVE})
        self.assertContains(response, "Please try again")
        self.assertContains(response, SENSITIVE)
        self.assertEqual(before, self.snapshot())
        self.assertIn("timeout", " ".join(logs.output))
        self.assertNotIn(SENSITIVE, " ".join(logs.output))

    def test_save_failure_logs_category_retains_form_and_does_not_publish(self):
        with patch("events.services.doi_preview.fetch_metadata", return_value=CrossrefMetadata(
            "Fixture", "", None, "https://example.org/fixture", "10.1234/fixture", "article",
        )):
            preview = self.client.post(reverse("admin:events_event_doi_lookup", args=[self.event.pk]),
                                       {"action": "fetch", "doi": "10.1234/fixture"})
        before = self.snapshot()
        with patch("events.doi_admin.confirm_preview", side_effect=OperationalError(SENSITIVE)), \
             self.assertLogs("events.doi_admin", level="ERROR") as logs:
            response = self.client.post(preview.url, {
                "action": "save", "title": SENSITIVE, "authors": "", "year": "",
                "original_url": "https://example.org/fixture", "resource_type": "article",
                "recommendation": SENSITIVE, "display_order": "0",
            })
        self.assertContains(response, "Please try again")
        self.assertContains(response, SENSITIVE)
        self.assertEqual(before, self.snapshot())
        self.assertIn("OperationalError", " ".join(logs.output))
        self.assertNotIn(SENSITIVE, " ".join(logs.output))
