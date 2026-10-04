"""Public reading endpoints; no public content-management operations."""

from django.db.models import Count, Prefetch
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer

from .models import Event, EventResource
from .serializers import EventDetailSerializer, EventListSerializer


class EventListView(ListAPIView):
    serializer_class = EventListSerializer
    authentication_classes = []
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]
    pagination_class = None
    filter_backends = []
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        return Event.objects.annotate(
            resource_count=Count("event_resources")
        ).order_by("id")


class EventDetailView(RetrieveAPIView):
    serializer_class = EventDetailSerializer
    authentication_classes = []
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]
    filter_backends = []
    http_method_names = ["get", "head", "options"]

    def get_queryset(self):
        return Event.objects.annotate(
            resource_count=Count("event_resources")
        ).prefetch_related(Prefetch(
            "event_resources",
            queryset=EventResource.objects.select_related("resource").order_by(
                "display_order", "id"
            ),
            to_attr="reading_links",
        ))
