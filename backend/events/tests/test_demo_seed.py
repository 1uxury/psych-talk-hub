"""Step 09 acceptance: deterministic, offline, non-destructive demo imports."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from io import StringIO
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError
from django.test import TestCase

from events.demo_seed import load_demo_manifest, seed_demo_data
from events.models import Event, EventResource, Resource


class DemoSeedTests(TestCase):
    seed_at = datetime(2026, 10, 4, 18, tzinfo=timezone.utc)
    sleep_key = "demo-event-sleep-memory-v1"
    social_key = "demo-event-social-connection-v1"

    def import_demo(self, *, seed_at=None):
        return seed_demo_data(seed_at=self.seed_at if seed_at is None else seed_at)

    def snapshot(self):
        return {
            "events": list(Event.objects.order_by("id").values()),
            "resources": list(Resource.objects.order_by("id").values()),
            "associations": list(EventResource.objects.order_by("id").values()),
        }

    def test_first_import_has_eight_fictional_talks_three_readings_each_and_fixed_dates(self):
        self.assertEqual(self.import_demo(), {"events": 8, "resources": 11, "associations": 24})
        upcoming = Event.objects.get(seed_key=self.sleep_key)
        past = Event.objects.get(seed_key=self.social_key)
        self.assertEqual(upcoming.starts_at, self.seed_at + timedelta(days=30))
        self.assertEqual(past.starts_at, self.seed_at - timedelta(days=7))
        self.assertEqual(Event.objects.filter(starts_at__gt=self.seed_at).count(), 4)
        self.assertEqual(Event.objects.filter(starts_at__lt=self.seed_at).count(), 4)
        for event in Event.objects.all():
            self.assertTrue(event.is_example)
            self.assertIn("Example event", event.title)
            self.assertIn("fictional speaker", event.speaker)
            self.assertIn("Reading selections are illustrative; these talks are fictional.", event.description)
            self.assertIn("Independent portfolio prototype. Not affiliated with Conn8cting.", event.description)
            links = list(event.event_resources.all())
            self.assertEqual(len(links), 3)
            self.assertEqual([link.display_order for link in links], [10, 20, 30])
            self.assertTrue(all("illustrative" in link.recommendation for link in links))

    def test_curated_bibliography_and_provenance_are_present_without_invented_dois(self):
        self.import_demo()
        expected_papers = {
            "10.1152/physrev.00032.2012": ("About Sleep's Role in Memory", "Björn Rasch; Jan Born", 2013),
            "10.1038/nrn2762": ("The memory function of sleep", "Susanne Diekelmann; Jan Born", 2010),
            "10.1371/journal.pmed.1000316": (
                "Social Relationships and Mortality Risk: A Meta-analytic Review",
                "Julianne Holt-Lunstad; Timothy B. Smith; J. Bradley Layton", 2010,
            ),
            "10.1177/0146167214529799": (
                "Social Interactions and Well-Being", "Gillian M. Sandstrom; Elizabeth W. Dunn", 2014,
            ),
        }
        self.assertEqual(set(Resource.objects.exclude(doi=None).values_list("doi", flat=True)), set(expected_papers))
        for doi, bibliography in expected_papers.items():
            resource = Resource.objects.get(doi=doi)
            self.assertEqual((resource.title, resource.authors, resource.year), bibliography)
            self.assertEqual(resource.original_url, f"https://doi.org/{doi}")
            self.assertEqual(resource.resource_type, "research_paper")
            self.assertEqual(resource.metadata_source, "crossref")
            self.assertIsNone(resource.seed_key)
        nih = Resource.objects.get(seed_key="demo-resource-nih-sleep-on-it-v1")
        who = Resource.objects.get(seed_key="demo-resource-who-social-connection-v1")
        self.assertEqual((nih.title, nih.authors, nih.year), ("Sleep On It", "NIH News in Health", 2013))
        self.assertEqual(nih.original_url, "https://newsinhealth.nih.gov/2013/04/sleep-it")
        self.assertEqual(who.authors, "World Health Organization")
        self.assertEqual(who.year, 2025)
        self.assertTrue(who.original_url.startswith("https://www.who.int/news/item/30-06-2025-"))
        for article in (nih, who):
            self.assertIsNone(article.doi)
            self.assertEqual((article.resource_type, article.metadata_source), ("article", "manual"))
        manifest = load_demo_manifest()
        self.assertEqual(manifest["verified_on"], "2026-10-04")
        self.assertTrue(all(entry["verification_url"].startswith("https://") for entry in manifest["resources"]))

    def test_repeat_import_changes_neither_records_ids_nor_dates(self):
        self.import_demo()
        before = self.snapshot()
        self.assertEqual(self.import_demo(seed_at=self.seed_at + timedelta(days=400)),
                         {"events": 0, "resources": 0, "associations": 0})
        self.assertEqual(self.snapshot(), before)

    def test_repeat_import_preserves_manual_edits_and_deliberately_empty_fields(self):
        self.import_demo()
        event = Event.objects.get(seed_key=self.sleep_key)
        event.title = "Edited talk"
        event.starts_at = self.seed_at + timedelta(days=70)
        event.description = event.topic = event.speaker = ""
        event.is_example = False
        event.save()
        resource = Resource.objects.get(doi="10.1038/nrn2762")
        resource.title = "Edited bibliography"
        resource.authors = ""
        resource.year = None
        resource.original_url = "https://example.org/curated-link"
        resource.resource_type = "article"
        resource.metadata_source = "manual"
        resource.save()
        link = event.event_resources.get(resource=resource)
        link.recommendation = ""
        link.display_order = -8
        link.save()
        before = self.snapshot()
        self.import_demo(seed_at=self.seed_at + timedelta(days=5))
        self.assertEqual(self.snapshot(), before)

    def test_existing_normalised_doi_is_reused_without_overwriting_shared_metadata(self):
        existing = Resource.objects.create(
            doi="10.1038/NRN2762", title="Already curated", authors="Kept author",
            original_url="https://example.org/existing", metadata_source="manual",
        )
        other_event = Event.objects.create(title="Independent talk", starts_at=self.seed_at)
        other_link = EventResource.objects.create(event=other_event, resource=existing, recommendation="Keep this")
        manifest = deepcopy(load_demo_manifest())
        manifest["resources"][1]["fields"]["doi"] = "  10.1038/NRN2762  "
        with patch("events.demo_seed.load_demo_manifest", return_value=manifest):
            self.assertEqual(self.import_demo(), {"events": 8, "resources": 10, "associations": 24})
        existing.refresh_from_db()
        other_link.refresh_from_db()
        self.assertEqual((existing.title, existing.authors, existing.metadata_source),
                         ("Already curated", "Kept author", "manual"))
        self.assertEqual(existing.original_url, "https://example.org/existing")
        self.assertIsNone(existing.seed_key)
        self.assertEqual(other_link.recommendation, "Keep this")
        self.assertTrue(EventResource.objects.filter(event__seed_key=self.sleep_key, resource=existing).exists())
        self.assertEqual((Event.objects.count(), Resource.objects.count(), EventResource.objects.count()), (9, 11, 25))

    def test_unkeyed_manual_records_with_identical_titles_and_urls_are_not_merged(self):
        existing_ids = []
        for entry in load_demo_manifest()["resources"]:
            if entry["fields"]["doi"] is None:
                fields = {**entry["fields"], "seed_key": None}
                existing_ids.append(Resource.objects.create(**fields).pk)
        self.assertEqual(self.import_demo(), {"events": 8, "resources": 11, "associations": 24})
        self.assertEqual(Resource.objects.count(), 18)
        for resource in Resource.objects.filter(pk__in=existing_ids):
            self.assertIsNone(resource.seed_key)
            self.assertFalse(resource.event_resources.exists())

    def test_removed_reading_is_the_only_record_recreated_on_repeat(self):
        self.import_demo()
        removed = EventResource.objects.get(event__seed_key=self.sleep_key, resource__doi="10.1038/nrn2762")
        event_id, resource_id, old_id = removed.event_id, removed.resource_id, removed.pk
        removed.delete()
        before = self.snapshot()
        self.assertEqual(self.import_demo(), {"events": 0, "resources": 0, "associations": 1})
        restored = EventResource.objects.get(event_id=event_id, resource_id=resource_id)
        self.assertNotEqual(restored.pk, old_id)
        after = self.snapshot()
        self.assertEqual(after["events"], before["events"])
        self.assertEqual(after["resources"], before["resources"])
        self.assertEqual([row for row in after["associations"] if row["id"] != restored.pk], before["associations"])

    def test_deleted_talk_is_recreated_without_moving_the_surviving_talk_or_recreating_books(self):
        self.import_demo()
        Event.objects.get(seed_key=self.social_key).delete()
        before = self.snapshot()
        later = self.seed_at + timedelta(days=3)
        self.assertEqual(self.import_demo(seed_at=later), {"events": 1, "resources": 0, "associations": 3})
        self.assertEqual(Event.objects.get(seed_key=self.social_key).starts_at, later - timedelta(days=7))
        self.assertEqual(list(Resource.objects.order_by("id").values()), before["resources"])
        self.assertEqual(Event.objects.get(seed_key=self.sleep_key).starts_at, self.seed_at + timedelta(days=30))

    def test_missing_unlinked_seeded_article_and_its_reading_are_filled(self):
        self.import_demo()
        article = Resource.objects.get(seed_key="demo-resource-nih-sleep-on-it-v1")
        article.event_resources.all().delete()
        article.delete()  # Ordinary ORM deletion; Admin still prohibits resource deletion.
        before = self.snapshot()
        self.assertEqual(self.import_demo(), {"events": 0, "resources": 1, "associations": 3})
        self.assertEqual(self.snapshot()["events"], before["events"])
        for row in before["resources"]:
            self.assertIn(row, self.snapshot()["resources"])

    def test_invalid_import_instant_is_rejected_before_any_records_are_created(self):
        for invalid in (datetime(2026, 10, 4), "2026-10-04"):
            with self.subTest(invalid=invalid), self.assertRaises(ValidationError):
                seed_demo_data(seed_at=invalid)
        self.assertEqual(self.snapshot(), {"events": [], "resources": [], "associations": []})

    def test_late_link_failure_rolls_back_the_entire_import(self):
        original_save = EventResource.save
        calls = []

        def fail_last_link(instance, *args, **kwargs):
            calls.append(instance)
            if len(calls) == 24:
                raise ValidationError("Simulated final reading failure")
            return original_save(instance, *args, **kwargs)

        with patch.object(EventResource, "save", new=fail_last_link):
            with self.assertRaises(ValidationError):
                self.import_demo()
        self.assertEqual(len(calls), 24)
        self.assertEqual(self.snapshot(), {"events": [], "resources": [], "associations": []})
        self.assertEqual(self.import_demo(), {"events": 8, "resources": 11, "associations": 24})

    def test_management_command_is_explicit_offline_and_reports_created_counts(self):
        output = StringIO()
        with patch("requests.sessions.Session.request", side_effect=AssertionError("No network during seed")) as request:
            with patch("events.demo_seed.timezone.now", return_value=self.seed_at):
                call_command("seed_demo", stdout=output)
                call_command("seed_demo", stdout=output)
        request.assert_not_called()
        self.assertIn("8 talks, 11 resources, 24 reading links", output.getvalue())
        self.assertIn("0 talks, 0 resources, 0 reading links", output.getvalue())
        self.assertIn("Existing records were kept.", output.getvalue())

    def test_management_command_failure_has_no_internal_database_details(self):
        with patch("events.management.commands.seed_demo.seed_demo_data",
                   side_effect=IntegrityError("private-database-sentinel")):
            with self.assertRaises(CommandError) as error:
                call_command("seed_demo", stdout=StringIO())
        self.assertIn("no partial import was saved", str(error.exception))
        self.assertNotIn("private-database-sentinel", str(error.exception))
        self.assertEqual(self.snapshot(), {"events": [], "resources": [], "associations": []})
