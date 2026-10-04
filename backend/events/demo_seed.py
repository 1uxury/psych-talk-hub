"""Explicit, offline demo import; existing records are never updated."""

import json
from datetime import datetime, timedelta
from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from events.models import Event, EventResource, Resource


MANIFEST_PATH = Path(__file__).resolve().parent / "data" / "demo_reading.json"


def load_demo_manifest():
    with MANIFEST_PATH.open(encoding="utf-8") as manifest_file:
        return json.load(manifest_file)


def seed_demo_data(*, seed_at=None):
    """Fill missing records in one transaction, using one aware seed instant."""
    seed_at = timezone.now() if seed_at is None else seed_at
    if not isinstance(seed_at, datetime) or timezone.is_naive(seed_at):
        raise ValidationError("Provide a timezone-aware demo import instant.")
    manifest = load_demo_manifest()
    created_counts = {"events": 0, "resources": 0, "associations": 0}
    resources = {}

    with transaction.atomic():
        for entry in manifest["resources"]:
            candidate = Resource(**entry["fields"])
            # Normalise before identity lookup; existing bibliography stays untouched.
            candidate.full_clean(validate_unique=False, validate_constraints=False)
            if candidate.doi:
                identity = {"doi": candidate.doi}
            elif candidate.seed_key:
                identity = {"seed_key": candidate.seed_key}
            else:
                raise ValidationError("Demo resources require a DOI or stable seed key.")
            defaults = {
                field: getattr(candidate, field)
                for field in entry["fields"] if field not in identity
            }
            resource, created = Resource.objects.get_or_create(**identity, defaults=defaults)
            resources[entry["key"]] = resource
            created_counts["resources"] += int(created)

        for entry in manifest["events"]:
            event, created = Event.objects.get_or_create(
                seed_key=entry["seed_key"],
                defaults={
                    **entry["fields"],
                    "starts_at": seed_at + timedelta(days=entry["offset_days"]),
                },
            )
            created_counts["events"] += int(created)
            for reading in entry["reading"]:
                _, created = EventResource.objects.get_or_create(
                    event=event,
                    resource=resources[reading["resource"]],
                    defaults={
                        "recommendation": reading["recommendation"],
                        "display_order": reading["display_order"],
                    },
                )
                created_counts["associations"] += int(created)

    return created_counts
