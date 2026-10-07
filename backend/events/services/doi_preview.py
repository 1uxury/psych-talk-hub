"""Trusted, per-tab DOI previews; no business writes and no network under locks."""

from copy import deepcopy
from dataclasses import asdict
from math import isfinite
from secrets import token_hex

from django.contrib.auth import HASH_SESSION_KEY, SESSION_KEY
from django.contrib.sessions.models import Session
from django.db import transaction
from django.utils import timezone

from config.session_backend import PREVIEW_KEY
from events.models import Resource
from .crossref import fetch_metadata
from .doi import normalize_doi


INVALID_PREVIEW = "This preview is no longer valid. Fetch metadata again."
BIBLIOGRAPHY_FIELDS = ("title", "authors", "year", "original_url", "resource_type")


class InvalidPreview(Exception):
    def __init__(self):
        super().__init__(INVALID_PREVIEW)


def _session_data(request, *, lock=False, user=None):
    user = user or request.user
    key = request.session.session_key
    rows = Session.objects.select_for_update() if lock else Session.objects
    row = rows.filter(session_key=key, expire_date__gt=timezone.now()).first()
    if row is None:
        raise InvalidPreview
    data = request.session.decode(row.session_data)
    if (
        data.get(SESSION_KEY) != str(user.pk)
        or data.get(HASH_SESSION_KEY) != user.get_session_auth_hash()
    ):
        raise InvalidPreview
    return row, data


def _get_state(request, data, event_id, preview_id, *, statuses=("active",)):
    previews = data.get(PREVIEW_KEY, {})
    state = previews.get(preview_id) if isinstance(previews, dict) else None
    if (
        not isinstance(state, dict)
        or state.get("user_id") != request.user.pk
        or state.get("session_key") != request.session.session_key
        or state.get("event_id") != event_id
        or state.get("status") not in statuses
        or type(state.get("expires_at")) not in (int, float)
        or not isfinite(state["expires_at"])
        or not isinstance(state.get("doi"), str)
        or not state["doi"]
        or not isinstance(state.get("bibliography"), dict)
        or timezone.now().timestamp() >= state.get("expires_at", 0)
    ):
        raise InvalidPreview
    return state


def load_preview(request, event_id, preview_id):
    _, data = _session_data(request)
    return deepcopy(_get_state(request, data, event_id, preview_id, statuses=("active", "saved")))


def create_preview(request, event_id, input_value):
    doi = normalize_doi(input_value)
    resource = Resource.objects.filter(doi=doi).first()
    if resource is not None:
        bibliography = {field: getattr(resource, field) for field in BIBLIOGRAPHY_FIELDS}
        needs_review = False
    else:
        metadata = fetch_metadata(doi)
        converted = asdict(metadata)
        bibliography = {field: converted[field] for field in BIBLIOGRAPHY_FIELDS}
        needs_review = metadata.needs_review
    # Lifetime begins at successful loading, before waiting for the row lock.
    loaded_at = timezone.now().timestamp()
    preview_id = token_hex(24)
    state = {
        "user_id": request.user.pk, "session_key": request.session.session_key,
        "event_id": event_id, "doi": doi, "input_value": input_value,
        "bibliography": bibliography, "existing_resource_id": resource.pk if resource else None,
        "needs_review": needs_review, "loaded_at": loaded_at,
        "expires_at": loaded_at + 15 * 60, "status": "active",
    }
    with transaction.atomic():
        row, data = _session_data(request, lock=True)
        previews = data.setdefault(PREVIEW_KEY, {})
        previews[preview_id] = state
        row.session_data = request.session.encode(data)
        row.save(update_fields=["session_data"])
    return preview_id


def cancel_preview(request, event_id, preview_id):
    with transaction.atomic():
        row, data = _session_data(request, lock=True)
        state = _get_state(request, data, event_id, preview_id)
        state["status"] = "cancelled"
        row.session_data = request.session.encode(data)
        row.save(update_fields=["session_data"])
