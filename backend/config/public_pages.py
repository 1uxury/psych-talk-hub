"""Serve the built React entry only for the two declared public page routes."""

from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe


@never_cache
@require_safe
def public_page(request, event_id=None):
    # Event existence and loading states are handled by the existing JSON API.
    try:
        template = get_template("index.html")
    except TemplateDoesNotExist:
        return HttpResponse(
            "We couldn't load this page. Please try again.", status=503,
        )
    return HttpResponse(template.render({}, request))
