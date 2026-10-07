"""Confirm trusted DOI state and its result in one short database transaction."""

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import transaction

from events.doi_forms import DoiReviewForm
from events.doi_permissions import can_import
from events.models import Event, EventResource, Resource
from config.session_backend import PREVIEW_KEY

from .doi_preview import BIBLIOGRAPHY_FIELDS, InvalidPreview, _get_state, _session_data
from .resource_save import DoiSaveResult, save_doi_to_event


class InvalidDetails(Exception):
    def __init__(self, form):
        self.form = form
        super().__init__("Review the form errors before saving.")


def saved_result(state, event_id, *, lock=False):
    result = state.get("result")
    if not isinstance(result, dict) or any(
        type(result.get(field)) is not int or result[field] <= 0
        for field in ("association_id", "resource_id")
    ):
        raise InvalidPreview
    rows = EventResource.objects.select_related("resource")
    if lock:
        rows = rows.select_for_update(of=("self",))
    association = rows.filter(
        pk=result.get("association_id"), event_id=event_id,
        resource_id=result.get("resource_id"), resource__doi=state.get("doi"),
    ).first()
    if association is None:
        # A removed result must never be recreated by replaying an old form.
        raise InvalidPreview
    return DoiSaveResult(
        association.resource, association,
        result.get("resource_created", False), result.get("association_created", False),
    )


def confirm_preview(request, event_id, preview_id, submitted):
    with transaction.atomic():
        # Fresh identity/permissions, even if this request cached them earlier.
        user = get_user_model().objects.filter(pk=request.user.pk).first()
        if user is None or not can_import(user):
            raise PermissionDenied
        row, data = _session_data(request, lock=True, user=user)
        state = _get_state(request, data, event_id, preview_id, statuses=("active", "saved"))
        Event.objects.select_for_update().get(pk=event_id)
        # Lock waits and form edits never extend the original deadline.
        _get_state(request, data, event_id, preview_id, statuses=("active", "saved"))
        if state["status"] == "saved":
            return saved_result(state, event_id, lock=True)
        resource = Resource.objects.filter(doi=state["doi"]).first()
        if resource is None and not user.has_perm("events.add_resource"):
            raise PermissionDenied
        bibliography = (
            {field: getattr(resource, field) for field in BIBLIOGRAPHY_FIELDS}
            if resource else state["bibliography"]
        )
        form = DoiReviewForm(submitted, bibliography=bibliography, existing=resource is not None)
        if not form.is_valid():
            raise InvalidDetails(form)
        result = save_doi_to_event(
            event_id=event_id, doi=state["doi"], bibliography=form.cleaned_data,
            recommendation=form.cleaned_data["recommendation"],
            display_order=form.cleaned_data["display_order"],
        )
        _get_state(request, data, event_id, preview_id)
        state["status"] = "saved"
        state["result"] = {
            "resource_id": result.resource.pk, "association_id": result.association.pk,
            "resource_created": result.resource_created,
            "association_created": result.association_created,
        }
        data[PREVIEW_KEY][preview_id] = state
        row.session_data = request.session.encode(data)
        row.save(update_fields=["session_data"])
        return result
