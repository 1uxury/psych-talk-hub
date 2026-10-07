"""Keep API errors JSON and safe without changing Admin or public page errors."""

import logging

from django.http import Http404, JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.common import no_append_slash
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


def is_api_request(request):
    return request.path_info == "/api" or request.path_info.startswith("/api/")


@csrf_exempt
@no_append_slash
def api_not_found(request, unmatched_path=""):
    # This fallback has no reads or writes, even for unsupported path/method pairs.
    return JsonResponse({"detail": "Not found."}, status=404)


class ApiErrorMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if not is_api_request(request):
            return None
        if isinstance(exception, Http404):
            return api_not_found(request)
        # Record only the category, never exception text, SQL, secrets or a traceback.
        logger.error("API request failed (%s).", type(exception).__name__)
        return JsonResponse({"detail": "Internal server error."}, status=500)

    def process_response(self, request, response):
        # Also sanitise failures produced outside the view (e.g. other middleware).
        if is_api_request(request) and response.status_code == 500:
            return JsonResponse({"detail": "Internal server error."}, status=500)
        return response
