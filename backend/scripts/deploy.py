"""Free Render build/start entry; never seed data or initialise administrators."""

import argparse
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import subprocess
import sys


REPOSITORY = Path(__file__).resolve().parents[2]
BACKEND = REPOSITORY / "backend"
FRONTEND = REPOSITORY / "frontend"


class EntryAssets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("type") == "module":
            self.urls.append(attrs.get("src", ""))
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.urls.append(attrs.get("href", ""))


def check_artifacts(collected=False):
    """Fail before migrations if the entry references missing/wrong-path assets."""
    dist = FRONTEND / "dist"
    parser = EntryAssets()
    parser.feed((dist / "index.html").read_text(encoding="utf-8"))
    prefix = "/static/frontend/assets/"
    suffixes = set()
    for url in parser.urls:
        if not url.startswith(prefix):
            raise ValueError("Frontend entry has an unexpected asset URL.")
        filename = url[len(prefix):]
        if not filename or "/" in filename or "\\" in filename:
            raise ValueError("Frontend entry has an invalid asset filename.")
        asset = dist / "assets" / filename
        if not asset.is_file():
            raise ValueError("A built frontend asset is missing.")
        suffixes.add(asset.suffix)
        if collected and not (BACKEND / "staticfiles" / "frontend" / "assets" / filename).is_file():
            raise ValueError("A collected frontend asset is missing.")
    if not {".js", ".css"}.issubset(suffixes):
        raise ValueError("Frontend entry must reference built JavaScript and CSS.")
    if collected and not (BACKEND / "staticfiles" / "admin" / "css" / "base.css").is_file():
        raise ValueError("Collected Admin assets are missing.")


def run(arguments, directory):
    subprocess.run(arguments, cwd=directory, check=True)


def build():
    expected_node = (REPOSITORY / ".node-version").read_text().strip()
    manifest = json.loads((FRONTEND / "package.json").read_text())
    for command, expected in (("node", "v" + expected_node), ("npm", manifest["engines"]["npm"])):
        actual = subprocess.run(
            [command, "--version"], check=True, capture_output=True, text=True,
        ).stdout.strip()
        if actual != expected:
            raise ValueError("Build runtime does not match the repository pins.")
    run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], BACKEND)
    run([sys.executable, "-m", "pip", "check"], BACKEND)
    run(["npm", "ci", "--no-audit", "--no-fund"], FRONTEND)
    run(["npm", "run", "build"], FRONTEND)
    check_artifacts()
    run([sys.executable, "manage.py", "check"], BACKEND)
    run([sys.executable, "manage.py", "collectstatic", "--noinput"], BACKEND)
    check_artifacts(collected=True)


def start():
    if sys.platform != "linux":
        raise ValueError("Gunicorn startup is supported only on Linux.")
    port = os.environ.get("PORT", "10000")
    if not port.isascii() or not port.isdecimal() or not 1 <= int(port) <= 65535:
        raise ValueError("PORT must be an integer between 1 and 65535.")
    check_artifacts(collected=True)
    run([sys.executable, "manage.py", "check"], BACKEND)
    run([sys.executable, "manage.py", "migrate", "--noinput"], BACKEND)
    os.chdir(BACKEND)
    # exec replaces this process only after both preceding commands succeed.
    os.execv(sys.executable, [
        sys.executable, "-m", "gunicorn", "config.wsgi:application",
        "--bind", f"0.0.0.0:{port}", "--workers", "1",
        "--access-logfile", "-", "--error-logfile", "-",
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "start"))
    action = parser.parse_args().action
    try:
        if os.environ.get("DJANGO_ENV") != "production":
            raise ValueError("Deployment requires explicit production configuration.")
        expected_python = (REPOSITORY / ".python-version").read_text().strip()
        if ".".join(map(str, sys.version_info[:3])) != expected_python:
            raise ValueError("Python does not match the repository pin.")
        (build if action == "build" else start)()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        # Never print exception text, command arguments or environment values.
        print(f"Deployment stopped ({type(error).__name__}).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
