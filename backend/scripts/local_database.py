"""Manage only the ignored, project-local PostgreSQL 17 instance on Windows."""

import argparse
import secrets
import socket
import subprocess
from pathlib import Path

import psycopg
from psycopg import sql


REPOSITORY = Path(__file__).resolve().parents[2]
BACKEND = REPOSITORY / "backend"
LOCAL = REPOSITORY / ".tools" / "postgres17"
BIN = LOCAL / "pgsql" / "bin"
DATA = LOCAL / "data"
PORT = 5433


def run_tool(name, *arguments):
    return subprocess.run(
        [str(BIN / f"{name}.exe"), *map(str, arguments)],
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def start():
    run_tool("pg_ctl", "-D", DATA, "-l", LOCAL / "server.log", "-w", "start")


def initialise():
    if DATA.exists() or any((BACKEND / name).exists() for name in (".env", ".env.test")):
        raise RuntimeError("Existing data/configuration detected; init refuses to overwrite it.")
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", PORT))
    admin_password = secrets.token_urlsafe(40)
    application_password = secrets.token_urlsafe(40)
    password_file = LOCAL / "init.password"
    password_file.write_text(admin_password, encoding="utf-8")
    # Recovery information is local-only and excluded by the .tools/ ignore rule.
    (LOCAL / "admin.env").write_text(
        f"DATABASE_URL=postgresql://psychtalk_local_admin:{admin_password}@127.0.0.1:{PORT}/postgres\n",
        encoding="utf-8",
    )
    try:
        run_tool(
            "initdb", "-D", DATA, "-U", "psychtalk_local_admin",
            "--pwfile", password_file, "--auth=scram-sha-256", "--encoding=UTF8", "--locale=C",
        )
    finally:
        password_file.unlink(missing_ok=True)
    with (DATA / "postgresql.conf").open("a", encoding="utf-8") as config:
        config.write(f"\n# PsychTalk Hub isolated local instance\nlisten_addresses = '127.0.0.1'\nport = {PORT}\n")
    start()
    with psycopg.connect(
        host="127.0.0.1", port=PORT, dbname="postgres", user="psychtalk_local_admin",
        password=admin_password, autocommit=True,
    ) as connection:
        connection.execute(
            sql.SQL("CREATE ROLE {} LOGIN CREATEDB NOSUPERUSER NOCREATEROLE PASSWORD {}").format(
                sql.Identifier("psychtalk_dev"), sql.Literal(application_password),
            )
        )
        connection.execute(
            sql.SQL("CREATE DATABASE {} OWNER {} TEMPLATE template0 ENCODING 'UTF8'").format(
                sql.Identifier("psych_talk_dev"), sql.Identifier("psychtalk_dev"),
            )
        )
    database_url = f"postgresql://psychtalk_dev:{application_password}@127.0.0.1:{PORT}/psych_talk_dev"
    for filename, debug in ((".env", "True"), (".env.test", "False")):
        with (BACKEND / filename).open("x", encoding="utf-8") as env_file:
            env_file.write(
                f"SECRET_KEY={secrets.token_urlsafe(64)}\nDATABASE_URL={database_url}\n"
                f"TEST_DATABASE_NAME=test_psychtalk\nDEBUG={debug}\n"
                "ALLOWED_HOSTS=localhost,127.0.0.1,[::1]\n"
            )
    print("Local PostgreSQL initialised on 127.0.0.1:5433; private environment files created.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("init", "start", "stop", "status"))
    action = parser.parse_args().action
    if not (BIN / "pg_ctl.exe").is_file():
        parser.error("Extract the PostgreSQL 17 Windows binary archive into .tools/postgres17 first.")
    try:
        if action == "init":
            initialise()
        elif action == "start":
            start()
        elif action == "stop":
            run_tool("pg_ctl", "-D", DATA, "-m", "fast", "-w", "stop")
        else:
            run_tool("pg_ctl", "-D", DATA, "status")
    except (OSError, RuntimeError, subprocess.CalledProcessError, psycopg.Error):
        parser.exit(1, "Local database operation failed; inspect local files/logs. No credentials are printed.\n")


if __name__ == "__main__":
    main()
