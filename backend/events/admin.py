"""Talks, shared bibliography, per-talk reading and DOI import management."""

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.widgets import AdminSplitDateTime
from django.core.exceptions import PermissionDenied
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import Event, EventResource, Resource
from .doi_admin import doi_preview_view


class LondonDateTimeWidget(AdminSplitDateTime):
    def decompress(self, value):
        with timezone.override("Europe/London"):
            return super().decompress(value)


class LondonDateTimeField(forms.SplitDateTimeField):
    def clean(self, value):
        with timezone.override("Europe/London"):
            return super().clean(value)


class EventAdminForm(forms.ModelForm):
    starts_at = LondonDateTimeField(
        label="Start time (Europe/London)",
        help_text="Enter London local time (GMT in winter, BST in summer).",
        widget=LondonDateTimeWidget,
    )

    class Meta:
        model = Event
        fields = ("title", "description", "topic", "starts_at", "speaker", "is_example")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    fields = (*EventAdminForm.Meta.fields, "public_page", "doi_import")
    readonly_fields = ("public_page", "doi_import")
    list_display = ("title", "starts_at", "speaker", "is_example", "public_page")
    search_fields = ("title", "topic", "speaker")
    ordering = ("starts_at", "id")
    delete_confirmation_template = "admin/events/event/delete_confirmation.html"
    delete_selected_confirmation_template = "admin/events/event/delete_selected_confirmation.html"

    def get_urls(self):
        return [
            path("<int:event_id>/doi/", self.admin_site.admin_view(self.doi_view), name="events_event_doi_lookup"),
            path("<int:event_id>/doi/<str:preview_id>/", self.admin_site.admin_view(self.doi_view), name="events_event_doi_preview"),
        ] + super().get_urls()

    def doi_view(self, request, event_id, preview_id=None):
        return doi_preview_view(self, request, event_id, preview_id)

    @admin.display(description="DOI reading")
    def doi_import(self, obj):
        if not obj.pk:
            return "Save this talk before importing reading."
        return format_html('<a href="{}">Import reading by DOI</a>', reverse("admin:events_event_doi_lookup", args=[obj.pk]))

    def view_on_site(self, obj):
        # Django serves this declared page; React reads its data through the API.
        return f"/events/{obj.pk}"

    @admin.display(description="Public page")
    def public_page(self, obj):
        if not obj.pk:
            return "Save this talk to get its public address."
        return format_html('<a href="{}">View public talk</a>', self.view_on_site(obj))

    def response_add(self, request, obj, post_url_continue=None):
        response = super().response_add(request, obj, post_url_continue)
        self.message_user(request, self.public_page(obj), messages.SUCCESS)
        return response

    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        self.message_user(request, self.public_page(obj), messages.SUCCESS)
        return response

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj) and request.user.has_perm(
            "events.delete_eventresource"
        )

    def delete_model(self, request, obj):
        if not self.has_delete_permission(request, obj):
            raise PermissionDenied
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        if not self.has_delete_permission(request):
            raise PermissionDenied
        super().delete_queryset(request, queryset)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    change_form_template = "admin/events/resource/change_form.html"
    fields = ("title", "authors", "year", "original_url", "resource_type", "doi", "metadata_source")
    readonly_fields = ("doi", "metadata_source")
    list_display = ("title", "authors", "year", "resource_type", "metadata_source")
    search_fields = ("title", "authors", "doi")
    ordering = ("title", "id")
    actions = None

    # Manual creation retains the model's manual source; edits cannot forge it.
    # Forbid even unlinked Resource deletion and even superuser requests.
    def has_delete_permission(self, request, obj=None):
        return False

    def delete_model(self, request, obj):
        raise PermissionDenied

    def delete_queryset(self, request, queryset):
        raise PermissionDenied


@admin.register(EventResource)
class EventResourceAdmin(admin.ModelAdmin):
    fields = ("event", "resource", "recommendation", "display_order")
    list_display = ("event", "resource", "display_order", "recommendation")
    list_filter = ("event",)
    list_select_related = ("event", "resource")
    search_fields = ("event__title", "resource__title")
    ordering = ("display_order", "id")
    actions = None
    delete_confirmation_template = "admin/events/eventresource/delete_confirmation.html"

    def has_add_permission(self, request):
        return (
            super().has_add_permission(request)
            and request.user.has_perm("events.change_event")
            and request.user.has_perm("events.view_resource")
        )

    def get_readonly_fields(self, request, obj=None):
        # Editing reading context cannot silently move a link to another talk.
        return ("event", "resource") if obj else ()
