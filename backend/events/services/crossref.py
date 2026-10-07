"""Fixed-target bibliography lookup with safe failures; no persistence."""

from urllib.parse import quote

import requests

from .crossref_metadata import convert_work
from .doi import normalize_doi


CROSSREF_WORKS_URL = "https://api.crossref.org/works/"
NOT_FOUND_MESSAGE = "No publication was found for this DOI."
UNAVAILABLE_MESSAGE = (
    "We couldn't fetch publication details. Please try again or add the resource manually."
)


class CrossrefLookupError(Exception):
    """Safe message and recovery choices for a future bound Admin form.

    Keep the submitted value for correction/retry; never include it or provider
    details in the exception text. This does not store session or form state.
    """

    can_add_manually = True

    def __init__(self, code, input_value):
        self.code = code
        self.input_value = input_value
        self.message = NOT_FOUND_MESSAGE if code == "not_found" else UNAVAILABLE_MESSAGE
        super().__init__(self.message)

    @property
    def can_retry(self):
        # A 404 needs a corrected DOI or manual entry, rather than a retry of
        # the unchanged identifier. Other failures allow an explicit new fetch.
        return self.code != "not_found"


def request_doi(value):
    """Validate first and return the raw response without following redirects.

    This transport does not inspect JSON, map provider errors, retry, or persist
    anything. Its caller owns conversion and closing the response.
    """
    doi = normalize_doi(value)
    return requests.get(
        CROSSREF_WORKS_URL + quote(doi, safe=""),
        headers={"Accept": "application/json", "User-Agent": "PsychTalkHub/0.1"},
        timeout=(3, 7),
        allow_redirects=False,
    )


def fetch_metadata(value):
    """Fetch once, close the response, and map expected lookup failures safely.

    Invalid DOI input keeps the existing ValidationError, before any HTTP call.
    Incomplete bibliography is still a reviewable success, not a provider error.
    """
    doi = normalize_doi(value)
    try:
        with request_doi(doi) as response:
            if response.status_code == 404:
                raise CrossrefLookupError("not_found", value)
            if response.status_code == 429:
                raise CrossrefLookupError("rate_limited", value)
            if 500 <= response.status_code <= 599:
                raise CrossrefLookupError("upstream_error", value)
            if response.status_code != 200:
                raise CrossrefLookupError("invalid_response", value)
            try:
                payload = response.json()
            except (ValueError, RecursionError):
                raise CrossrefLookupError("invalid_response", value) from None
            if (
                not isinstance(payload, dict)
                or payload.get("status") != "ok"
                or payload.get("message-type") != "work"
                or not isinstance(payload.get("message"), dict)
            ):
                raise CrossrefLookupError("invalid_response", value)
            return convert_work(doi, payload["message"])
    except requests.Timeout:
        # ConnectTimeout is also a ConnectionError: classify timeouts first.
        raise CrossrefLookupError("timeout", value) from None
    except requests.ConnectionError:
        raise CrossrefLookupError("connection_failed", value) from None
    except requests.RequestException:
        raise CrossrefLookupError("provider_unavailable", value) from None
