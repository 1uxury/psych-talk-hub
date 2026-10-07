"""Step 19: DOI identity, single decoding and no arbitrary request targets."""

from unittest.mock import patch
from urllib.parse import urlsplit

import requests
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from events.services.crossref import request_doi
from events.services.doi import INVALID_DOI_MESSAGE, normalize_doi


class DoiNormalizationTests(SimpleTestCase):
    def assert_invalid(self, values):
        for value in values:
            with self.subTest(value=repr(value)):
                with self.assertRaises(ValidationError) as error:
                    normalize_doi(value)
                self.assertEqual(error.exception.messages, [INVALID_DOI_MESSAGE])
                self.assertEqual(error.exception.code, "invalid_doi")

    def test_bare_link_case_whitespace_and_encoded_path_share_identity(self):
        for value in (
            "10.1234/ABC.Def", " \t10.1234/ABC.Def\n", "\u300010.1234/abc.def\u3000",
            "https://doi.org/10.1234/ABC.Def", " HTTPS://DOI.ORG/10.1234/ABC.Def ",
            "https://doi.org/%31%30%2E1234%2FABC%2EDef",
        ):
            with self.subTest(value=value):
                self.assertEqual(normalize_doi(value), "10.1234/abc.def")

    def test_registrant_accepts_four_and_nine_ascii_digits(self):
        for value in ("10.0000/a", "10.123456789/a"):
            self.assertEqual(normalize_doi(value), value)

    def test_empty_wrong_prefix_registrant_and_suffix_are_rejected(self):
        self.assert_invalid((
            None, 19, b"10.1234/a", "", " \t\n", "doi:10.1234/a", "11.1234/a",
            "10.123/a", "10.1234567890/a", "10.abcd/a", "10.１２３４/a",
            "10.1234", "10.1234/", "10.1234/ \t",
        ))

    def test_internal_whitespace_in_bare_and_link_input_is_rejected(self):
        self.assert_invalid((
            "10.1234/two words", "10.1234/two\twords", "10.1234/two\nwords",
            "10.1234/two\rwords", "10.1234/two\u00a0words",
            "https://doi.org/10.1234/two words", "https://doi.org/10.1234/two\nwords",
            "https://do\ti.org/10.1234/a", "\x00https://doi.org/10.1234/a",
        ))

    def test_other_schemes_hosts_and_ambiguous_authorities_are_rejected(self):
        self.assert_invalid((
            "http://doi.org/10.1234/a", "ftp://doi.org/10.1234/a",
            "https://dx.doi.org/10.1234/a", "https://example.org/10.1234/a",
            "https://doi.org.example.org/10.1234/a", "https://doi.org./10.1234/a",
            "https://doi%2eorg/10.1234/a", "https://127.0.0.1/10.1234/a",
            "https://[::1]/10.1234/a", "https://[doi.org/10.1234/a",
            "//doi.org/10.1234/a", "https:doi.org/10.1234/a",
            "https://doi.org\\example.org/10.1234/a",
        ))

    def test_credentials_and_every_explicit_port_are_rejected(self):
        self.assert_invalid((
            "https://user@doi.org/10.1234/a", "https://user:pass@doi.org/10.1234/a",
            "https://@doi.org/10.1234/a", "https://doi.org:443/10.1234/a",
            "https://doi.org:80/10.1234/a", "https://doi.org:/10.1234/a",
            "https://doi.org:invalid/10.1234/a", "https://doi.org:99999/10.1234/a",
        ))

    def test_query_fragment_and_empty_delimiters_are_rejected_on_links(self):
        self.assert_invalid((
            "https://doi.org/10.1234/a?x=1", "https://doi.org/10.1234/a#part",
            "https://doi.org/10.1234/a?", "https://doi.org/10.1234/a#",
            "https://doi.org/10.1234/a?#",
        ))

    def test_suffix_punctuation_and_plus_are_preserved(self):
        suffix = "ABC.(Def);/G:HI%2F?x=1#part.+"
        self.assertEqual(normalize_doi(" 10.1234/" + suffix + " "), "10.1234/" + suffix.lower())
        self.assertEqual(
            normalize_doi("https://doi.org/10.1234/ABC.%28Def%29%3B%2FG%3AHI%252F%3Fx%3D1%23part.%2B"),
            "10.1234/" + suffix.lower(),
        )

    def test_link_path_is_decoded_exactly_once_and_bare_input_is_not_decoded(self):
        self.assertEqual(normalize_doi("https://doi.org/10.1234/A%252FB"), "10.1234/a%2fb")
        self.assertEqual(normalize_doi("https://doi.org/10.1234/A%2520B"), "10.1234/a%20b")
        self.assertEqual(normalize_doi("10.1234/A%2FB"), "10.1234/a%2fb")
        self.assert_invalid(("https://doi.org/%2531%2530.1234/a",))

    def test_decoded_whitespace_invalid_utf8_and_missing_link_doi_are_rejected(self):
        self.assert_invalid((
            "https://doi.org/10.1234/a%20b", "https://doi.org/10.1234/a%09b",
            "https://doi.org/10.1234/a%0Ab", "https://doi.org/10.1234/a%C2%A0b",
            "https://doi.org/10.1234/a%20", "https://doi.org/%2010.1234/a",
            "https://doi.org/10.1234/%FF", "https://doi.org/", "https://doi.org",
            "https://doi.org//10.1234/a", "https://doi.org/10.1234/",
        ))


class CrossrefTargetTests(SimpleTestCase):
    def test_invalid_input_never_reaches_http_transport(self):
        with patch("events.services.crossref.requests.get") as get:
            for value in (
                None, "", "11.1234/a", "10.123/a", "10.1234567890/a",
                "10.１２３４/a", "10.1234/", "10.1234/two words",
                "https://doi.org/10.1234/two\nwords", "https://doi.org/10.1234/a%20b",
                "https://doi.org/%2531%2530.1234/a", "https://doi.org/10.1234/%FF",
                "http://doi.org/10.1234/a", "https://dx.doi.org/10.1234/a",
                "https://example.org/10.1234/a", "https://doi.org.example.org/10.1234/a",
                "https://doi.org./10.1234/a", "https://[doi.org/10.1234/a",
                "https://user:pass@doi.org/10.1234/a", "https://@doi.org/10.1234/a",
                "https://doi.org:443/10.1234/a", "https://doi.org:/10.1234/a",
                "https://doi.org/10.1234/a?x=1", "https://doi.org/10.1234/a#part",
                "https://doi.org/10.1234/a?", "https://doi.org/10.1234/a#",
            ):
                with self.subTest(value=repr(value)):
                    with self.assertRaises(ValidationError):
                        request_doi(value)
            get.assert_not_called()

    def test_fixed_target_encodes_the_entire_identifier(self):
        with patch("events.services.crossref.requests.get") as get:
            response = request_doi(" 10.1234/ABC;/https://example.org?x=1#part%2F+ ")
        self.assertIs(response, get.return_value)
        get.assert_called_once_with(
            "https://api.crossref.org/works/10.1234%2Fabc%3B%2Fhttps%3A%2F%2Fexample.org%3Fx%3D1%23part%252f%2B",
            headers={"Accept": "application/json", "User-Agent": "PsychTalkHub/0.1"},
            timeout=(3, 7), allow_redirects=False,
        )
        get.return_value.json.assert_not_called()

    def send_response(self, status=200, location=None):
        def send(request, **kwargs):
            response = requests.Response()
            response.status_code = status
            response.url = request.url
            response.request = request
            response._content = b"raw provider response"
            if location is not None:
                response.headers["Location"] = location
            return response
        return send

    def test_requests_preparation_keeps_punctuation_in_one_fixed_identifier(self):
        with patch("requests.adapters.HTTPAdapter.send", side_effect=self.send_response()) as send:
            response = request_doi("https://doi.org/10.1234/A%252FB%3Fx%3D1%23part%2B")
        with response:
            send.assert_called_once()
            request = send.call_args.args[0]
            self.assertEqual(request.method, "GET")
            self.assertEqual(request.url, "https://api.crossref.org/works/10.1234%2Fa%252fb%3Fx%3D1%23part%2B")
            self.assertEqual(urlsplit(request.url).netloc, "api.crossref.org")
            self.assertEqual(urlsplit(request.url).query, "")
            self.assertEqual(urlsplit(request.url).fragment, "")
            self.assertEqual(send.call_args.kwargs["timeout"], (3, 7))
            self.assertTrue(send.call_args.kwargs["verify"])

    def test_cross_host_local_and_same_host_redirects_make_only_one_request(self):
        for status in (301, 302, 303, 307, 308):
            for location in (
                "https://example.org/private", "//example.org/private",
                "http://127.0.0.1/private", "https://api.crossref.org/works/another",
            ):
                with self.subTest(status=status, location=location):
                    with patch("requests.adapters.HTTPAdapter.send", side_effect=self.send_response(status, location)) as send:
                        response = request_doi("10.1234/a")
                    with response:
                        send.assert_called_once()
                        self.assertEqual(send.call_args.args[0].url, "https://api.crossref.org/works/10.1234%2Fa")
                        self.assertEqual(response.status_code, status)
                        self.assertEqual(response.history, [])

    def test_provider_http_failures_are_raw_responses_without_retry(self):
        for status in (404, 429, 500, 503):
            with self.subTest(status=status):
                with patch("requests.adapters.HTTPAdapter.send", side_effect=self.send_response(status)) as send:
                    response = request_doi("10.1234/a")
                with response:
                    send.assert_called_once()
                    self.assertEqual(response.status_code, status)

    def test_connection_failure_is_not_retried_or_converted_in_step_19(self):
        with patch("requests.adapters.HTTPAdapter.send", side_effect=requests.ConnectionError) as send:
            with self.assertRaises(requests.ConnectionError):
                request_doi("10.1234/a")
        send.assert_called_once()
