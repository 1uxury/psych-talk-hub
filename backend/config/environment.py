"""Read environment-specific configuration without development fallbacks in production."""

import os
import re
from urllib.parse import urlsplit

import environ
from django.core.exceptions import ImproperlyConfigured


def load_environment(base_dir):
    mode = os.environ.get("DJANGO_ENV", "development")
    if mode not in {"development", "test", "production"}:
        raise ImproperlyConfigured("DJANGO_ENV must be development, test or production.")

    env = environ.Env()
    if mode != "production":
        env_file = base_dir / (".env.test" if mode == "test" else ".env")
        if env_file.is_file():
            env.read_env(env_file, overwrite=False)

    secret = env.str("SECRET_KEY", default="")
    if len(secret) < 50 or len(set(secret)) < 5 or secret.startswith("django-insecure-"):
        raise ImproperlyConfigured("SECRET_KEY must be an explicit, strong secret of at least 50 characters.")

    database_url = env.str("DATABASE_URL", default="")
    try:
        parsed = urlsplit(database_url)
        if parsed.scheme not in {"postgres", "postgresql", "psql"}:
            raise ValueError
        database = env.db_url_config(database_url)
    except (ValueError, TypeError, KeyError):
        raise ImproperlyConfigured("DATABASE_URL must be a valid PostgreSQL connection URL.") from None
    if not all(database.get(key) for key in ("NAME", "USER", "PASSWORD", "HOST")):
        raise ImproperlyConfigured("DATABASE_URL must include a database, user, password and host.")
    if database.get("ENGINE") != "django.db.backends.postgresql":
        raise ImproperlyConfigured("Only PostgreSQL is supported.")

    debug = env.bool("DEBUG", default=mode == "development")
    hosts = [host.strip() for host in env.list("ALLOWED_HOSTS", default=[]) if host.strip()]
    options = database.setdefault("OPTIONS", {})
    options["connect_timeout"] = 3
    database["CONN_MAX_AGE"] = 0

    test_name = None
    if mode == "production":
        if debug:
            raise ImproperlyConfigured("DEBUG must be disabled in production.")
        if not hosts or any("*" in host or host.startswith(".") for host in hosts):
            raise ImproperlyConfigured("Production requires explicit ALLOWED_HOSTS without wildcards.")
        if options.get("sslmode") not in {"require", "verify-ca", "verify-full"}:
            raise ImproperlyConfigured("Production DATABASE_URL must require TLS using sslmode.")
    else:
        if database["HOST"] not in {"localhost", "127.0.0.1", "::1"}:
            raise ImproperlyConfigured("Development and test databases must use the local isolated instance.")
        test_name = env.str("TEST_DATABASE_NAME", default="")
        if not re.fullmatch(r"test_[a-z0-9_]+", test_name) or test_name == database["NAME"]:
            raise ImproperlyConfigured("TEST_DATABASE_NAME must be a separate database beginning with test_.")
        database["TEST"] = {"NAME": test_name}
        if not hosts:
            hosts = ["localhost", "127.0.0.1", "[::1]"]
        if mode == "test":
            debug = False

    return {
        "mode": mode,
        "secret": secret,
        "debug": debug,
        "hosts": hosts,
        "database": database,
        "database_name": database["NAME"],
        "test_name": test_name,
    }
