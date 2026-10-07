"""Step 17: controlled deployment order; no subprocess or production DB access."""

from contextlib import redirect_stderr
from io import StringIO
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from unittest.mock import call, patch

from django.test import SimpleTestCase

from scripts import deploy


class DeploymentTests(SimpleTestCase):
    def test_build_uses_locks_and_collects_without_migrations_seeding_or_admin_creation(self):
        versions = [subprocess.CompletedProcess([], 0, "v24.14.0\n"),
                    subprocess.CompletedProcess([], 0, "11.9.0\n")]
        with patch.object(deploy.subprocess, "run", side_effect=versions), patch.object(
            deploy, "run",
        ) as run, patch.object(deploy, "check_artifacts") as artifacts:
            deploy.build()
        self.assertEqual(run.call_args_list, [
            call([deploy.sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], deploy.BACKEND),
            call([deploy.sys.executable, "-m", "pip", "check"], deploy.BACKEND),
            call(["npm", "ci", "--no-audit", "--no-fund"], deploy.FRONTEND),
            call(["npm", "run", "build"], deploy.FRONTEND),
            call([deploy.sys.executable, "manage.py", "check"], deploy.BACKEND),
            call([deploy.sys.executable, "manage.py", "collectstatic", "--noinput"], deploy.BACKEND),
        ])
        self.assertEqual(artifacts.call_args_list, [call(), call(collected=True)])

    def test_wrong_node_or_npm_stops_before_installation(self):
        for versions in (("v22.0.0",), ("v24.14.0", "10.0.0")):
            responses = [subprocess.CompletedProcess([], 0, value) for value in versions]
            with self.subTest(versions=versions), patch.object(
                deploy.subprocess, "run", side_effect=responses,
            ), patch.object(deploy, "run") as run:
                with self.assertRaises(ValueError):
                    deploy.build()
                run.assert_not_called()

    def test_build_command_failure_does_not_continue(self):
        versions = [subprocess.CompletedProcess([], 0, "v24.14.0"),
                    subprocess.CompletedProcess([], 0, "11.9.0")]
        with patch.object(deploy.subprocess, "run", side_effect=versions), patch.object(
            deploy, "run", side_effect=subprocess.CalledProcessError(1, ["private-sentinel"]),
        ) as run, patch.object(deploy, "check_artifacts") as artifacts:
            with self.assertRaises(subprocess.CalledProcessError):
                deploy.build()
        self.assertEqual(run.call_count, 1)
        artifacts.assert_not_called()

    def test_start_checks_then_migrates_before_replacing_process_with_one_worker(self):
        order = []
        with patch.object(deploy.sys, "platform", "linux"), patch.dict(os.environ, {"PORT": "10000"}), patch.object(
            deploy, "check_artifacts", side_effect=lambda **kwargs: order.append("assets"),
        ), patch.object(deploy, "run", side_effect=lambda args, directory: order.append(args[2])) as run, patch.object(
            deploy.os, "chdir",
        ) as chdir, patch.object(deploy.os, "execv", side_effect=lambda *args: order.append("exec")) as execute:
            deploy.start()
        self.assertEqual(order, ["assets", "check", "migrate", "exec"])
        self.assertEqual(run.call_args_list[-1], call(
            [deploy.sys.executable, "manage.py", "migrate", "--noinput"], deploy.BACKEND,
        ))
        chdir.assert_called_once_with(deploy.BACKEND)
        arguments = execute.call_args.args[1]
        self.assertIn("config.wsgi:application", arguments)
        self.assertEqual(arguments[arguments.index("--workers") + 1], "1")
        self.assertEqual(arguments[arguments.index("--bind") + 1], "0.0.0.0:10000")
        access_format = arguments[arguments.index("--access-logformat") + 1]
        self.assertEqual(access_format, "%(m)s %(s)s %(M)sms")
        # URLs/queries contain private preview IDs; access logs retain only metrics.
        for private_atom in ("%(r)s", "%(U)s", "%(q)s", "%(h)s", "%(u)s"):
            self.assertNotIn(private_atom, access_format)

    def test_check_or_migration_failure_never_launches_gunicorn(self):
        failure = subprocess.CalledProcessError(1, ["migrate"])
        for effects in ([failure], [None, failure]):
            with self.subTest(stage=len(effects)), patch.object(deploy.sys, "platform", "linux"), patch.dict(
                os.environ, {"PORT": "10000"},
            ), patch.object(deploy, "check_artifacts"), patch.object(deploy, "run", side_effect=effects), patch.object(
                deploy.os, "execv",
            ) as execute, patch.object(deploy.os, "chdir") as chdir:
                with self.assertRaises(subprocess.CalledProcessError):
                    deploy.start()
                execute.assert_not_called()
                chdir.assert_not_called()

    def test_missing_artifacts_never_runs_migrations(self):
        with patch.object(deploy.sys, "platform", "linux"), patch.dict(os.environ, {"PORT": "10000"}), patch.object(
            deploy, "check_artifacts", side_effect=ValueError("missing assets"),
        ), patch.object(deploy, "run") as run, patch.object(deploy.os, "execv") as execute:
            with self.assertRaises(ValueError):
                deploy.start()
        run.assert_not_called()
        execute.assert_not_called()

    def test_windows_and_invalid_ports_refuse_startup(self):
        for platform, port in (("win32", "10000"), ("linux", "0"), ("linux", "65536"),
                               ("linux", "abc"), ("linux", "10000;command")):
            with self.subTest(platform=platform, port=port), patch.object(deploy.sys, "platform", platform), patch.dict(
                os.environ, {"PORT": port},
            ), patch.object(deploy, "run") as run:
                with self.assertRaises(ValueError):
                    deploy.start()
                run.assert_not_called()

    def test_main_requires_production_and_pinned_python_without_echoing_errors(self):
        scenarios = (("development", (3, 13, 16)), ("production", (3, 12, 0)))
        for mode, version in scenarios:
            with self.subTest(mode=mode, version=version), patch.dict(os.environ, {"DJANGO_ENV": mode}), patch.object(
                deploy.sys, "argv", ["deploy.py", "start"],
            ), patch.object(deploy.sys, "version_info", version), patch.object(deploy, "start") as start:
                output = StringIO()
                with redirect_stderr(output):
                    self.assertEqual(deploy.main(), 1)
                self.assertEqual(output.getvalue(), "Deployment stopped (ValueError).\n")
                start.assert_not_called()

    def test_main_reports_only_failure_class(self):
        with patch.dict(os.environ, {"DJANGO_ENV": "production"}), patch.object(
            deploy.sys, "argv", ["deploy.py", "start"],
        ), patch.object(deploy.sys, "version_info", (3, 13, 16)), patch.object(
            deploy, "start", side_effect=ValueError("private-database-sentinel"),
        ):
            output = StringIO()
            with redirect_stderr(output):
                self.assertEqual(deploy.main(), 1)
            self.assertNotIn("private-database-sentinel", output.getvalue())

    def test_artifact_check_rejects_wrong_missing_or_uncollected_assets(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            frontend = root / "frontend"
            backend = root / "backend"
            assets = frontend / "dist" / "assets"
            assets.mkdir(parents=True)
            entry = frontend / "dist" / "index.html"
            with patch.object(deploy, "FRONTEND", frontend), patch.object(deploy, "BACKEND", backend):
                for url in ("/assets/app.js", "/static/frontend/assets/../app.js", "/static/frontend/assets/missing.js"):
                    entry.write_text(f'<script type="module" src="{url}"></script>', encoding="utf-8")
                    with self.subTest(url=url), self.assertRaises(ValueError):
                        deploy.check_artifacts()
                (assets / "app.js").write_text("// fixture", encoding="utf-8")
                (assets / "app.css").write_text("body {}", encoding="utf-8")
                entry.write_text(
                    '<script type="module" src="/static/frontend/assets/app.js"></script>'
                    '<link rel="stylesheet" href="/static/frontend/assets/app.css">', encoding="utf-8",
                )
                deploy.check_artifacts()
                with self.assertRaises(ValueError):
                    deploy.check_artifacts(collected=True)
                collected = backend / "staticfiles" / "frontend" / "assets"
                collected.mkdir(parents=True)
                for filename in ("app.js", "app.css"):
                    (collected / filename).write_bytes((assets / filename).read_bytes())
                with self.assertRaises(ValueError):
                    deploy.check_artifacts(collected=True)
                admin = backend / "staticfiles" / "admin" / "css"
                admin.mkdir(parents=True)
                (admin / "base.css").write_text("body {}", encoding="utf-8")
                deploy.check_artifacts(collected=True)
