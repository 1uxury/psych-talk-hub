"""Small readiness probe: check this application and PostgreSQL, never Crossref."""

from django.db import DatabaseError, connection
from django.http import JsonResponse


def healthz(request):
    if request.method not in {"GET", "HEAD"}:
        response = JsonResponse({"detail": "Method not allowed."}, status=405)
        response["Allow"] = "GET, HEAD"
    else:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                ready = cursor.fetchone() == (1,)
        except DatabaseError:
            ready = False
        response = JsonResponse(
            {"status": "ok"} if ready else {"detail": "Service unavailable."},
            status=200 if ready else 503,
        )
    response["Cache-Control"] = "no-store"
    return response
