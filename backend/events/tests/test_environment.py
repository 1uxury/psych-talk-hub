"""Fail-closed settings checks, independent of database credentials and services."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings

from config.environment import load_environment
from config.test_runner import IsolatedDatabaseRunner


TEST_SECRET = "test-only-random-looking-key-never-use-for-real-config-2026"
LOCAL_URL = "postgresql://test_user:test_password@127.0.0.1:5433/psych_talk_dev"
PRODUCTION_URL = "postgresql://test_user:test_password@db.example.invalid/psych_talk_prod?sslmode=require"


class EnvironmentTests(SimpleTestCase):
    def configuration(self, changes=None):
        values = {
            "DJANGO_ENV": "test",
            "SECRET_KEY": TEST_SECRET,
            "DATABASE_URL": LOCAL_URL,
            "TEST_DATABASE_NAME": "test_psychtalk",
        }
        values.update(changes or {})
        with TemporaryDirectory() as directory, patch.dict(os.environ, values, clear=True):
            return load_environment(Path(directory))

    def test_local_configuration_has_separate_test_database_and_bounded_connection_wait(self):
        config = self.configuration()
        self.assertEqual(config["database"]["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(config["database"]["TEST"]["NAME"], "test_psychtalk")
        self.assertFalse(config["debug"])
        self.assertEqual(config["database"]["OPTIONS"]["connect_timeout"], 3)

    def test_test_database_cannot_share_name_with_development_database(self):
        for name in ("", "psych_talk_dev", "test_wrong-name"):
            with self.subTest(name=name), self.assertRaises(ImproperlyConfigured):
                self.configuration({"TEST_DATABASE_NAME": name})
        with self.assertRaises(ImproperlyConfigured):
            self.configuration({"DATABASE_URL": LOCAL_URL.replace("psych_talk_dev", "test_psychtalk")})

    def test_local_modes_cannot_connect_to_remote_database(self):
        for mode in ("development", "test"):
            with self.subTest(mode=mode), self.assertRaises(ImproperlyConfigured):
                self.configuration({"DJANGO_ENV": mode, "DATABASE_URL": PRODUCTION_URL})

    def test_invalid_modes_secrets_and_database_urls_fail_without_echoing_credentials(self):
        for changes in (
            {"DJANGO_ENV": "unknown"},
            {"SECRET_KEY": ""},
            {"SECRET_KEY": "x" * 60},
            {"DATABASE_URL": ""},
            {"DATABASE_URL": "sqlite:///db.sqlite3"},
            {"DATABASE_URL": "postgresql://user:private-sentinel@localhost:invalid/db"},
            {"DATABASE_URL": "postgresql://localhost/db"},
        ):
            with self.subTest(changes=list(changes)):
                with self.assertRaises(ImproperlyConfigured) as error:
                    self.configuration(changes)
                self.assertNotIn("private-sentinel", str(error.exception))

    def test_production_requires_secret_database_hosts_debug_disabled_and_tls(self):
        valid = {
            "DJANGO_ENV": "production",
            "DATABASE_URL": PRODUCTION_URL,
            "ALLOWED_HOSTS": "demo.example.invalid",
        }
        config = self.configuration(valid)
        self.assertFalse(config["debug"])
        self.assertIsNone(config["test_name"])
        for change in (
            {"SECRET_KEY": ""},
            {"DATABASE_URL": ""},
            {"ALLOWED_HOSTS": ""},
            {"ALLOWED_HOSTS": "*"},
            {"ALLOWED_HOSTS": ".example.invalid"},
            {"DEBUG": "True"},
            {"DATABASE_URL": PRODUCTION_URL.replace("?sslmode=require", "")},
            {"DATABASE_URL": PRODUCTION_URL.replace("sslmode=require", "sslmode=disable")},
        ):
            with self.subTest(change=list(change)), self.assertRaises(ImproperlyConfigured):
                self.configuration({**valid, **change})

    def test_production_does_not_read_local_env_and_process_values_take_precedence(self):
        with TemporaryDirectory() as directory:
            base_dir = Path(directory)
            for filename in (".env", ".env.test"):
                (base_dir / filename).write_text(
                    f"SECRET_KEY={TEST_SECRET}\nDATABASE_URL={LOCAL_URL}\nTEST_DATABASE_NAME=test_psychtalk\n",
                    encoding="utf-8",
                )
            with patch.dict(os.environ, {"DJANGO_ENV": "production"}, clear=True):
                with self.assertRaises(ImproperlyConfigured):
                    load_environment(base_dir)
            process_secret = TEST_SECRET + "-process-override"
            with patch.dict(os.environ, {"DJANGO_ENV": "test", "SECRET_KEY": process_secret}, clear=True):
                config = load_environment(base_dir)
                self.assertEqual(config["secret"], process_secret)

    @override_settings(DJANGO_ENV="production")
    def test_production_test_runner_refuses_before_opening_database(self):
        with patch("django.test.runner.DiscoverRunner.setup_databases") as setup:
            with self.assertRaises(ImproperlyConfigured):
                IsolatedDatabaseRunner().setup_databases()
            setup.assert_not_called()
