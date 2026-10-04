"""Step 06 acceptance: shared bibliography and PostgreSQL constraints."""

import json

from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.test import TestCase
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from events.models import Resource


class BibliographyProbeSerializer(serializers.ModelSerializer):
    """Test-only null/type probe; the public association serializer comes later."""

    resource_id = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = Resource
        fields = (
            "resource_id", "title", "authors", "year", "original_url", "doi",
            "resource_type", "metadata_source",
        )
        read_only_fields = fields


class ResourceTests(TestCase):
    def create_resource(self, **overrides):
        values = {"title": "Reading fixture", "original_url": "https://example.org/reading"}
        values.update(overrides)
        return Resource.objects.create(**values)

    def test_both_types_and_sources_round_trip_and_edits_retain_source(self):
        for resource_type in Resource.ResourceType.values:
            for metadata_source in Resource.MetadataSource.values:
                with self.subTest(resource_type=resource_type, metadata_source=metadata_source):
                    resource = self.create_resource(
                        authors="First Author; Second Author",
                        year=2020,
                        resource_type=resource_type,
                        metadata_source=metadata_source,
                    )
                    resource.refresh_from_db()
                    self.assertIsInstance(resource.pk, int)
                    self.assertEqual(resource.authors, "First Author; Second Author")
                    self.assertEqual(resource.year, 2020)
                    self.assertEqual(resource.resource_type, resource_type)
                    self.assertEqual(resource.metadata_source, metadata_source)
                    self.assertEqual(str(resource), resource.title)
                    resource.title = "Corrected reading fixture"
                    resource.save(update_fields=["title"])
                    resource.refresh_from_db()
                    self.assertEqual(resource.title, "Corrected reading fixture")
                    self.assertEqual(resource.metadata_source, metadata_source)

    def test_minimal_resource_has_contract_defaults(self):
        resource = self.create_resource()
        resource.refresh_from_db()
        self.assertEqual(resource.authors, "")
        self.assertIsNone(resource.year)
        self.assertIsNone(resource.doi)
        self.assertIsNone(resource.seed_key)
        self.assertEqual(resource.resource_type, "article")
        self.assertEqual(resource.metadata_source, "manual")

    def test_multiple_empty_dois_and_seed_keys_become_null_without_conflicts(self):
        for empty in (None, "", " \t\n", "\u3000"):
            with self.subTest(empty=repr(empty)):
                resource = self.create_resource(doi=empty, seed_key=empty)
                resource.refresh_from_db()
                self.assertIsNone(resource.doi)
                self.assertIsNone(resource.seed_key)
        self.assertEqual(Resource.objects.count(), 4)

    def test_bare_doi_is_trimmed_lowercased_and_preserves_suffix_punctuation(self):
        resource = self.create_resource(doi=" 10.1234/ABC.(Def);/G:HI%2F?x=1#part. ")
        resource.refresh_from_db()
        self.assertEqual(resource.doi, "10.1234/abc.(def);/g:hi%2f?x=1#part.")
        self.assertEqual(Resource.objects.get(doi=resource.doi).pk, resource.pk)
        seeded = self.create_resource(seed_key=" demo-reading ")
        seeded.refresh_from_db()
        self.assertEqual(seeded.seed_key, "demo-reading")

    def test_invalid_bare_dois_are_rejected_without_creating_records(self):
        for doi in (
            "11.1234/abc", "10.123/abc", "10.1234567890/abc", "10.1234/",
            "10.1234/two words", "10.1234/two\nwords", "https://doi.org/10.1234/abc",
        ):
            with self.subTest(doi=doi):
                with self.assertRaises(ValidationError) as error:
                    self.create_resource(doi=doi)
                self.assertIn("doi", error.exception.message_dict)
        self.assertEqual(Resource.objects.count(), 0)

    def test_duplicate_nonempty_identifiers_fail_validation_and_database_uniqueness(self):
        for field, value, duplicate in (
            ("doi", "10.1234/example", " 10.1234/EXAMPLE "),
            ("seed_key", "demo-reading", " demo-reading "),
        ):
            with self.subTest(field=field):
                first = self.create_resource(**{field: value})
                with self.assertRaises(ValidationError) as error:
                    self.create_resource(**{field: duplicate})
                self.assertIn(field, error.exception.message_dict)
                other = self.create_resource()
                # This bypasses save/full_clean and tests the database boundary.
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Resource.objects.filter(pk=other.pk).update(**{field: value})
                other.refresh_from_db()
                self.assertIsNone(getattr(other, field))
                self.assertEqual(Resource.objects.get(**{field: value}).pk, first.pk)
        self.assertEqual(Resource.objects.count(), 4)

    def test_manual_records_with_same_title_or_url_remain_independent(self):
        first = self.create_resource()
        identical = self.create_resource()
        same_title = self.create_resource(original_url="https://example.org/another")
        same_url = self.create_resource(title="Another reading fixture")
        self.assertEqual(len({first.pk, identical.pk, same_title.pk, same_url.pk}), 4)
        self.assertEqual(Resource.objects.count(), 4)
        for resource in (first, identical, same_title, same_url):
            self.assertEqual(resource.metadata_source, "manual")
        self.assertEqual(Resource.objects.get(pk=first.pk).pk, first.pk)

    def test_missing_and_whitespace_only_titles_are_rejected(self):
        for title in (None, "", " \t\n", "\u3000"):
            with self.subTest(title=repr(title)):
                with self.assertRaises(ValidationError) as error:
                    self.create_resource(title=title)
                self.assertIn("title", error.exception.message_dict)
        self.assertEqual(Resource.objects.count(), 0)

    def test_original_url_requires_valid_http_or_https(self):
        for original_url in (
            None, "", " ", "ftp://example.org/file", "ftps://example.org/file",
            "javascript:alert(1)", "file:///reading.pdf", "example.org/reading",
            "https://", "https://example.org/two words",
        ):
            with self.subTest(original_url=original_url):
                with self.assertRaises(ValidationError) as error:
                    self.create_resource(original_url=original_url)
                self.assertIn("original_url", error.exception.message_dict)
        self.assertEqual(Resource.objects.count(), 0)
        for original_url in ("http://example.org/reading", "https://example.org/reading"):
            resource = self.create_resource(original_url=original_url)
            resource.refresh_from_db()
            self.assertEqual(resource.original_url, original_url)

    def test_year_accepts_null_and_inclusive_bounds_and_rejects_out_of_range(self):
        for year in (None, 1, 9999):
            with self.subTest(year=year):
                resource = self.create_resource(year=year)
                resource.refresh_from_db()
                self.assertEqual(resource.year, year)
        for year in (-1, 0, 10000, "not-a-year"):
            with self.subTest(year=year):
                with self.assertRaises(ValidationError) as error:
                    self.create_resource(year=year)
                self.assertIn("year", error.exception.message_dict)
        self.assertEqual(Resource.objects.count(), 3)

    def test_unknown_or_empty_types_and_sources_are_rejected(self):
        for field in ("resource_type", "metadata_source"):
            for value in (None, "", "unknown"):
                with self.subTest(field=field, value=value):
                    with self.assertRaises(ValidationError) as error:
                        self.create_resource(**{field: value})
                    self.assertIn(field, error.exception.message_dict)
        self.assertEqual(Resource.objects.count(), 0)

    def test_database_rejects_invalid_writes_that_bypass_model_validation(self):
        resource = self.create_resource()
        invalid_updates = (
            {"title": None}, {"title": ""}, {"title": " \t\n"}, {"authors": None},
            {"year": 0}, {"year": 10000}, {"original_url": None}, {"original_url": ""},
            {"original_url": "ftp://example.org/file"}, {"doi": ""}, {"doi": " "},
            {"doi": "10.1234/UPPERCASE"}, {"doi": "10.123/invalid"},
            {"doi": "10.1234/two words"}, {"seed_key": " "},
            {"resource_type": "unknown"}, {"metadata_source": "unknown"},
        )
        for values in invalid_updates:
            with self.subTest(values=values):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Resource.objects.filter(pk=resource.pk).update(**values)
        resource.refresh_from_db()
        self.assertEqual(resource.title, "Reading fixture")
        self.assertEqual(resource.authors, "")
        self.assertEqual(resource.original_url, "https://example.org/reading")
        self.assertIsNone(resource.year)
        self.assertIsNone(resource.doi)
        self.assertIsNone(resource.seed_key)
        self.assertEqual(resource.resource_type, "article")
        self.assertEqual(resource.metadata_source, "manual")

    def test_missing_bibliography_serializes_as_empty_author_and_json_nulls(self):
        resource = self.create_resource(seed_key="private-seed")
        resource.refresh_from_db()
        payload = json.loads(JSONRenderer().render(BibliographyProbeSerializer(resource).data))
        self.assertEqual(payload, {
            "resource_id": resource.pk,
            "title": "Reading fixture",
            "authors": "",
            "year": None,
            "original_url": "https://example.org/reading",
            "doi": None,
            "resource_type": "article",
            "metadata_source": "manual",
        })
        complete = self.create_resource(authors="An Author", year=9999, doi="10.1234/example")
        payload = json.loads(JSONRenderer().render(BibliographyProbeSerializer(complete).data))
        self.assertEqual(payload["authors"], "An Author")
        self.assertIsInstance(payload["year"], int)
        self.assertEqual(payload["doi"], "10.1234/example")

    def test_resource_migration_is_applied_in_the_isolated_postgresql_database(self):
        self.assertEqual(connection.vendor, "postgresql")
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM django_migrations WHERE app = %s", ["events"])
            migration_names = {row[0] for row in cursor.fetchall()}
        self.assertIn("0001_initial", migration_names)
        self.assertIn("0002_resource", migration_names)
        self.assertIn("events_resource", connection.introspection.table_names())
