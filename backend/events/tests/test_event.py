"""Step 05 acceptance: Event validation and PostgreSQL persistence."""

from datetime import datetime, timezone as datetime_timezone
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.test import TestCase

from events.models import Event


class EventTests(TestCase):
    def setUp(self):
        self.starts_at = datetime(2026, 11, 3, 19, 30, tzinfo=datetime_timezone.utc)

    def test_complete_event_round_trips(self):
        event = Event.objects.create(
            title="Learning and memory",
            description="An example psychology talk.",
            topic="Memory",
            starts_at=self.starts_at,
            speaker="Example speaker",
            is_example=True,
            seed_key="learning-and-memory",
        )
        stored = Event.objects.get(pk=event.pk)
        self.assertIsInstance(stored.pk, int)
        self.assertEqual(stored.title, "Learning and memory")
        self.assertEqual(stored.description, "An example psychology talk.")
        self.assertEqual(stored.topic, "Memory")
        self.assertEqual(stored.starts_at, self.starts_at)
        self.assertEqual(stored.speaker, "Example speaker")
        self.assertTrue(stored.is_example)
        self.assertEqual(stored.seed_key, "learning-and-memory")
        self.assertEqual(str(stored), stored.title)

    def test_minimal_event_defaults_to_empty_text_non_example_and_null_seed_key(self):
        event = Event.objects.create(title="A talk", starts_at=self.starts_at)
        event.refresh_from_db()
        self.assertEqual((event.description, event.topic, event.speaker), ("", "", ""))
        self.assertFalse(event.is_example)
        self.assertIsNone(event.seed_key)
        explicit = Event.objects.create(
            title="Another talk", starts_at=self.starts_at, description="", topic="", speaker=""
        )
        explicit.refresh_from_db()
        self.assertEqual((explicit.description, explicit.topic, explicit.speaker), ("", "", ""))

    def test_blank_titles_are_rejected_without_creating_records(self):
        for title in ("", " ", "\t\r\n", "\u3000"):
            with self.subTest(title=repr(title)):
                with self.assertRaises(ValidationError) as error:
                    Event.objects.create(title=title, starts_at=self.starts_at)
                self.assertIn("title", error.exception.message_dict)
        self.assertEqual(Event.objects.count(), 0)

    def test_missing_or_naive_start_time_is_rejected(self):
        for starts_at in (None, datetime(2026, 11, 3, 19, 30)):
            with self.subTest(starts_at=starts_at):
                with self.assertRaises(ValidationError) as error:
                    Event.objects.create(title="A talk", starts_at=starts_at)
                self.assertIn("starts_at", error.exception.message_dict)
        self.assertEqual(Event.objects.count(), 0)

    def test_unused_seed_keys_are_null_and_do_not_conflict(self):
        for seed_key in (None, "", " \t "):
            with self.subTest(seed_key=seed_key):
                event = Event.objects.create(
                    title="An ordinary talk", starts_at=self.starts_at, seed_key=seed_key
                )
                event.refresh_from_db()
                self.assertIsNone(event.seed_key)
        self.assertEqual(Event.objects.count(), 3)

    def test_duplicate_seed_key_fails_validation_and_database_constraint(self):
        event = Event.objects.create(
            title="First talk", starts_at=self.starts_at, seed_key="demo-upcoming"
        )
        with self.assertRaises(ValidationError) as error:
            Event.objects.create(
                title="Second talk", starts_at=self.starts_at, seed_key=" demo-upcoming "
            )
        self.assertIn("seed_key", error.exception.message_dict)
        other = Event.objects.create(title="Another talk", starts_at=self.starts_at)
        # QuerySet.update bypasses model validation: the database must still refuse duplicates.
        with self.assertRaises(IntegrityError), transaction.atomic():
            Event.objects.filter(pk=other.pk).update(seed_key=event.seed_key)
        other.refresh_from_db()
        self.assertIsNone(other.seed_key)
        self.assertEqual(Event.objects.count(), 2)

    def test_database_rejects_blank_titles_missing_time_and_blank_seed_keys(self):
        event = Event.objects.create(title="Keep this talk", starts_at=self.starts_at)
        for values in ({"title": ""}, {"title": " \t\n"}, {"starts_at": None}, {"seed_key": " "}):
            with self.subTest(values=values):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Event.objects.filter(pk=event.pk).update(**values)
        event.refresh_from_db()
        self.assertEqual(event.title, "Keep this talk")
        self.assertEqual(event.starts_at, self.starts_at)
        self.assertIsNone(event.seed_key)

    def test_london_winter_and_summer_times_return_same_instant_in_utc(self):
        for month, utc_hour in ((1, 19), (7, 18)):
            with self.subTest(month=month):
                local_time = datetime(2026, month, 15, 19, 30, tzinfo=ZoneInfo("Europe/London"))
                event = Event.objects.create(title="A London talk", starts_at=local_time)
                event.refresh_from_db()
                expected = datetime(2026, month, 15, utc_hour, 30, tzinfo=datetime_timezone.utc)
                self.assertEqual(event.starts_at, local_time)
                self.assertEqual(event.starts_at, expected)
                self.assertEqual(event.starts_at.utcoffset().total_seconds(), 0)

    def test_initial_event_migration_is_applied_in_the_isolated_postgresql_database(self):
        self.assertEqual(connection.vendor, "postgresql")
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM django_migrations WHERE app = %s", ["events"]
            )
            migration_names = {row[0] for row in cursor.fetchall()}
        self.assertIn("0001_initial", migration_names)
        self.assertIn("events_event", connection.introspection.table_names())
