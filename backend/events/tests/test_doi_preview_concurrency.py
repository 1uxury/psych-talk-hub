"""Real concurrent Admin requests sharing one database session on PostgreSQL."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db import connections
from django.test import Client, TransactionTestCase
from django.urls import reverse
from django.utils import timezone

from config.session_backend import PREVIEW_KEY, SessionStore
from events.models import Event, EventResource, Resource
from events.services.crossref_metadata import CrossrefMetadata


class DoiPreviewConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("concurrent-preview", password="test-only")
        self.event = Event.objects.create(title="Concurrent target", starts_at=timezone.now())
        self.other = Event.objects.create(title="Second target", starts_at=timezone.now())
        self.client.force_login(self.user)
        self.key = self.client.session.session_key
        self.network_patch = patch("requests.sessions.Session.request", side_effect=AssertionError("No real HTTP"))
        self.network = self.network_patch.start()
        self.addCleanup(self.network_patch.stop)
        self.addCleanup(self.network.assert_not_called)
        self.metadata_patch = patch("events.services.doi_preview.fetch_metadata", side_effect=self.metadata)
        self.metadata_mock = self.metadata_patch.start()
        self.addCleanup(self.metadata_patch.stop)
        self.before = self.snapshot()

    def metadata(self, doi):
        # The provider is mocked, but the HTTP view/session writes are real.
        self.assertFalse(connections["default"].in_atomic_block)
        return CrossrefMetadata("Concurrent fixture", "", None, "https://example.org/fixture", doi, "article")

    def snapshot(self):
        return [list(model.objects.order_by("pk").values()) for model in (Event, Resource, EventResource)]

    def url(self, event):
        return reverse("admin:events_event_doi_lookup", args=[event.pk])

    def states(self):
        return Session.objects.get(session_key=self.key).get_decoded().get(PREVIEW_KEY, {})

    def fetch(self, event, doi):
        response = self.client.post(self.url(event), {"action": "fetch", "doi": doi})
        self.assertEqual(response.status_code, 302)
        return response.url

    def race(self, actions):
        start = Barrier(2, timeout=10)
        lock_gate = Barrier(2, timeout=10)

        def worker(index):
            db = connections["default"]
            db.close()
            try:
                with db.cursor() as cursor:
                    cursor.execute("SET statement_timeout = '12s'")
                    cursor.execute("SET lock_timeout = '10s'")
                    cursor.execute("SELECT pg_backend_pid(), current_database()")
                    pid, database = cursor.fetchone()
                self.assertTrue(database.startswith("test_"))
                gated = False

                def gate(execute, sql, params, many, context):
                    nonlocal gated
                    if not gated and '"django_session"' in sql and "FOR UPDATE" in sql:
                        gated = True
                        # Both requests reach a real row lock from independent
                        # connections; row reads happen after acquiring the lock.
                        lock_gate.wait()
                    return execute(sql, params, many, context)

                client = Client()
                client.cookies[settings.SESSION_COOKIE_NAME] = self.key
                start.wait()
                with db.execute_wrapper(gate):
                    result = actions[index](client)
                self.assertTrue(gated)
                self.assertFalse(db.needs_rollback)
                return pid, database, result
            finally:
                db.close()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(worker, index) for index in range(2)]
            results = [future.result(timeout=25) for future in futures]
        self.assertNotEqual(results[0][0], results[1][0])
        self.assertEqual(results[0][1], results[1][1])
        self.assertEqual(results[0][1], connections["default"].settings_dict["NAME"])
        self.assertEqual(self.snapshot(), self.before)
        return [item[2] for item in results]

    def test_simultaneous_fetches_same_session_keep_both_tabs(self):
        for round_number in range(3):
            results = self.race([
                lambda client: client.post(self.url(self.event), {"action": "fetch", "doi": f"10.1234/tab-a-{round_number}"}),
                lambda client: client.post(self.url(self.other), {"action": "fetch", "doi": f"10.1234/tab-b-{round_number}"}),
            ])
            self.assertEqual([response.status_code for response in results], [302, 302])
            self.assertEqual(len(self.states()), 2 * (round_number + 1))
            for response in results:
                self.assertEqual(self.client.get(response.url).status_code, 200)
        self.assertEqual(self.metadata_mock.call_count, 6)

    def test_cancel_and_fetch_merge_without_resurrecting_other_tab(self):
        first = self.fetch(self.event, "10.1234/first")
        second = self.fetch(self.other, "10.1234/second")
        second_id = second.rstrip("/").split("/")[-1]
        original_second = self.states()[second_id]
        results = self.race([
            lambda client: client.post(first, {"action": "cancel"}),
            lambda client: client.post(self.url(self.other), {"action": "fetch", "doi": "10.1234/third"}),
        ])
        self.assertEqual([response.status_code for response in results], [302, 302])
        self.assertEqual(len(self.states()), 3)
        self.assertEqual(self.states()[second_id], original_second)
        self.assertEqual(self.client.get(first).status_code, 400)
        self.assertEqual(self.client.get(second).status_code, 200)
        self.assertEqual(self.client.get(results[1].url).status_code, 200)

    def test_cancel_racing_stale_ordinary_session_save_keeps_latest_namespace(self):
        first = self.fetch(self.event, "10.1234/first")
        second = self.fetch(self.other, "10.1234/second")
        stale = SessionStore(self.key)
        stale.items()
        stale["ordinary"] = "changed by unrelated request"

        def save_stale(client):
            # Its session snapshot was loaded before either racing operation.
            stale.save()
            return "saved"

        results = self.race([
            lambda client: client.post(first, {"action": "cancel"}), save_stale,
        ])
        self.assertEqual(results[0].status_code, 302)
        self.assertEqual(results[1], "saved")
        self.assertEqual(len(self.states()), 2)
        self.assertEqual(self.client.get(first).status_code, 400)
        self.assertEqual(self.client.get(second).status_code, 200)
