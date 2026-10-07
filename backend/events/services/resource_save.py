"""Save reviewed DOI bibliography and its talk link together, without HTTP."""

from collections.abc import Mapping
from dataclasses import dataclass

from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import IntegrityError, transaction

from events.models import Event, EventResource, Resource

from .doi import normalize_doi


@dataclass(frozen=True)
class DoiSaveResult:
    resource: Resource
    association: EventResource
    resource_created: bool
    association_created: bool


def _is_identity_conflict(error, model):
    """Recognize only this model's DOI/pair uniqueness, never error text."""
    if model is Resource:
        fields, key, code = ("doi",), "doi", "unique"
        constraint = "events_resource_doi_key"
    else:
        fields, key, code = ("event", "resource"), NON_FIELD_ERRORS, "unique_together"
        constraint = "unique_event_resource"
    if isinstance(error, IntegrityError):
        cause = error.__cause__
        diagnostic = getattr(cause, "diag", None)
        return (
            getattr(cause, "sqlstate", None) == "23505"
            and getattr(diagnostic, "table_name", None) == model._meta.db_table
            and getattr(diagnostic, "constraint_name", None) == constraint
        )
    errors = getattr(error, "error_dict", {})
    return set(errors) == {key} and bool(errors[key]) and all(
        item.code == code
        and (item.params or {}).get("model_class") is model
        and (item.params or {}).get("unique_check") == fields
        for item in errors[key]
    )


def save_doi_to_event(
    *, event_id, doi, bibliography: Mapping | None = None,
    recommendation="", display_order=0,
):
    """Reuse current saved data, or validate/create bibliography and a link.

    The caller supplies a trusted target/DOI and reviewed bibliographic values;
    it must check permissions and preview state before calling. Only title,
    authors, year, original_url and resource_type may initialize a new Resource.
    Existing resources ignore all preview fields; existing links also ignore
    submitted recommendation/order. No form, session or Crossref call lives here.

    Each attempt joins a caller's transaction so later state-save failure rolls
    back both records. Only a verified DOI/pair uniqueness race is recovered,
    after rollback; all other errors propagate. Each identity is recovered at
    most once (up to three attempts), without HTTP or an unbounded retry loop.
    """
    normalized_doi = normalize_doi(doi)
    recovered = set()
    while True:
        saving_model = None
        try:
            with transaction.atomic():
                event = Event.objects.get(pk=event_id)
                resource = Resource.objects.filter(doi=normalized_doi).first()
                resource_created = resource is None
                if resource_created:
                    fields = bibliography if bibliography is not None else {}
                    resource = Resource(
                        doi=normalized_doi,
                        metadata_source=Resource.MetadataSource.CROSSREF,
                        **{
                            field: fields[field]
                            for field in ("title", "authors", "year", "original_url", "resource_type")
                            if field in fields
                        },
                    )
                    saving_model = Resource
                    resource.save()
                    saving_model = None

                association = EventResource.objects.filter(event=event, resource=resource).first()
                association_created = association is None
                if association_created:
                    association = EventResource(
                        event=event, resource=resource,
                        recommendation=recommendation, display_order=display_order,
                    )
                    saving_model = EventResource
                    association.save()
                    saving_model = None

                return DoiSaveResult(
                    resource=resource, association=association,
                    resource_created=resource_created, association_created=association_created,
                )
        except (IntegrityError, ValidationError) as error:
            # Never query a broken transaction, or return rolled-back instances.
            if (saving_model is None or saving_model in recovered
                    or not _is_identity_conflict(error, saving_model)):
                raise
            if saving_model is Resource:
                winner = Resource.objects.filter(doi=normalized_doi)
            else:
                winner = EventResource.objects.filter(event_id=event_id, resource__doi=normalized_doi)
            if not winner.exists():
                raise
            recovered.add(saving_model)
