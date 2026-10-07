"""Step 20: mocked successful conversion, incomplete review and no persistence."""

import copy
import json
from dataclasses import asdict
from unittest.mock import patch

import requests
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from events.models import Event, EventResource, Resource
from events.services.crossref import fetch_metadata
from events.services.crossref_metadata import convert_work


DOI = "10.1234/fixture"


def work_fixture(**overrides):
    work = {
        "title": ["Conversion fixture"],
        "author": [{"given": "First", "family": "Author"}],
        "published-print": {"date-parts": [[2020, 5, 1]]},
        "URL": "https://example.org/reading",
        "type": "journal-article",
    }
    work.update(overrides)
    return work


def success_response(work):
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps({
        "status": "ok", "message-type": "work", "message-version": "1.0.0",
        "message": work,
    }).encode("utf-8")
    response.headers["Content-Type"] = "application/json"
    return response


class CrossrefConversionTests(SimpleTestCase):
    def test_first_nonempty_title_is_trimmed_without_joining_or_fallback(self):
        work = work_fixture(title=[None, 7, "", " \t", " First: a title. ", "Second title"])
        work["subtitle"] = ["Ignored subtitle"]
        work["container-title"] = ["Ignored journal title"]
        self.assertEqual(convert_work(DOI, work).title, "First: a title.")

    def test_missing_or_invalid_title_requires_administrator_input(self):
        for titles in (None, [], ["", " \n"], "Not a title array", {}, [None, 12, {}]):
            with self.subTest(titles=titles):
                result = convert_work(DOI, work_fixture(title=titles))
                self.assertEqual(result.title, "")
                self.assertEqual(result.missing_required_fields, ("title",))
                self.assertTrue(result.needs_review)
        result = convert_work(DOI, {})
        self.assertEqual(result.missing_required_fields, ("title", "original_url"))

    def test_overlength_first_title_is_preserved_for_correction_not_replaced(self):
        result = convert_work(DOI, work_fixture(title=["T" * 501, "Later title"]))
        self.assertEqual(result.title, "T" * 501)
        self.assertEqual(result.missing_required_fields, ("title",))
        with self.assertRaises(ValidationError):
            Resource(**asdict(result)).full_clean(validate_unique=False, validate_constraints=False)

    def test_personal_partial_and_organisation_authors_keep_source_order(self):
        work = work_fixture(author=[
            {"given": " First ", "family": " Person ", "name": "Ignored organisation"},
            {"name": " Study Group "},
            {"given": "OnlyGiven"},
            {"family": "OnlyFamily", "name": "Ignored name"},
            {"given": " ", "family": None, "name": " Organisation Two "},
            {"given": 12, "family": [], "name": "Organisation Three"},
            None, "Invalid author", {}, {"affiliation": [{"name": "Not an author"}]},
            {"given": "First", "family": "Person"},
        ])
        self.assertEqual(
            convert_work(DOI, work).authors,
            "First Person; Study Group; OnlyGiven; OnlyFamily; Organisation Two; Organisation Three; First Person",
        )

    def test_missing_and_unusable_authors_remain_an_optional_empty_string(self):
        for authors in (None, [], {}, "Author", [None, {}, {"name": " "}]):
            with self.subTest(authors=authors):
                result = convert_work(DOI, work_fixture(author=authors))
                self.assertEqual(result.authors, "")
                self.assertEqual(result.missing_required_fields, ())
                self.assertTrue(result.needs_review)
                Resource(**asdict(result)).full_clean(validate_unique=False, validate_constraints=False)

    def test_print_online_issued_priority_uses_year_not_earliest_date(self):
        work = work_fixture(**{
            "published-print": {"date-parts": [[2022]]},
            "published-online": {"date-parts": [[2021]]},
            "issued": {"date-parts": [[2019]]},
            "created": {"date-parts": [[2018]]},
        })
        self.assertEqual(convert_work(DOI, work).year, 2022)
        del work["published-print"]
        self.assertEqual(convert_work(DOI, work).year, 2021)
        del work["published-online"]
        self.assertEqual(convert_work(DOI, work).year, 2019)
        del work["issued"]
        self.assertIsNone(convert_work(DOI, work).year)

    def test_invalid_preferred_year_falls_back_without_numeric_coercion(self):
        for year in (None, "2020", 2020.0, True, False, 0, -1, 10000, [], {}):
            with self.subTest(year=year):
                work = work_fixture(**{
                    "published-print": {"date-parts": [[year]]},
                    "published-online": {"date-parts": [[2021]]},
                    "issued": {"date-parts": [[2022]]},
                })
                self.assertEqual(convert_work(DOI, work).year, 2021)
                work["published-online"] = {"date-parts": [[year]]}
                self.assertEqual(convert_work(DOI, work).year, 2022)

    def test_malformed_and_missing_dates_produce_null_without_blocking_save(self):
        for date in (None, [], "2020", {}, {"date-parts": None}, {"date-parts": []},
                     {"date-parts": [None]}, {"date-parts": [2020]},
                     {"date-parts": [[]]}, {"date-parts": {"year": 2020}}):
            with self.subTest(date=date):
                result = convert_work(DOI, work_fixture(**{"published-print": date}))
                self.assertIsNone(result.year)
                self.assertTrue(result.needs_review)
                self.assertEqual(result.missing_required_fields, ())
                Resource(**asdict(result)).full_clean(validate_unique=False, validate_constraints=False)

    def test_year_boundaries_and_first_date_part_of_range(self):
        for year in (1, 9999):
            result = convert_work(DOI, work_fixture(**{"published-print": {"date-parts": [[year]]}}))
            self.assertEqual(result.year, year)
            self.assertIs(type(result.year), int)
        work = work_fixture(**{
            "published-print": {"date-parts": [[2020, 12, 1], [2021, 1, 1]]},
        })
        self.assertEqual(convert_work(DOI, work).year, 2020)
        work["published-print"]["date-parts"][0][0] = 0
        self.assertIsNone(convert_work(DOI, work).year)

    def test_only_journal_and_proceedings_map_to_research_paper(self):
        for kind in ("journal-article", "proceedings-article", "book-chapter", "posted-content",
                     "report", "other", None, "", [], {}):
            with self.subTest(kind=kind):
                result = convert_work(DOI, work_fixture(type=kind))
                expected = "research_paper" if kind in ("journal-article", "proceedings-article") else "article"
                self.assertEqual(result.resource_type, expected)
                self.assertEqual(result.metadata_source, "crossref")

    def test_valid_http_and_https_urls_preserve_publisher_path_query_and_fragment(self):
        for url in ("http://example.org/paper", "https://example.org/Case%2FPath?x=1&y=2#part"):
            with self.subTest(url=url):
                result = convert_work(DOI, work_fixture(URL=" " + url + " "))
                self.assertEqual(result.original_url, url)
                self.assertFalse(result.needs_review)
                Resource(**asdict(result)).full_clean(validate_unique=False, validate_constraints=False)

    def test_missing_and_invalid_urls_stay_empty_without_resolver_or_link_fallback(self):
        for url in (None, "", " ", 3, [], {}, "javascript:alert(1)", "data:text/plain,paper",
                    "ftp://example.org/paper", "//example.org/paper", "/paper", "https://",
                    "https://[invalid/paper", "https://example.org/two words",
                    "https://example.org/a\nb", "https://example.org/a\x00b",
                    "https://example.org/" + "a" * 2048):
            with self.subTest(url=url):
                work = work_fixture(URL=url, link=[{"URL": "https://example.org/fallback"}])
                work["resource"] = {"primary": {"URL": "https://example.org/another"}}
                result = convert_work(DOI, work)
                self.assertEqual(result.original_url, "")
                self.assertEqual(result.missing_required_fields, ("original_url",))
                with self.assertRaises(ValidationError) as error:
                    Resource(**asdict(result)).full_clean(validate_unique=False, validate_constraints=False)
                self.assertIn("original_url", error.exception.message_dict)

    def test_only_card_fields_are_returned_and_input_is_not_changed(self):
        work = work_fixture(DOI="10.9999/other", abstract="Do not import this abstract",
                            summary="Do not generate conclusions", metadata_source="manual")
        before = copy.deepcopy(work)
        result = convert_work(" HTTPS://DOI.ORG/10.1234/FIXTURE ", work)
        self.assertEqual(asdict(result), {
            "title": "Conversion fixture", "authors": "First Author", "year": 2020,
            "original_url": "https://example.org/reading", "doi": DOI,
            "resource_type": "research_paper", "metadata_source": "crossref",
        })
        self.assertEqual(work, before)
        self.assertEqual(result.missing_required_fields, ())
        self.assertFalse(result.needs_review)


class CrossrefSuccessfulFetchTests(SimpleTestCase):
    def test_real_requests_pipeline_uses_one_fixed_encoded_target_and_closes_response(self):
        response = success_response(work_fixture())
        with patch("requests.adapters.HTTPAdapter.send", return_value=response) as send:
            with patch.object(response, "close", wraps=response.close) as close:
                result = fetch_metadata(" https://doi.org/10.1234/A%3Fq%3D1%23part ")
        send.assert_called_once()
        request = send.call_args.args[0]
        self.assertEqual(request.url, "https://api.crossref.org/works/10.1234%2Fa%3Fq%3D1%23part")
        self.assertEqual(request.method, "GET")
        self.assertEqual(request.headers["Accept"], "application/json")
        self.assertEqual(send.call_args.kwargs["timeout"], (3, 7))
        self.assertTrue(send.call_args.kwargs["verify"])
        self.assertEqual(result.doi, "10.1234/a?q=1#part")
        close.assert_called_once()

    def test_incomplete_success_is_returned_for_review_and_response_is_closed(self):
        response = success_response({})
        with patch("events.services.crossref.requests.get", return_value=response) as get:
            with patch.object(response, "close", wraps=response.close) as close:
                result = fetch_metadata(DOI)
        get.assert_called_once()
        self.assertFalse(get.call_args.kwargs["allow_redirects"])
        self.assertEqual(result.missing_required_fields, ("title", "original_url"))
        self.assertEqual(result.authors, "")
        self.assertIsNone(result.year)
        self.assertTrue(result.needs_review)
        close.assert_called_once()

    def test_invalid_doi_fails_before_fetch(self):
        with patch("events.services.crossref.requests.get") as get:
            with self.assertRaises(ValidationError):
                fetch_metadata("https://example.org/10.1234/fixture")
        get.assert_not_called()


class CrossrefPersistenceBoundaryTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(title="Existing talk", starts_at=timezone.now())
        self.resource = Resource.objects.create(
            title="Administrator-edited title", authors="Saved authors", year=2024,
            original_url="https://example.org/saved", doi=DOI, metadata_source="crossref",
        )
        EventResource.objects.create(event=self.event, resource=self.resource,
                                     recommendation="Keep this reason", display_order=-3)

    def snapshot(self):
        return [list(model.objects.order_by("pk").values())
                for model in (Event, Resource, EventResource)]

    def test_fetch_and_conversion_neither_query_nor_modify_any_business_record(self):
        before = self.snapshot()
        for work in (work_fixture(), {}):
            with self.subTest(work=work):
                with patch("events.services.crossref.requests.get", return_value=success_response(work)) as get:
                    with self.assertNumQueries(0):
                        result = fetch_metadata(DOI)
                get.assert_called_once()
                self.assertEqual(result.doi, DOI)
                self.assertEqual(self.snapshot(), before)

    def test_missing_invalid_and_overlength_required_metadata_cannot_save(self):
        before = self.snapshot()
        for overrides, field in (({"title": []}, "title"),
                                 ({"title": ["T" * 501]}, "title"),
                                 ({"URL": None}, "original_url"),
                                 ({"URL": "javascript:alert(1)"}, "original_url")):
            with self.subTest(overrides=overrides):
                result = convert_work("10.1234/new", work_fixture(**overrides))
                self.assertIn(field, result.missing_required_fields)
                with self.assertRaises(ValidationError) as error:
                    Resource(**asdict(result)).save()
                self.assertIn(field, error.exception.message_dict)
                self.assertEqual(self.snapshot(), before)
