"""Admin DOI lookup, review, confirmation and cancellation."""

import logging

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import DatabaseError
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from .doi_forms import DoiLookupForm, DoiReviewForm
from .doi_permissions import VIEW_PERMISSIONS, WRITE_PERMISSIONS, can_import
from .models import Event, Resource
from .services.crossref import CrossrefLookupError
from .services.doi import normalize_doi
from .services.doi_confirmation import InvalidDetails, confirm_preview, saved_result
from .services.doi_preview import (
    BIBLIOGRAPHY_FIELDS, InvalidPreview, cancel_preview, create_preview, load_preview,
)

logger = logging.getLogger(__name__)
LOOKUP_FAILURE_CODES = frozenset({
    "not_found", "rate_limited", "upstream_error", "invalid_response",
    "timeout", "connection_failed", "provider_unavailable",
})


def log_save_failure(error):
    logger.error("DOI confirmation failed (%s).", type(error).__name__)


def doi_preview_view(model_admin, request, event_id, preview_id=None):
    if request.method not in ("GET", "POST"):
        return HttpResponseNotAllowed(["GET", "POST"])
    if not request.user.has_perms(VIEW_PERMISSIONS):
        raise PermissionDenied
    if request.method == "POST" and not can_import(request.user):
        raise PermissionDenied
    event = Event.objects.filter(pk=event_id).first()
    lookup_url = reverse("admin:events_event_doi_lookup", args=[event_id])
    context = {
        **model_admin.admin_site.each_context(request), "opts": model_admin.model._meta,
        "title": "Import reading by DOI", "event": event, "lookup_url": lookup_url,
        "event_list_url": reverse("admin:events_event_changelist"),
        "lookup_form": DoiLookupForm(), "preview_id": preview_id,
    }

    def render(status=200):
        return TemplateResponse(request, "admin/events/event/doi_preview.html", context, status=status)

    if event is None:
        context["state_error"] = "This talk is no longer available."
        return render(404)
    context["event_url"] = reverse("admin:events_event_change", args=[event_id])
    if preview_id is None:
        if request.method == "POST":
            if request.POST.get("action") != "fetch":
                return HttpResponseNotAllowed(["GET", "POST"])
            form = context["lookup_form"] = DoiLookupForm(request.POST)
            if form.is_valid():
                doi = form.cleaned_data["doi"]
                # Check creation permission before any provider request.
                if (
                    not Resource.objects.filter(doi=normalize_doi(doi)).exists()
                    and not request.user.has_perm("events.add_resource")
                ):
                    raise PermissionDenied
                try:
                    identity = create_preview(request, event_id, doi)
                except CrossrefLookupError as error:
                    category = error.code if error.code in LOOKUP_FAILURE_CODES else "provider_unavailable"
                    logger.warning("DOI lookup failed (%s).", category)
                    form.add_error(None, error.message)
                    context["can_retry"] = error.can_retry
                except InvalidPreview as error:
                    context["state_error"] = str(error)
                else:
                    return redirect("admin:events_event_doi_preview", event_id, identity)
        return render()
    try:
        state = load_preview(request, event_id, preview_id)
        if request.method == "POST" and request.POST.get("action") == "cancel":
            cancel_preview(request, event_id, preview_id)
            return redirect(context["event_url"])
    except InvalidPreview as error:
        context["state_error"] = str(error)
        return render(400)
    resource = Resource.objects.filter(doi=state["doi"]).first()
    if state["status"] == "saved":
        try:
            if request.method == "POST":
                if request.POST.get("action") != "save":
                    raise InvalidPreview
                result = confirm_preview(request, event_id, preview_id, request.POST)
            else:
                result = saved_result(state, event_id)
        except InvalidPreview as error:
            context["state_error"] = str(error)
            return render(400)
        except Event.DoesNotExist:
            context["state_error"] = "This talk is no longer available."
            return render(404)
        except DatabaseError as error:
            log_save_failure(error)
            context["state_error"] = "We couldn't save this resource. Please try again."
            return render(503)
        if request.method == "POST":
            return redirect("admin:events_event_doi_preview", event_id, preview_id)
        context.update(
            result=result, public_url=f"/events/{event_id}",
            association_url=reverse("admin:events_eventresource_change", args=[result.association.pk]),
        )
        return render()
    existing = resource is not None
    bibliography = (
        {field: getattr(resource, field) for field in BIBLIOGRAPHY_FIELDS}
        if existing else state["bibliography"]
    )
    if request.method == "POST":
        if request.POST.get("action") not in ("review", "save"):
            context["state_error"] = "Choose Save to event, Check details or Cancel preview."
            return render(400)
        if not existing and not request.user.has_perm("events.add_resource"):
            raise PermissionDenied
    form = DoiReviewForm(
        request.POST if request.method == "POST" else None,
        bibliography=bibliography, existing=existing,
    )
    context.update(
        review_form=form, doi=state["doi"], existing=existing,
        needs_review=state["needs_review"] and not existing,
        resource_type_label=resource.get_resource_type_display() if resource else "",
    )
    if request.method == "POST" and form.is_valid():
        if request.POST.get("action") == "review":
            context["checked"] = True
        else:
            try:
                confirm_preview(request, event_id, preview_id, request.POST)
            except InvalidDetails as error:
                context["review_form"] = error.form
            except InvalidPreview as error:
                context["state_error"] = str(error)
                return render(400)
            except Event.DoesNotExist:
                context["state_error"] = "This talk is no longer available."
                return render(404)
            except (DatabaseError, ValidationError) as error:
                log_save_failure(error)
                form.add_error(None, "We couldn't save this resource. Please try again.")
            else:
                logger.info("DOI confirmation succeeded.")
                return redirect("admin:events_event_doi_preview", event_id, preview_id)
    return render()
