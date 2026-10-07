"""Step 07 acceptance: independent reading links and PostgreSQL integrity."""

from datetime import datetime, timezone

from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from events.models import Event, EventResource, Resource


class EventResourceTests(TestCase):
    def setUp(self):
        starts_at = datetime(2026, 11, 3, 19, 30, tzinfo=timezone.utc)
        self.event = Event.objects.create(title="Memory talk", starts_at=starts_at)
        self.other_event = Event.objects.create(title="Attention talk", starts_at=starts_at)
        self.resource = Resource.objects.create(
            title="Reading fixture", original_url="https://example.org/reading"
        )

    def create_resource(self, label):
        return Resource.objects.create(
            title=label, original_url="https://example.org/reading"
        )

    def test_complete_link_round_trips_with_separate_integer_identity(self):
        link = EventResource.objects.create(
            event=self.event,
            resource=self.resource,
            recommendation="Connect this reading to the talk's examples.",
            display_order=-3,
        )
        link.refresh_from_db()
        self.assertIsInstance(link.pk, int)
        self.assertEqual(link.event_id, self.event.pk)
        self.assertEqual(link.resource_id, self.resource.pk)
        self.assertEqual(link.recommendation, "Connect this reading to the talk's examples.")
        self.assertEqual(link.display_order, -3)
        self.assertEqual(str(link), f"{self.event} — {self.resource}")
        self.assertEqual(self.event.event_resources.get().pk, link.pk)
        self.assertEqual(self.resource.event_resources.get().pk, link.pk)

    def test_minimal_link_defaults_to_empty_recommendation_and_zero_order(self):
        link = EventResource.objects.create(event=self.event, resource=self.resource)
        link.refresh_from_db()
        self.assertEqual(link.recommendation, "")
        self.assertEqual(link.display_order, 0)
        self.assertIsInstance(link.display_order, int)

    def test_shared_resource_has_independent_recommendations_and_orders(self):
        first = EventResource.objects.create(
            event=self.event, resource=self.resource, recommendation="For memory.", display_order=1
        )
        second = EventResource.objects.create(
            event=self.other_event, resource=self.resource,
            recommendation="For attention.", display_order=8,
        )
        first.recommendation = "Revised memory reading."
        first.display_order = -2
        first.save(update_fields=["recommendation", "display_order"])
        first.refresh_from_db()
        second.refresh_from_db()
        self.resource.refresh_from_db()
        self.assertEqual((first.recommendation, first.display_order), ("Revised memory reading.", -2))
        self.assertEqual((second.recommendation, second.display_order), ("For attention.", 8))
        self.assertEqual(self.resource.title, "Reading fixture")
        self.assertEqual(Resource.objects.count(), 1)
        self.assertEqual(self.resource.event_resources.count(), 2)

    def test_duplicate_pair_is_rejected_by_normal_save_without_overwriting(self):
        original = EventResource.objects.create(
            event=self.event, resource=self.resource, recommendation="Keep this.", display_order=4
        )
        with self.assertRaises(ValidationError):
            EventResource.objects.create(
                event=self.event, resource=self.resource,
                recommendation="Do not replace.", display_order=-10,
            )
        original.refresh_from_db()
        self.assertEqual((original.recommendation, original.display_order), ("Keep this.", 4))
        self.assertEqual(EventResource.objects.count(), 1)

    def test_database_rejects_duplicate_insert_and_update_that_bypass_validation(self):
        original = EventResource.objects.create(event=self.event, resource=self.resource)
        with self.assertRaises(IntegrityError), transaction.atomic():
            EventResource.objects.bulk_create([
                EventResource(event=self.event, resource=self.resource)
            ])
        other = EventResource.objects.create(event=self.other_event, resource=self.resource)
        with self.assertRaises(IntegrityError), transaction.atomic():
            EventResource.objects.filter(pk=other.pk).update(event_id=self.event.pk)
        other.refresh_from_db()
        self.assertEqual(other.event_id, self.other_event.pk)
        self.assertEqual(EventResource.objects.count(), 2)
        self.assertTrue(EventResource.objects.filter(pk=original.pk).exists())

    def test_different_orders_sort_ascending_including_negative_values(self):
        links = []
        for index, order in enumerate((10, 0, -5, 2)):
            links.append(EventResource.objects.create(
                event=self.event, resource=self.create_resource(f"Reading {index}"),
                display_order=order,
            ))
        expected = [links[index].pk for index in (2, 1, 3, 0)]
        for _ in range(2):
            self.assertEqual(
                list(self.event.event_resources.values_list("pk", flat=True)), expected
            )

    def test_equal_orders_use_association_id_and_remain_stable_after_edits(self):
        resources = [self.create_resource(f"Reading {index}") for index in range(3)]
        # Reverse resource IDs so ordering by resource ID would give the wrong result.
        links = [EventResource.objects.create(event=self.event, resource=resource)
                 for resource in reversed(resources)]
        EventResource.objects.create(
            event=self.other_event, resource=self.resource, display_order=-20
        )
        expected = [link.pk for link in links]
        self.assertEqual(list(self.event.event_resources.values_list("pk", flat=True)), expected)
        links[0].display_order = 4
        links[0].save(update_fields=["display_order"])
        self.assertEqual(
            list(self.event.event_resources.values_list("pk", flat=True)),
            [links[1].pk, links[2].pk, links[0].pk],
        )
        links[0].display_order = 0
        links[0].save(update_fields=["display_order"])
        self.assertEqual(list(self.event.event_resources.values_list("pk", flat=True)), expected)

    def test_invalid_required_relations_order_and_null_recommendation_are_rejected(self):
        missing_event_id = max(self.event.pk, self.other_event.pk) + 1000
        missing_resource_id = self.resource.pk + 1000
        for field, value in (
            ("event_id", None), ("resource_id", None),
            ("event_id", missing_event_id), ("resource_id", missing_resource_id),
            ("display_order", None), ("display_order", "not-an-integer"),
            ("display_order", -2147483649), ("display_order", 2147483648),
            ("recommendation", None),
        ):
            with self.subTest(field=field, value=value):
                values = {"event_id": self.event.pk, "resource_id": self.resource.pk}
                values[field] = value
                with self.assertRaises(ValidationError) as error:
                    EventResource.objects.create(**values)
                self.assertIn(field.removesuffix("_id"), error.exception.message_dict)
        self.assertEqual(EventResource.objects.count(), 0)

    def test_database_rejects_nulls_and_missing_foreign_keys(self):
        link = EventResource.objects.create(event=self.event, resource=self.resource)
        for values in (
            {"event_id": None}, {"resource_id": None},
            {"recommendation": None}, {"display_order": None},
            {"event_id": max(self.event.pk, self.other_event.pk) + 1000},
            {"resource_id": self.resource.pk + 1000},
        ):
            with self.subTest(values=values):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    EventResource.objects.filter(pk=link.pk).update(**values)
                    # PostgreSQL foreign keys are deferred; check before savepoint exit.
                    connection.check_constraints(table_names=[EventResource._meta.db_table])
        link.refresh_from_db()
        self.assertEqual(link.event_id, self.event.pk)
        self.assertEqual(link.resource_id, self.resource.pk)
        self.assertEqual((link.recommendation, link.display_order), ("", 0))

    def test_removing_link_keeps_both_events_resource_and_other_link(self):
        first = EventResource.objects.create(event=self.event, resource=self.resource)
        other = EventResource.objects.create(event=self.other_event, resource=self.resource)
        first.delete()
        self.assertEqual(Event.objects.count(), 2)
        self.assertEqual(Resource.objects.count(), 1)
        self.assertEqual(list(EventResource.objects.values_list("pk", flat=True)), [other.pk])

    def test_single_and_queryset_event_deletion_remove_only_their_links(self):
        surviving = EventResource.objects.create(event=self.other_event, resource=self.resource)
        starts_at = self.event.starts_at
        for bulk in (False, True):
            with self.subTest(bulk=bulk):
                event = Event.objects.create(title="Temporary talk", starts_at=starts_at)
                private_reading = self.create_resource("Reading only linked here")
                EventResource.objects.create(event=event, resource=self.resource)
                EventResource.objects.create(event=event, resource=private_reading)
                event_id = event.pk
                if bulk:
                    Event.objects.filter(pk=event_id).delete()
                else:
                    event.delete()
                self.assertFalse(Event.objects.filter(pk=event_id).exists())
                self.assertFalse(EventResource.objects.filter(event_id=event_id).exists())
                self.assertTrue(Resource.objects.filter(pk=private_reading.pk).exists())
                self.assertTrue(Resource.objects.filter(pk=self.resource.pk).exists())
                self.assertTrue(EventResource.objects.filter(pk=surviving.pk).exists())

    def test_linked_resource_is_protected_from_single_and_queryset_deletion(self):
        link = EventResource.objects.create(event=self.event, resource=self.resource)
        with self.assertRaises(ProtectedError):
            self.resource.delete()
        with self.assertRaises(ProtectedError):
            Resource.objects.filter(pk=self.resource.pk).delete()
        self.assertTrue(Resource.objects.filter(pk=self.resource.pk).exists())
        self.assertTrue(EventResource.objects.filter(pk=link.pk).exists())
        # This is FK protection, not the global Admin deletion policy from step 08.

    def test_link_migration_is_applied_in_the_isolated_postgresql_database(self):
        self.assertEqual(connection.vendor, "postgresql")
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM django_migrations WHERE app = %s", ["events"])
            migration_names = {row[0] for row in cursor.fetchall()}
        self.assertTrue({"0001_initial", "0002_resource", "0003_event_resource"} <= migration_names)
        self.assertIn("events_eventresource", connection.introspection.table_names())
