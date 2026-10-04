"""Root infrastructure, administration and public API routes."""
from django.contrib import admin
from django.urls import include, path

from .api_errors import api_not_found
from .health import healthz
from .public_pages import public_page

urlpatterns = [
    path("api/", include("events.urls")),
    path("api/", api_not_found, name="api-not-found"),
    path("api/<path:unmatched_path>", api_not_found),
    path("api", api_not_found),
    path("healthz/", healthz, name="healthz"),
    path("admin/", admin.site.urls),
    path("", public_page, name="public-home"),
    path("events/<int:event_id>", public_page, name="public-event"),
]
