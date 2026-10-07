"""Browser image addresses; the server never downloads remote images."""

import re
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


def validate_cover_image_url(value):
    if not value:
        return
    if re.fullmatch(r"/static/events/posters/[a-z0-9-]+\.svg", value):
        return
    message = "Use an HTTPS image URL without credentials, or a bundled /static/events/posters/name.svg path."
    if re.search(r"[\s\\]", value):
        raise ValidationError(message)
    try:
        URLValidator(schemes=["https"])(value)
        parts = urlsplit(value)
        if parts.username is not None or parts.password is not None:
            raise ValidationError(message)
    except (ValidationError, ValueError) as error:
        raise ValidationError(message) from error
