"""Step 04 acceptance: actual PostgreSQL, readiness failures and Admin entry."""

from unittest.mock import patch

from django.conf import settings
from django.db import OperationalError, connection
from django.test import TestCase


class InfrastructureTests(TestCase):
    def test_database_is_postgresql_17_and_separate_from_configured_database(self):
        self.assertEqual(connection.vendor, "postgresql")
        self.assertNotEqual(connection.settings_dict["NAME"], settings.CONFIGURED_DATABASE_NAME)
        self.assertEqual(connection.settings_dict["NAME"], connection.settings_dict["TEST"]["NAME"])
        with connection.cursor() as cursor:
            cursor.execute("SHOW server_version_num")
            version = int(cursor.fetchone()[0])
        self.assertGreaterEqual(version, 170000)
        self.assertLess(version, 180000)
        self.assertIn("django_session", connection.introspection.table_names())

    def test_health_checks_real_database_without_calling_external_services(self):
        with patch("requests.sessions.Session.request") as external_request:
            response = self.client.get("/healthz/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertEqual(response["Cache-Control"], "no-store")
        external_request.assert_not_called()

    def test_database_failure_returns_safe_unavailable_response(self):
        with patch("config.health.connection.cursor", side_effect=OperationalError("private-db-sentinel")):
            response = self.client.get("/healthz/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Service unavailable."})
        self.assertNotIn(b"private-db-sentinel", response.content)

    def test_health_head_has_no_body_and_unsafe_methods_do_not_query(self):
        response = self.client.head("/healthz/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")
        for method in ("post", "put", "patch", "delete", "options"):
            with self.subTest(method=method), patch("config.health.connection.cursor") as cursor:
                response = getattr(self.client, method)("/healthz/")
                self.assertEqual(response.status_code, 405)
                self.assertEqual(response["Allow"], "GET, HEAD")
                cursor.assert_not_called()

    def test_admin_login_is_available_without_creating_an_admin_account(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, "csrfmiddlewaretoken")
        response = self.client.get("/admin/")
        self.assertRedirects(response, "/admin/login/?next=/admin/", fetch_redirect_response=False)
