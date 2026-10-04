"""Talks, shared bibliography and ordered reading links for each talk."""

from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
    URLValidator,
)
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone


class Event(models.Model):
    title = models.CharField(
        max_length=255,
        validators=[RegexValidator(r"\S", "Enter a title containing non-whitespace text.")],
    )
    description = models.TextField(blank=True, default="")
    topic = models.CharField(max_length=100, blank=True, default="")
    starts_at = models.DateTimeField()
    speaker = models.CharField(max_length=255, blank=True, default="")
    is_example = models.BooleanField(default=False)
    seed_key = models.CharField(max_length=100, blank=True, null=True, unique=True, default=None)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(title__regex=r"\S"),
                name="event_title_has_text",
            ),
            models.CheckConstraint(
                condition=models.Q(seed_key__isnull=True) | models.Q(seed_key__regex=r"\S"),
                name="event_seed_key_null_or_text",
            ),
        ]

    def clean(self):
        super().clean()
        if self.seed_key is not None:
            self.seed_key = self.seed_key.strip() or None
        if isinstance(self.starts_at, datetime) and timezone.is_naive(self.starts_at):
            raise ValidationError({"starts_at": "Provide a timezone-aware start time."})

    def save(self, *args, **kwargs):
        # ORM saves must enforce the same input rules as future Admin forms.
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Resource(models.Model):
    class ResourceType(models.TextChoices):
        RESEARCH_PAPER = "research_paper", "Research paper"
        ARTICLE = "article", "Article / web resource"

    class MetadataSource(models.TextChoices):
        CROSSREF = "crossref", "Crossref"
        MANUAL = "manual", "Manual"

    title = models.CharField(
        max_length=500,
        validators=[RegexValidator(r"\S", "Enter a title containing non-whitespace text.")],
    )
    authors = models.TextField(blank=True, default="")
    year = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        default=None,
        validators=[MinValueValidator(1), MaxValueValidator(9999)],
    )
    original_url = models.URLField(
        max_length=2048,
        validators=[URLValidator(schemes=["http", "https"])],
    )
    doi = models.CharField(max_length=2048, blank=True, null=True, unique=True, default=None)
    resource_type = models.CharField(
        max_length=20, choices=ResourceType.choices, default=ResourceType.ARTICLE
    )
    metadata_source = models.CharField(
        max_length=10, choices=MetadataSource.choices, default=MetadataSource.MANUAL
    )
    seed_key = models.CharField(max_length=100, blank=True, null=True, unique=True, default=None)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(title__regex=r"\S"),
                name="resource_title_has_text",
            ),
            models.CheckConstraint(
                condition=models.Q(year__isnull=True) | models.Q(year__gte=1, year__lte=9999),
                name="resource_year_in_range",
            ),
            models.CheckConstraint(
                condition=models.Q(original_url__iregex=r"^https?://[^[:space:]]+$"),
                name="resource_url_http_scheme",
            ),
            models.CheckConstraint(
                condition=models.Q(doi__isnull=True)
                | (
                    models.Q(doi__regex=r"^10\.[0-9]{4,9}/[^[:space:]]+$")
                    & models.Q(doi=Lower("doi"))
                ),
                name="resource_doi_canonical_or_null",
            ),
            models.CheckConstraint(
                condition=models.Q(resource_type__in=["research_paper", "article"]),
                name="resource_type_known",
            ),
            models.CheckConstraint(
                condition=models.Q(metadata_source__in=["crossref", "manual"]),
                name="resource_source_known",
            ),
            models.CheckConstraint(
                condition=models.Q(seed_key__isnull=True) | models.Q(seed_key__regex=r"\S"),
                name="resource_seed_null_or_text",
            ),
        ]

    def clean(self):
        super().clean()
        if self.seed_key is not None:
            self.seed_key = self.seed_key.strip() or None
        if self.doi is not None:
            self.doi = self.doi.strip().lower() or None
        if self.doi is not None:
            # Store bare identifiers only; DOI-link parsing belongs to step 19.
            try:
                RegexValidator(
                    r"\A10\.[0-9]{4,9}/\S+\Z", "Enter a valid bare DOI."
                )(self.doi)
            except ValidationError as error:
                raise ValidationError({"doi": error.messages}) from error

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class EventResource(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="event_resources"
    )
    resource = models.ForeignKey(
        Resource, on_delete=models.PROTECT, related_name="event_resources"
    )
    recommendation = models.TextField(blank=True, default="")
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ["display_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["event", "resource"], name="unique_event_resource"
            ),
        ]

    def clean(self):
        super().clean()
        if self.recommendation is None:
            raise ValidationError({
                "recommendation": "Use an empty string for no recommendation."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.event} — {self.resource}"
