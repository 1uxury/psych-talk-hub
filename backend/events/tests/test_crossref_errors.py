"""Step 21: safe lookup failures, explicit retry and unchanged business data."""

import json
import traceback
from unittest.mock import patch

import requests
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from events.models import Event, EventResource, Resource
from events.services.crossref import CrossrefLookupError, fetch_metadata
from events.services.doi import INVALID_DOI_MESSAGE
from events.tests.test_crossref_metadata import DOI, success_response, work_fixture


INPUT = " \tHTTPS://DOI.ORG/10.1234/FIXTURE \n"
PRIVATE_DETAIL = "private-provider-body-and-connection-details"
NOT_FOUND = "No publication was found for this DOI."
UNAVAILABLE = (
    "We couldn't fetch publication details. Please try again or add the resource manually."
)


def http_response(status=200, body=None):
    response = requests.Response()
    response.status_code = status
    response._content = body if body is not None else PRIVATE_DETAIL.encode()
    response.headers["Content-Type"] = "application/json"
    return response


class CrossrefErrorTests(SimpleTestCase):
    def assert_safe_error(self, error, code, value=INPUT):
        message = NOT_FOUND if code == "not_found" else UNAVAILABLE
        self.assertEqual(error.code, code)
        self.assertEqual(error.message, message)
        self.assertEqual(str(error), message)
        self.assertEqual(error.args, (message,))
        self.assertEqual(error.input_value, value)
        self.assertEqual(error.can_retry, code != "not_found")
        self.assertTrue(error.can_add_manually)
        self.assertNotIn(PRIVATE_DETAIL, repr(error))
        self.assertNotIn(PRIVATE_DETAIL, "".join(traceback.format_exception(error)))
        self.assertIsNone(error.__cause__)

    def assert_response_failure(self, response, code, parses_json=False):
        # Exercise the actual Requests preparation/redirect machinery. Only the
        # final HTTP adapter is mocked, so this cannot contact an external host.
        def send_response(request, **kwargs):
            response.request = request
            response.url = request.url
            return response

        with patch("requests.adapters.HTTPAdapter.send", side_effect=send_response) as send:
            with patch.object(response, "close", wraps=response.close) as close:
                with patch.object(response, "json", wraps=response.json) as decode:
                    with self.assertRaises(CrossrefLookupError) as caught:
                        fetch_metadata(INPUT)
        self.assert_safe_error(caught.exception, code)
        send.assert_called_once()
        self.assertEqual(send.call_args.args[0].url, "https://api.crossref.org/works/10.1234%2Ffixture")
        self.assertEqual(send.call_args.kwargs["timeout"], (3, 7))
        self.assertTrue(send.call_args.kwargs["verify"])
        # Requests also closes a redirect while preparing its unused _next
        # request, even with redirects disabled. The lookup closes it again.
        self.assertEqual(close.call_count, 2 if response.is_redirect else 1)
        self.assertEqual(decode.call_count, int(parses_json))

    def test_not_found_keeps_exact_input_and_offers_correction_or_manual_entry(self):
        self.assert_response_failure(http_response(404), "not_found")

    def test_rate_limit_ignores_retry_after_and_does_not_retry_automatically(self):
        response = http_response(429)
        response.headers["Retry-After"] = "120"
        self.assert_response_failure(response, "rate_limited")

    def test_upstream_errors_have_safe_message_without_reading_error_body(self):
        for status in (500, 502, 503, 504, 599):
            with self.subTest(status=status):
                self.assert_response_failure(http_response(status), "upstream_error")

    def test_other_http_statuses_and_redirects_are_invalid_without_followup(self):
        for status in (201, 202, 204, 301, 302, 303, 307, 308, 400, 401, 403, 422):
            with self.subTest(status=status):
                response = http_response(status)
                response.headers["Location"] = "https://example.org/" + PRIVATE_DETAIL
                self.assert_response_failure(response, "invalid_response")

    def test_empty_html_malformed_and_excessively_nested_json_are_safe_failures(self):
        for body in (
            b"", b"<html>" + PRIVATE_DETAIL.encode() + b"</html>",
            b'{"message":' + PRIVATE_DETAIL.encode(),
            b"[" * 5000 + b"0" + b"]" * 5000,
        ):
            with self.subTest(body_length=len(body)):
                self.assert_response_failure(http_response(body=body), "invalid_response", parses_json=True)

    def test_invalid_envelopes_are_errors_rather_than_empty_success(self):
        for payload in (
            None, False, 7, PRIVATE_DETAIL, [], {},
            {"status": "error", "message-type": "work", "message": {"detail": PRIVATE_DETAIL}},
            {"status": "ok", "message-type": "work-list", "message": {}},
            {"status": "ok", "message-type": "work"},
            {"status": "ok", "message-type": "work", "message": None},
            {"status": "ok", "message-type": "work", "message": []},
            {"status": "ok", "message-type": "work", "message": PRIVATE_DETAIL},
        ):
            with self.subTest(payload=payload):
                self.assert_response_failure(
                    http_response(body=json.dumps(payload).encode()), "invalid_response", parses_json=True,
                )

    def test_connection_tls_and_proxy_failures_are_safe_and_not_retried(self):
        for exception in (requests.ConnectionError, requests.exceptions.SSLError, requests.exceptions.ProxyError):
            with self.subTest(exception=exception.__name__):
                with patch("requests.adapters.HTTPAdapter.send", side_effect=exception(PRIVATE_DETAIL)) as send:
                    with self.assertRaises(CrossrefLookupError) as caught:
                        fetch_metadata(INPUT)
                self.assert_safe_error(caught.exception, "connection_failed")
                send.assert_called_once()

    def test_connect_read_and_generic_timeouts_are_classified_before_connection_failure(self):
        for exception in (requests.Timeout, requests.ConnectTimeout, requests.ReadTimeout):
            with self.subTest(exception=exception.__name__):
                with patch("requests.adapters.HTTPAdapter.send", side_effect=exception(PRIVATE_DETAIL)) as send:
                    with self.assertRaises(CrossrefLookupError) as caught:
                        fetch_metadata(INPUT)
                self.assert_safe_error(caught.exception, "timeout")
                send.assert_called_once()

    def test_other_requests_failures_do_not_expose_internal_details(self):
        for exception in (requests.RequestException, requests.exceptions.ChunkedEncodingError,
                          requests.exceptions.ContentDecodingError):
            with self.subTest(exception=exception.__name__):
                with patch("requests.adapters.HTTPAdapter.send", side_effect=exception(PRIVATE_DETAIL)) as send:
                    with self.assertRaises(CrossrefLookupError) as caught:
                        fetch_metadata(INPUT)
                self.assert_safe_error(caught.exception, "provider_unavailable")
                send.assert_called_once()

    def test_explicit_retry_is_a_new_fetch_with_preserved_input_and_can_succeed(self):
        response = success_response(work_fixture())
        with patch("requests.adapters.HTTPAdapter.send", side_effect=[requests.ReadTimeout(PRIVATE_DETAIL), response]) as send:
            with self.assertRaises(CrossrefLookupError) as caught:
                fetch_metadata(INPUT)
            self.assert_safe_error(caught.exception, "timeout")
            send.assert_called_once()
            with patch.object(response, "close", wraps=response.close) as close:
                result = fetch_metadata(caught.exception.input_value)
            self.assertEqual(send.call_count, 2)
            close.assert_called_once()
        self.assertEqual(result.doi, DOI)
        self.assertEqual(result.title, "Conversion fixture")
        self.assertFalse(result.needs_review)

    def test_invalid_input_keeps_existing_validation_and_never_requests(self):
        for value in ("", "  invalid DOI  ", "https://example.org/10.1234/fixture"):
            with self.subTest(value=value):
                form_values = {"doi": value, "recommendation": "Keep this entered text"}
                before = form_values.copy()
                with patch("requests.adapters.HTTPAdapter.send") as send:
                    with self.assertRaises(ValidationError) as caught:
                        fetch_metadata(form_values["doi"])
                self.assertEqual(caught.exception.messages, [INVALID_DOI_MESSAGE])
                self.assertEqual(caught.exception.code, "invalid_doi")
                self.assertEqual(form_values, before)
                send.assert_not_called()

    def test_unexpected_programming_error_is_not_misreported_as_provider_failure(self):
        response = success_response(work_fixture())
        with patch("requests.adapters.HTTPAdapter.send", return_value=response) as send:
            with patch.object(response, "close", wraps=response.close) as close:
                with patch("events.services.crossref.convert_work", side_effect=RuntimeError("Test programming fault")):
                    with self.assertRaisesRegex(RuntimeError, "Test programming fault"):
                        fetch_metadata(INPUT)
        send.assert_called_once()
        close.assert_called_once()


class CrossrefFailurePersistenceTests(TestCase):
    def setUp(self):
        first = Event.objects.create(title="Saved talk", starts_at=timezone.now(), seed_key="failure-talk")
        second = Event.objects.create(title="Other talk", starts_at=timezone.now())
        shared = Resource.objects.create(
            title="Administrator-edited bibliography", authors="", year=None, doi=DOI,
            original_url="https://example.org/edited", metadata_source="crossref",
        )
        Resource.objects.create(title="Unlinked manual resource", original_url="https://example.org/manual")
        EventResource.objects.create(event=first, resource=shared, recommendation="Keep edited reason", display_order=-4)
        EventResource.objects.create(event=second, resource=shared, recommendation="", display_order=9)

    def snapshot(self):
        return [list(model.objects.order_by("pk").values())
                for model in (Event, Resource, EventResource)]

    def test_all_http_and_response_failures_leave_counts_and_complete_fields_unchanged(self):
        before = self.snapshot()
        cases = [(http_response(status), code) for status, code in (
            (404, "not_found"), (429, "rate_limited"), (500, "upstream_error"),
            (502, "upstream_error"), (503, "upstream_error"), (504, "upstream_error"),
            (302, "invalid_response"), (403, "invalid_response"), (204, "invalid_response"),
        )]
        cases.extend((http_response(body=body), "invalid_response") for body in (
            b"<html>unavailable</html>", b"", b"null", b"[]",
            b'{"status":"ok","message-type":"work","message":[]}',
        ))
        # Test both a saved DOI and a new identifier: neither is permission to
        # create, overwrite or link any business record during failed lookup.
        for value in (INPUT, "10.1234/new"):
            for response, code in cases:
                with self.subTest(value=value, code=code, status=response.status_code):
                    with patch("requests.adapters.HTTPAdapter.send", return_value=response) as send:
                        with self.assertNumQueries(0):
                            with self.assertRaises(CrossrefLookupError) as caught:
                                fetch_metadata(value)
                    self.assertEqual(caught.exception.code, code)
                    self.assertEqual(caught.exception.input_value, value)
                    send.assert_called_once()
                    self.assertEqual(self.snapshot(), before)

    def test_transport_failures_and_invalid_input_leave_all_business_data_unchanged(self):
        before = self.snapshot()
        for value in (INPUT, "10.1234/new"):
            for exception in (requests.ConnectionError, requests.ConnectTimeout, requests.ReadTimeout,
                              requests.exceptions.ChunkedEncodingError):
                with self.subTest(value=value, exception=exception.__name__):
                    with patch("requests.adapters.HTTPAdapter.send", side_effect=exception(PRIVATE_DETAIL)) as send:
                        with self.assertNumQueries(0):
                            with self.assertRaises(CrossrefLookupError):
                                fetch_metadata(value)
                    send.assert_called_once()
                    self.assertEqual(self.snapshot(), before)
        with patch("requests.adapters.HTTPAdapter.send") as send:
            with self.assertNumQueries(0):
                with self.assertRaises(ValidationError):
                    fetch_metadata("https://example.org/private")
        send.assert_not_called()
        self.assertEqual(self.snapshot(), before)
