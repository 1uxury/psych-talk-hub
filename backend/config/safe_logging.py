"""Keep Django request/security logs useful without URL or exception payloads."""

import logging


class SafeRequestFilter(logging.Filter):
    def filter(self, record):
        if record.name == "django.request" or record.name.startswith("django.security"):
            status = getattr(record, "status_code", None)
            record.msg = "Request rejected." if record.name.startswith("django.security") else "Request failed."
            record.args = ()
            if type(status) is int:
                record.msg += " Status %s."
                record.args = (status,)
            # Tracebacks can contain SQL, credentials and submitted preview values.
            record.exc_info = None
            record.exc_text = None
            record.stack_info = None
        return True
