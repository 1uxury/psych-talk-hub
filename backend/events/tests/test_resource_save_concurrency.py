"""Step 23: real PostgreSQL races, rollback recovery and error boundaries."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Barrier, Event as ThreadEvent, local
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.db import IntegrityError, OperationalError, connection, connections, models, transaction
from django.db.models.query import QuerySet
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from events.models import Event, EventResource, Resource
from events.services import resource_save
from events.tests.test_resource_save import bibliography_fixture


class DoiSaveConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.assertEqual(connection.vendor, "postgresql")
        self.events = [Event.objects.create(title=f"Race talk {i}", starts_at=timezone.now())
                       for i in range(2)]
        self.http = patch("requests.sessions.Session.request", side_effect=AssertionError("No HTTP during save."))
        request = self.http.start()
        self.addCleanup(self.http.stop)
        self.addCleanup(request.assert_not_called)

    def race(self, *, doi, event_ids, model, at_insert, outer_failure=False, two_conflicts=False):
        """Coordinate both workers after the missing read, before validation/INSERT.

        INSERT coordination runs after real full_clean and forces the database
        race. Validation coordination lets worker 0 commit before worker 1's
        real full_clean. No uniqueness or database exception is mocked.
        """
        barrier = Barrier(2, timeout=10)
        committed = ThreadEvent()
        resource_conflict = ThreadEvent()
        second_committed = ThreadEvent()
        association_barrier = Barrier(2, timeout=10)
        identity = local()
        conflicts = []
        original_save = model.save
        original_classify = resource_save._is_identity_conflict

        def classify(error, saving_model):
            # Called after the service atomic/savepoint has rolled back.
            self.assertFalse(connection.needs_rollback)
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                self.assertEqual(cursor.fetchone(), (1,))
            conflicts.append(error)
            if two_conflicts and saving_model is Resource:
                resource_conflict.set()
            return original_classify(error, saving_model)

        def save_after_winner(instance, *args, **kwargs):
            if not getattr(identity, "passed", False):
                identity.passed = True
                barrier.wait()
                if identity.index == 1:
                    if not committed.wait(10):
                        raise AssertionError("Winner did not commit.")
            return original_save(instance, *args, **kwargs)

        def gate_insert(execute, sql, params, many, context):
            if (two_conflicts and sql.startswith('INSERT INTO "events_eventresource"')
                    and identity.index in (1, 2) and not getattr(identity, "linked", False)):
                identity.linked = True
                association_barrier.wait()
                if identity.index == 1 and not second_committed.wait(10):
                    raise AssertionError("Second winner did not commit.")
            if (sql.startswith(f'INSERT INTO "{model._meta.db_table}"')
                    and not getattr(identity, "passed", False)):
                identity.passed = True
                barrier.wait()
            return execute(sql, params, many, context)

        def worker(index):
            # Django connections are thread-local: each worker opens/closes its own.
            db = connections["default"]
            db.close()
            identity.index = index
            try:
                with db.cursor() as cursor:
                    cursor.execute("SET statement_timeout = '12s'")
                    cursor.execute("SET lock_timeout = '10s'")
                    cursor.execute("SELECT pg_backend_pid(), current_database()")
                    pid, database = cursor.fetchone()
                fields = {**bibliography_fixture(), "title": f"Candidate {index}"}
                submitted = deepcopy(fields)
                kwargs = dict(event_id=event_ids[index], doi=doi, bibliography=fields,
                              recommendation=f"Reason {index}", display_order=index - 5)
                if two_conflicts and index == 2 and not resource_conflict.wait(10):
                    raise AssertionError("First conflict did not roll back.")
                with db.execute_wrapper(gate_insert):
                    if outer_failure and index == 1:
                        try:
                            with transaction.atomic():
                                result = resource_save.save_doi_to_event(**kwargs)
                                raise RuntimeError("Caller result write failed")
                        except RuntimeError as error:
                            self.assertEqual(str(error), "Caller result write failed")
                    else:
                        result = resource_save.save_doi_to_event(**kwargs)
                if index == 0:
                    committed.set()
                if index == 2:
                    second_committed.set()
                self.assertEqual(fields, submitted)
                self.assertFalse(db.needs_rollback)
                self.assertFalse(db.in_atomic_block)
                self.assertTrue(db.get_autocommit())
                # A fresh query on the SAME worker connection must work.
                visible = Resource.objects.get(doi=doi)
                self.assertEqual(visible.pk, result.resource.pk)
                return index, result, pid, database
            finally:
                db.close()

        save_patch = patch.object(model, "save", original_save if at_insert else save_after_winner)
        with save_patch, patch.object(resource_save, "_is_identity_conflict", classify):
            with ThreadPoolExecutor(max_workers=len(event_ids)) as executor:
                futures = [executor.submit(worker, i) for i in range(len(event_ids))]
                outputs = [future.result(timeout=25) for future in futures]
        self.assertEqual(len({out[2] for out in outputs}), len(event_ids))
        self.assertEqual([out[3] for out in outputs], [connection.settings_dict["NAME"]] * len(event_ids))
        self.assertTrue(outputs[0][3].startswith("test_"))
        self.assertEqual(len(conflicts), 2 if two_conflicts else 1)
        error = conflicts[0]
        if at_insert:
            self.assertIsInstance(error, IntegrityError)
            self.assertEqual(error.__cause__.sqlstate, "23505")
            expected = "events_resource_doi_key" if model is Resource else "unique_event_resource"
            self.assertEqual(error.__cause__.diag.constraint_name, expected)
        else:
            self.assertIsInstance(error, ValidationError)
        if two_conflicts:
            self.assertIsInstance(conflicts[1], IntegrityError)
            self.assertEqual(conflicts[1].__cause__.sqlstate, "23505")
            self.assertEqual(conflicts[1].__cause__.diag.constraint_name, "unique_event_resource")
        return [out[1] for out in outputs]

    def assert_same_link(self, results, doi, existing_resource=None):
        resource = Resource.objects.get(doi=doi)
        link = EventResource.objects.get(resource=resource)
        self.assertEqual([r.resource.pk for r in results], [resource.pk] * 2)
        self.assertEqual([r.association.pk for r in results], [link.pk] * 2)
        self.assertEqual(sum(r.resource_created for r in results), 0 if existing_resource else 1)
        self.assertEqual(sum(r.association_created for r in results), 1)
        winner = next(i for i, result in enumerate(results) if result.association_created)
        self.assertEqual((link.recommendation, link.display_order), (f"Reason {winner}", winner - 5))
        for result in results:
            self.assertEqual((result.association.recommendation, result.association.display_order),
                             (link.recommendation, link.display_order))
            self.assertEqual(result.resource.title, resource.title)
        if existing_resource:
            self.assertEqual(Resource.objects.filter(pk=resource.pk).values().get(), existing_resource)
        else:
            self.assertEqual(resource.title, f"Candidate {winner}")

    def test_simultaneous_new_doi_same_talk_recovers_actual_doi_unique_conflict(self):
        for round_number in range(3):
            doi = f"10.1234/race-same-{round_number}"
            with self.subTest(round=round_number):
                results = self.race(doi=doi, event_ids=[self.events[0].pk] * 2,
                                    model=Resource, at_insert=True)
                self.assert_same_link(results, doi)
        self.assertEqual((Resource.objects.count(), EventResource.objects.count()), (3, 3))

    def test_simultaneous_new_doi_two_talks_creates_one_resource_and_two_links(self):
        for round_number in range(3):
            doi = f"10.1234/race-different-{round_number}"
            with self.subTest(round=round_number):
                results = self.race(doi=doi, event_ids=[event.pk for event in self.events],
                                    model=Resource, at_insert=True)
                resource = Resource.objects.get(doi=doi)
                self.assertEqual(sum(r.resource_created for r in results), 1)
                winner = next(i for i, result in enumerate(results) if result.resource_created)
                self.assertEqual(resource.title, f"Candidate {winner}")
                self.assertEqual(EventResource.objects.filter(resource=resource).count(), 2)
                self.assertNotEqual(results[0].association.pk, results[1].association.pk)
                for i, result in enumerate(results):
                    self.assertTrue(result.association_created)
                    self.assertEqual(result.resource.pk, resource.pk)
                    self.assertEqual(result.resource.title, resource.title)
                    self.assertEqual((result.association.event_id, result.association.recommendation,
                                      result.association.display_order), (self.events[i].pk, f"Reason {i}", i - 5))
        self.assertEqual((Resource.objects.count(), EventResource.objects.count()), (3, 6))

    def test_simultaneous_existing_doi_same_talk_recovers_actual_pair_unique_conflict(self):
        for round_number in range(3):
            doi = f"10.1234/race-existing-{round_number}"
            Resource.objects.create(doi=doi, title="Current edited bibliography", authors="", year=None,
                                    original_url="http://example.org/current", metadata_source="manual",
                                    seed_key=f"preserve-race-{round_number}")
            before = Resource.objects.filter(doi=doi).values().get()
            with self.subTest(round=round_number):
                results = self.race(doi=doi, event_ids=[self.events[0].pk] * 2,
                                    model=EventResource, at_insert=True)
                self.assert_same_link(results, doi, before)
        self.assertEqual((Resource.objects.count(), EventResource.objects.count()), (3, 3))

    def test_resource_full_clean_race_returns_committed_current_data(self):
        doi = "10.1234/validation-resource-race"
        results = self.race(doi=doi, event_ids=[self.events[0].pk] * 2,
                            model=Resource, at_insert=False)
        self.assert_same_link(results, doi)

    def test_association_full_clean_race_returns_committed_current_link(self):
        doi = "10.1234/validation-link-race"
        Resource.objects.create(doi=doi, **bibliography_fixture())
        before = Resource.objects.values().get()
        results = self.race(doi=doi, event_ids=[self.events[0].pk] * 2,
                            model=EventResource, at_insert=False)
        self.assert_same_link(results, doi, before)

    def test_recovery_inside_caller_transaction_still_rolls_back_later_failure(self):
        doi = "10.1234/outer-rollback-race"
        results = self.race(doi=doi, event_ids=[event.pk for event in self.events],
                            model=Resource, at_insert=False, outer_failure=True)
        self.assertEqual((Resource.objects.count(), EventResource.objects.count()), (1, 1))
        self.assertTrue(results[0].resource_created)
        self.assertFalse(results[1].resource_created)
        self.assertTrue(results[1].association_created)
        self.assertFalse(EventResource.objects.filter(event=self.events[1]).exists())

    def test_one_request_recovers_doi_then_association_race_in_three_attempts(self):
        results = self.race(doi="10.1234/two-stage-race",
                            event_ids=[self.events[0].pk, self.events[1].pk, self.events[1].pk],
                            model=Resource, at_insert=False, two_conflicts=True)
        self.assertEqual((Resource.objects.count(), EventResource.objects.count()), (1, 2))
        self.assertEqual(sum(r.resource_created for r in results), 1)
        self.assertEqual(sum(r.association_created for r in results), 2)
        self.assertEqual(results[1].association.pk, results[2].association.pk)
        self.assertFalse(results[1].association_created)
        self.assertEqual((results[1].association.recommendation, results[1].association.display_order),
                         ("Reason 2", -3))
        self.assertEqual([r.resource.title for r in results], ["Candidate 0"] * 3)


class DoiSaveConflictBoundaryTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(title="Boundary talk", starts_at=timezone.now())
        self.doi = "10.1234/boundary-race"
        self.fields = bibliography_fixture()
        self.http = patch("requests.sessions.Session.request", side_effect=AssertionError("No HTTP during save."))
        request = self.http.start()
        self.addCleanup(self.http.stop)
        self.addCleanup(request.assert_not_called)

    def save(self):
        return resource_save.save_doi_to_event(event_id=self.event.pk, doi=self.doi, bibliography=self.fields)

    def snapshot(self):
        return [list(model.objects.order_by("pk").values()) for model in (Event, Resource, EventResource)]

    def assert_database_failure(self, model, save, sqlstate, constraint=None):
        before = self.snapshot()
        with patch.object(model, "save", autospec=True, side_effect=save) as saving:
            with self.assertRaises(IntegrityError) as caught:
                self.save()
        self.assertEqual(saving.call_count, 1)
        self.assertEqual(caught.exception.__cause__.sqlstate, sqlstate)
        if constraint:
            self.assertEqual(caught.exception.__cause__.diag.constraint_name, constraint)
        self.assertFalse(connection.needs_rollback)
        self.assertEqual(self.snapshot(), before)
        self.assertTrue(self.save().association_created)

    def test_other_resource_unique_constraint_is_not_recovered(self):
        Resource.objects.create(seed_key="occupied", **self.fields)

        def fail(resource):
            resource.seed_key = "occupied"
            models.Model.save(resource)

        self.assert_database_failure(Resource, fail, "23505", "events_resource_seed_key_key")

    def test_association_primary_key_conflict_is_not_recovered(self):
        old_resource = Resource.objects.create(**self.fields)
        old_link = EventResource.objects.create(event=self.event, resource=old_resource)

        def fail(link):
            link.pk = old_link.pk
            models.Model.save(link, force_insert=True)

        self.assert_database_failure(EventResource, fail, "23505", "events_eventresource_pkey")

    def test_resource_check_constraint_is_not_recovered(self):
        def fail(resource):
            resource.year = 10000
            models.Model.save(resource)

        self.assert_database_failure(Resource, fail, "23514", "resource_year_in_range")

    def test_operational_database_error_propagates_without_retry(self):
        error = OperationalError("Synthetic connection failure")
        before = self.snapshot()
        with patch.object(Resource, "save", side_effect=error) as saving:
            with self.assertRaises(OperationalError) as caught:
                self.save()
        self.assertIs(caught.exception, error)
        saving.assert_called_once()
        self.assertFalse(connection.needs_rollback)
        self.assertEqual(self.snapshot(), before)
        self.assertTrue(self.save().resource_created)

    def test_uniqueness_and_invalid_bibliography_are_not_swallowed_together(self):
        original_save = Resource.save
        before = self.snapshot()

        def fail(resource):
            # Winner is visible to full_clean; an independent field is also invalid.
            original_save(Resource(doi=self.doi, **self.fields))
            resource.title = ""
            original_save(resource)

        with patch.object(Resource, "save", autospec=True, side_effect=fail) as saving:
            with self.assertRaises(ValidationError) as caught:
                self.save()
        self.assertEqual(set(caught.exception.error_dict), {"title", "doi"})
        saving.assert_called_once()
        self.assertFalse(connection.needs_rollback)
        self.assertEqual(self.snapshot(), before)

    def test_unique_looking_error_without_a_saved_winner_is_not_recovered(self):
        candidate = Resource(doi=self.doi, **self.fields)
        error = ValidationError({"doi": candidate.unique_error_message(Resource, ("doi",))})
        before = self.snapshot()
        with patch.object(Resource, "save", side_effect=error) as saving:
            with self.assertRaises(ValidationError) as caught:
                self.save()
        self.assertIs(caught.exception, error)
        saving.assert_called_once()
        self.assertEqual(self.snapshot(), before)

    def test_persistent_same_identity_conflict_stops_after_one_recovery(self):
        Resource.objects.create(doi=self.doi, **self.fields)
        before = self.snapshot()
        original_first = QuerySet.first
        original_save = Resource.save

        def stale_lookup(queryset):
            # Simulate a repeatedly stale read; full_clean still sees the real winner.
            return None if queryset.model is Resource else original_first(queryset)

        with patch.object(QuerySet, "first", stale_lookup):
            with patch.object(Resource, "save", autospec=True, side_effect=original_save) as saving:
                with self.assertRaises(ValidationError):
                    self.save()
        self.assertEqual(saving.call_count, 2)
        self.assertFalse(connection.needs_rollback)
        self.assertEqual(self.snapshot(), before)
