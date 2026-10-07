"""Small readiness probe: check this application and PostgreSQL, never Crossref."""

import logging

from django.db import DatabaseError, connection
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def healthz(request):
    if request.method not in {"GET", "HEAD"}:
        response = JsonResponse({"detail": "Method not allowed."}, status=405)
        response["Allow"] = "GET, HEAD"
    else:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                ready = cursor.fetchone() == (1,)
        except DatabaseError as error:
            logger.warning("Readiness check failed (%s).", type(error).__name__)
            ready = False
        response = JsonResponse(
            {"status": "ok"} if ready else {"detail": "Service unavailable."},
            status=200 if ready else 503,
        )
    response["Cache-Control"] = "no-store"
    return response
