"""Step 22: isolated PostgreSQL save/reuse/rollback, without concurrency or HTTP."""

from copy import deepcopy
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, models, transaction
from django.test import TestCase
from django.utils import timezone

from events.models import Event, EventResource, Resource
from events.services.resource_save import save_doi_to_event


DOI = "10.1234/save-fixture"


def bibliography_fixture():
    return {
        "title": "Synthetic reviewed reading",
        "authors": "Fixture Author; Fixture Organisation",
        "year": 2024,
        "original_url": "https://example.org/reviewed?edition=1#reading",
        "resource_type": "research_paper",
    }


class DoiSaveTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(title="Fixture talk A", starts_at=timezone.now())
        self.other_event = Event.objects.create(title="Fixture talk B", starts_at=timezone.now())
        self.bibliography = bibliography_fixture()
        self.http = patch("requests.sessions.Session.request", side_effect=AssertionError("No HTTP during save."))
        self.request = self.http.start()
        self.addCleanup(self.http.stop)
        self.addCleanup(self.request.assert_not_called)

    def save(self, **overrides):
        values = {
            "event_id": self.event.pk, "doi": DOI, "bibliography": self.bibliography,
            "recommendation": "Reading for A", "display_order": -3,
        }
        values.update(overrides)
        return save_doi_to_event(**values)

    def snapshot(self):
        return {
            "events": list(Event.objects.order_by("pk").values()),
            "resources": list(Resource.objects.order_by("pk").values()),
            "associations": list(EventResource.objects.order_by("pk").values()),
        }

    def test_new_doi_creates_one_resource_and_link_with_reviewed_fields_only(self):
        self.bibliography.update({
            "doi": "10.9999/untrusted", "metadata_source": "manual", "seed_key": "untrusted",
            "id": 999, "abstract": "Do not import", "recommendation": "Wrong place",
        })
        submitted = deepcopy(self.bibliography)
        result = self.save(doi=" \tHTTPS://DOI.ORG/10.1234/SAVE-FIXTURE \n")
        self.assertTrue(result.resource_created)
        self.assertTrue(result.association_created)
        self.assertEqual(Resource.objects.count(), 1)
        self.assertEqual(EventResource.objects.count(), 1)
        resource = Resource.objects.get()
        for field, value in bibliography_fixture().items():
            self.assertEqual(getattr(resource, field), value)
        self.assertEqual(resource.doi, DOI)
        self.assertEqual(resource.metadata_source, "crossref")
        self.assertIsNone(resource.seed_key)
        link = EventResource.objects.get()
        self.assertEqual((link.event_id, link.resource_id), (self.event.pk, resource.pk))
        self.assertEqual((link.recommendation, link.display_order), ("Reading for A", -3))
        self.assertEqual((result.resource.pk, result.association.pk), (resource.pk, link.pk))
        self.assertEqual(self.bibliography, submitted)

    def test_another_talk_creates_only_link_and_preserves_all_existing_fields(self):
        first = self.save()
        before = self.snapshot()
        result = self.save(event_id=self.other_event.pk, recommendation="Reading for B", display_order=8)
        self.assertFalse(result.resource_created)
        self.assertTrue(result.association_created)
        self.assertEqual(result.resource.pk, first.resource.pk)
        self.assertEqual(Resource.objects.count(), 1)
        self.assertEqual(EventResource.objects.count(), 2)
        after = self.snapshot()
        self.assertEqual(after["events"], before["events"])
        self.assertEqual(after["resources"], before["resources"])
        self.assertEqual(after["associations"][0], before["associations"][0])
        self.assertEqual((result.association.recommendation, result.association.display_order), ("Reading for B", 8))

    def test_duplicate_call_ignores_changed_bibliography_reason_and_order(self):
        first = self.save()
        before = self.snapshot()
        result = self.save(bibliography={"title": "Replacement", "original_url": "invalid"},
                           recommendation="Replacement reason", display_order=123)
        self.assertFalse(result.resource_created)
        self.assertFalse(result.association_created)
        self.assertEqual((result.resource.pk, result.association.pk), (first.resource.pk, first.association.pk))
        self.assertEqual((result.association.recommendation, result.association.display_order), ("Reading for A", -3))
        self.assertEqual(self.snapshot(), before)

    def test_repeat_call_returns_current_edited_association_even_with_invalid_new_values(self):
        first = self.save()
        first.association.recommendation = ""
        first.association.display_order = -10
        first.association.save()
        before = self.snapshot()
        result = self.save(recommendation=None, display_order="invalid")
        self.assertFalse(result.association_created)
        self.assertEqual((result.association.recommendation, result.association.display_order), ("", -10))
        self.assertEqual(self.snapshot(), before)

    def test_resource_created_after_preview_is_reused_even_with_incomplete_preview(self):
        preview = {"title": "", "original_url": ""}
        resource = Resource.objects.create(
            doi=DOI, title="Saved after preview", authors="", year=None,
            original_url="http://example.org/current", resource_type="article",
            metadata_source="manual", seed_key="preserve-current-identity",
        )
        before = self.snapshot()
        result = self.save(bibliography=preview)
        self.assertFalse(result.resource_created)
        self.assertTrue(result.association_created)
        self.assertEqual(result.resource.pk, resource.pk)
        self.assertEqual(result.resource.title, "Saved after preview")
        self.assertEqual(self.snapshot()["resources"], before["resources"])
        self.assertEqual(preview, {"title": "", "original_url": ""})

    def test_resource_edited_after_preview_uses_database_bibliography_and_cleared_values(self):
        first = self.save()
        preview = deepcopy(self.bibliography)
        resource = first.resource
        resource.title = "Current edited title"
        resource.authors = ""
        resource.year = None
        resource.original_url = "http://example.org/edited"
        resource.resource_type = "article"
        resource.seed_key = "keep-seed"
        resource.save()
        before = self.snapshot()
        result = self.save(event_id=self.other_event.pk, bibliography=preview)
        self.assertFalse(result.resource_created)
        self.assertEqual(result.resource.title, "Current edited title")
        self.assertEqual((result.resource.authors, result.resource.year), ("", None))
        after = self.snapshot()
        self.assertEqual(after["resources"], before["resources"])
        self.assertEqual(after["events"], before["events"])
        self.assertEqual(after["associations"][0], before["associations"][0])

    def test_saved_doi_needs_no_preview_fields_and_new_optional_fields_use_defaults(self):
        minimal = {"title": "Minimal reading", "original_url": "https://example.org/minimal"}
        first = save_doi_to_event(event_id=self.event.pk, doi=DOI, bibliography=minimal)
        self.assertEqual((first.resource.authors, first.resource.year), ("", None))
        self.assertEqual(first.resource.resource_type, "article")
        self.assertEqual((first.association.recommendation, first.association.display_order), ("", 0))
        result = save_doi_to_event(event_id=self.other_event.pk, doi=DOI)
        self.assertFalse(result.resource_created)
        self.assertTrue(result.association_created)
        self.assertEqual(result.resource.pk, first.resource.pk)

    def test_invalid_new_bibliography_is_rejected_without_partial_records_or_input_changes(self):
        before = self.snapshot()
        cases = [None, {}, {"title": ""}, {"title": "   "}, {"title": "x" * 501},
                 {"original_url": ""}, {"original_url": "ftp://example.org/file"},
                 {"original_url": "not a URL"}, {"year": 10000}, {"resource_type": "unknown"}]
        for changes in cases:
            fields = changes if changes is None else {**self.bibliography, **changes}
            if changes == {}:
                fields = {}
            submitted = deepcopy(fields)
            with self.subTest(fields=changes), self.assertRaises(ValidationError):
                self.save(bibliography=fields)
            self.assertEqual(fields, submitted)
            self.assertEqual(self.snapshot(), before)

    def test_invalid_doi_fails_before_database_or_network_access(self):
        before = self.snapshot()
        with self.assertNumQueries(0), self.assertRaises(ValidationError) as caught:
            self.save(doi="https://example.org/10.1234/save-fixture")
        self.assertEqual(caught.exception.code, "invalid_doi")
        self.assertEqual(self.snapshot(), before)

    def test_link_validation_failure_rolls_back_new_resource_and_allows_explicit_retry(self):
        before = self.snapshot()
        for changes in ({"display_order": "invalid"}, {"recommendation": None}):
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                self.save(**changes)
            self.assertEqual(self.snapshot(), before)
        result = self.save()
        self.assertTrue(result.resource_created)
        self.assertTrue(result.association_created)

    def test_actual_database_link_failure_rolls_back_new_resource_and_connection_recovers(self):
        before = self.snapshot()

        def fail_link(link, *args, **kwargs):
            self.assertTrue(connection.in_atomic_block)
            self.assertTrue(Resource.objects.filter(pk=link.resource_id, doi=DOI).exists())
            # Bypass model validation to exercise a real PostgreSQL NOT NULL error.
            link.display_order = None
            return models.Model.save(link, *args, **kwargs)

        with patch.object(EventResource, "save", fail_link), self.assertRaises(IntegrityError):
            self.save()
        self.assertFalse(connection.needs_rollback)
        self.assertEqual(self.snapshot(), before)
        result = self.save()
        self.assertTrue(result.resource_created)
        self.assertEqual((Resource.objects.count(), EventResource.objects.count()), (1, 1))

    def test_link_failure_does_not_change_existing_shared_resource_or_other_links(self):
        self.save()
        before = self.snapshot()
        with self.assertRaises(ValidationError):
            self.save(event_id=self.other_event.pk, recommendation=None,
                      bibliography={"title": "Do not overwrite"})
        self.assertEqual(self.snapshot(), before)

    def test_caller_transaction_failure_can_roll_back_successful_service_result(self):
        before = self.snapshot()
        with self.assertRaisesMessage(RuntimeError, "Caller state save failed"):
            with transaction.atomic():
                result = self.save()
                self.assertTrue(Resource.objects.filter(pk=result.resource.pk).exists())
                self.assertTrue(EventResource.objects.filter(pk=result.association.pk).exists())
                raise RuntimeError("Caller state save failed")
        self.assertEqual(self.snapshot(), before)

    def test_missing_or_deleted_target_refuses_save_without_creating_resource(self):
        deleted_id = self.other_event.pk
        self.other_event.delete()
        before = self.snapshot()
        with self.assertRaises(Event.DoesNotExist):
            self.save(event_id=deleted_id)
        self.assertEqual(self.snapshot(), before)
