"""Public output fields defined by the technology stack's API contract."""

from datetime import timezone

from rest_framework import serializers

from .models import Event, EventResource


class EventListSerializer(serializers.ModelSerializer):
    starts_at = serializers.DateTimeField(
        format="iso-8601", default_timezone=timezone.utc, read_only=True
    )
    resource_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = (
            "id", "title", "description", "topic", "starts_at", "speaker",
            "is_example", "resource_count",
        )
        read_only_fields = fields


class EventResourceSerializer(serializers.ModelSerializer):
    association_id = serializers.IntegerField(source="id", read_only=True)
    resource_id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(source="resource.title", read_only=True)
    authors = serializers.CharField(source="resource.authors", read_only=True)
    year = serializers.IntegerField(source="resource.year", allow_null=True, read_only=True)
    original_url = serializers.URLField(source="resource.original_url", read_only=True)
    doi = serializers.CharField(source="resource.doi", allow_null=True, read_only=True)
    resource_type = serializers.CharField(source="resource.resource_type", read_only=True)
    metadata_source = serializers.CharField(source="resource.metadata_source", read_only=True)

    class Meta:
        model = EventResource
        fields = (
            "association_id", "resource_id", "title", "authors", "year",
            "original_url", "doi", "resource_type", "metadata_source",
            "recommendation", "display_order",
        )
        read_only_fields = fields


class EventDetailSerializer(EventListSerializer):
    resources = EventResourceSerializer(source="reading_links", many=True, read_only=True)

    class Meta(EventListSerializer.Meta):
        fields = EventListSerializer.Meta.fields + ("resources",)
        read_only_fields = fields
