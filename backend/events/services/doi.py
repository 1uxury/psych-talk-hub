"""Normalise administrator DOI input without network or database access."""

import re
from urllib.parse import unquote, urlsplit

from django.core.exceptions import ValidationError


INVALID_DOI_MESSAGE = "Enter a valid DOI or DOI link."
BARE_DOI = re.compile(r"10\.[0-9]{4,9}/\S+")


def normalize_doi(value):
    """Accept a bare identifier or a strict HTTPS doi.org link; decode links once."""
    if not isinstance(value, str):
        raise ValidationError(INVALID_DOI_MESSAGE, code="invalid_doi")
    doi = value.strip()
    if not doi.startswith("10."):
        # urlsplit removes tabs/newlines and leading controls instead of rejecting
        # them. Check the original text before parsing, including empty ?/# parts.
        if any(character.isspace() or ord(character) < 32 for character in doi):
            raise ValidationError(INVALID_DOI_MESSAGE, code="invalid_doi")
        try:
            link = urlsplit(doi)
            if (
                link.scheme.lower() != "https"
                or link.netloc.lower() != "doi.org"
                or "?" in doi
                or "#" in doi
                or not link.path.startswith("/")
            ):
                raise ValueError
            doi = unquote(link.path[1:], encoding="utf-8", errors="strict")
        except (ValueError, UnicodeError):
            raise ValidationError(INVALID_DOI_MESSAGE, code="invalid_doi") from None
    doi = doi.lower()
    if BARE_DOI.fullmatch(doi) is None:
        raise ValidationError(INVALID_DOI_MESSAGE, code="invalid_doi")
    return doi
