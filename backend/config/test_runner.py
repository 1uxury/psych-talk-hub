"""Prevent the test runner from connecting to a production database."""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test.runner import DiscoverRunner


class IsolatedDatabaseRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        if settings.DJANGO_ENV == "production":
            raise ImproperlyConfigured("Tests cannot run with production configuration.")
        return super().setup_databases(**kwargs)
