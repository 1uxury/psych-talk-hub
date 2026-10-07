"""Real PostgreSQL requests: confirmation/replay and cancellation races."""

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

from config.session_backend import PREVIEW_KEY
from events.models import Event, EventResource, Resource
from events.services.crossref_metadata import CrossrefMetadata


class DoiConfirmationConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("race-confirm", password="test-only")
        self.event = Event.objects.create(title="First confirmation target", starts_at=timezone.now())
        self.other = Event.objects.create(title="Second confirmation target", starts_at=timezone.now())
        self.client.force_login(self.user)
        self.key = self.client.session.session_key
        network = patch("requests.sessions.Session.request", side_effect=AssertionError("No real HTTP"))
        self.network = network.start()
        self.addCleanup(network.stop)
        self.addCleanup(self.network.assert_not_called)
        provider = patch("events.services.doi_preview.fetch_metadata", side_effect=lambda doi: CrossrefMetadata(
            "Race fixture", "", None, "https://example.org/race", doi, "article",
        ))
        self.provider = provider.start()
        self.addCleanup(provider.stop)

    def fetch(self, event, client=None):
        response = (client or self.client).post(reverse("admin:events_event_doi_lookup", args=[event.pk]),
                                               {"action": "fetch", "doi": "10.1234/race"})
        self.assertEqual(response.status_code, 302)
        return response.url

    def submitted(self, index):
        return {"action": "save", "title": f"Reviewed winner {index}", "authors": "", "year": "",
                "original_url": "https://example.org/race", "resource_type": "article",
                "recommendation": f"Winner reason {index}", "display_order": index}

    def race(self, actions, keys=None, *, insertion=False):
        keys = keys or [self.key, self.key]
        start, gate = Barrier(2, timeout=10), Barrier(2, timeout=10)
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
                def synchronize(execute, sql, params, many, context):
                    nonlocal gated
                    match = ('INSERT INTO "events_resource"' in sql if insertion else
                             '"django_session"' in sql and "FOR UPDATE" in sql)
                    if match and not gated:
                        gated = True
                        gate.wait()
                    return execute(sql, params, many, context)
                client = Client()
                client.cookies[settings.SESSION_COOKIE_NAME] = keys[index]
                start.wait()
                with db.execute_wrapper(synchronize):
                    result = actions[index](client)
                self.assertTrue(gated)
                self.assertFalse(db.needs_rollback)
                self.assertTrue(db.get_autocommit())
                with db.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    self.assertEqual(cursor.fetchone(), (1,))
                return pid, database, result
            finally:
                db.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(worker, i) for i in range(2)]
            results = [f.result(timeout=25) for f in futures]
        self.assertNotEqual(results[0][0], results[1][0])
        self.assertEqual(results[0][1], results[1][1])
        self.assertEqual(results[0][1], connections["default"].settings_dict["NAME"])
        return [r[2] for r in results]

    def test_same_preview_concurrent_confirm_returns_one_result_preserves_winner(self):
        url = self.fetch(self.event)
        untouched = self.fetch(self.other)
        before = Session.objects.get(session_key=self.key).get_decoded()[PREVIEW_KEY]
        results = self.race([lambda c: c.post(url, self.submitted(0)), lambda c: c.post(url, self.submitted(1))])
        self.assertEqual([r.status_code for r in results], [302, 302])
        self.assertEqual(Resource.objects.count(), 1)
        self.assertEqual(EventResource.objects.count(), 1)
        link = EventResource.objects.get()
        self.assertIn(link.recommendation, ("Winner reason 0", "Winner reason 1"))
        winner = int(link.recommendation[-1])
        self.assertEqual(link.display_order, winner)
        self.assertEqual(link.resource.title, f"Reviewed winner {winner}")
        states = Session.objects.get(session_key=self.key).get_decoded()[PREVIEW_KEY]
        untouched_id = untouched.rstrip("/").split("/")[-1]
        self.assertEqual(states[untouched_id], before[untouched_id])
        self.assertContains(self.client.get(url), "Resource added to this talk.")
        self.assertEqual(self.provider.call_count, 2)

    def test_distinct_tabs_same_session_same_doi_keep_both_success_results(self):
        first, second = self.fetch(self.event), self.fetch(self.other)
        results = self.race([lambda c: c.post(first, self.submitted(0)), lambda c: c.post(second, self.submitted(1))])
        self.assertEqual([r.status_code for r in results], [302, 302])
        self.assertEqual(Resource.objects.count(), 1)
        self.assertEqual(EventResource.objects.count(), 2)
        states = Session.objects.get(session_key=self.key).get_decoded()[PREVIEW_KEY]
        self.assertEqual([s["status"] for s in states.values()], ["saved", "saved"])
        for event, index in ((self.event, 0), (self.other, 1)):
            link = EventResource.objects.get(event=event)
            self.assertEqual((link.recommendation, link.display_order), (f"Winner reason {index}", index))

    def test_independent_sessions_different_targets_recover_real_doi_insert_conflict(self):
        another = Client()
        another.force_login(self.user)
        key = another.session.session_key
        first, second = self.fetch(self.event), self.fetch(self.other, another)
        conflicts = []
        from events.services import resource_save
        actual = resource_save._is_identity_conflict
        def classify(error, model):
            conflicts.append(getattr(error.__cause__, "sqlstate", None))
            return actual(error, model)
        with patch("events.services.resource_save._is_identity_conflict", side_effect=classify):
            results = self.race([lambda c: c.post(first, self.submitted(0)), lambda c: c.post(second, self.submitted(1))],
                                [self.key, key], insertion=True)
        self.assertEqual([r.status_code for r in results], [302, 302])
        self.assertEqual(conflicts, ["23505"])
        self.assertEqual((Resource.objects.count(), EventResource.objects.count()), (1, 2))
        for session_key in (self.key, key):
            states = Session.objects.get(session_key=session_key).get_decoded()[PREVIEW_KEY]
            self.assertEqual(next(iter(states.values()))["status"], "saved")

    def test_cancel_racing_confirmation_has_one_terminal_state(self):
        url = self.fetch(self.event)
        results = self.race([lambda c: c.post(url, self.submitted(0)), lambda c: c.post(url, {"action": "cancel"})])
        self.assertEqual(sorted(r.status_code for r in results), [302, 400])
        state = next(iter(Session.objects.get(session_key=self.key).get_decoded()[PREVIEW_KEY].values()))
        if state["status"] == "cancelled":
            self.assertEqual((Resource.objects.count(), EventResource.objects.count()), (0, 0))
            self.assertEqual(self.client.post(url, self.submitted(1)).status_code, 400)
        else:
            self.assertEqual(state["status"], "saved")
            self.assertEqual((Resource.objects.count(), EventResource.objects.count()), (1, 1))
            self.assertEqual(self.client.post(url, self.submitted(1)).status_code, 302)
