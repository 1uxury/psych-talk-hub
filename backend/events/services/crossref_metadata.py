"""Convert a Crossref work to bibliography for review, without I/O or saving."""

from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from .doi import normalize_doi


validate_original_url = URLValidator(schemes=["http", "https"])


@dataclass(frozen=True)
class CrossrefMetadata:
    title: str
    authors: str
    year: int | None
    original_url: str
    doi: str
    resource_type: str
    metadata_source: str = "crossref"

    @property
    def missing_required_fields(self):
        """Fields an administrator must supply/correct before model validation."""
        fields = []
        if not self.title or len(self.title) > 500:
            fields.append("title")
        if not self.original_url:
            fields.append("original_url")
        return tuple(fields)

    @property
    def needs_review(self):
        # Optional omissions deserve the incomplete-metadata notice too, but
        # authors/year remain optional and do not block later confirmation.
        return bool(self.missing_required_fields or not self.authors or self.year is None)


def _text(value):
    return value.strip() if isinstance(value, str) else ""


def _title(work):
    titles = work.get("title")
    if isinstance(titles, list):
        for value in titles:
            title = _text(value)
            if title:
                return title
    return ""


def _authors(work):
    authors = work.get("author")
    names = []
    if isinstance(authors, list):
        for author in authors:
            if not isinstance(author, dict):
                continue
            personal = " ".join(
                part for part in (_text(author.get("given")), _text(author.get("family")))
                if part
            )
            name = personal or _text(author.get("name"))
            if name:
                names.append(name)
    return "; ".join(names)


def _year(work):
    for field in ("published-print", "published-online", "issued"):
        date = work.get(field)
        if not isinstance(date, dict):
            continue
        parts = date.get("date-parts")
        if not isinstance(parts, list) or not parts or not isinstance(parts[0], list) or not parts[0]:
            continue
        year = parts[0][0]
        # JSON booleans are Python ints; neither they nor numeric strings/floats
        # are publication years. The first date is the start of a date range.
        if type(year) is int and 1 <= year <= 9999:
            return year
    return None


def _original_url(work):
    url = _text(work.get("URL"))
    if len(url) > 2048 or any(ord(character) < 32 for character in url):
        return ""
    try:
        validate_original_url(url)
    except ValidationError:
        return ""
    return url


def convert_work(value, work):
    """Use the requested DOI identity and only the card's bibliographic fields.

    Missing/invalid required metadata stays incomplete; never fabricate a title
    or resolver URL. The caller must review and run model/form validation before
    saving. The provider's DOI, abstract, links and other fields are not imported.
    """
    doi = normalize_doi(value)
    if not isinstance(work, dict):
        raise ValueError("Expected a Crossref work object.")
    return CrossrefMetadata(
        title=_title(work),
        authors=_authors(work),
        year=_year(work),
        original_url=_original_url(work),
        doi=doi,
        resource_type=(
            "research_paper" if work.get("type") in ("journal-article", "proceedings-article")
            else "article"
        ),
    )
