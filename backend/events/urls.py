"""Public event list and detail API routes."""

from django.urls import path

from .views import EventDetailView, EventListView

app_name = "events"

urlpatterns = [
    path("events/", EventListView.as_view(), name="event-list"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event-detail"),
]
