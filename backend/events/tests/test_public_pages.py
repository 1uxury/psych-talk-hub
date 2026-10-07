"""Step 17: page/static boundaries and Admin-to-public publication."""

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from events.models import Event, EventResource, Resource


class PublicPageTests(SimpleTestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / "templates").mkdir()
        (root / "templates" / "index.html").write_text(
            '<html lang="en"><title>PsychTalk Hub</title><div id="root"></div></html>',
            encoding="utf-8",
        )
        assets = root / "static" / "frontend" / "assets"
        assets.mkdir(parents=True)
        (assets / "fixture.js").write_text("console.log('fixture');", encoding="utf-8")
        (assets / "fixture.css").write_text("body { color: green; }", encoding="utf-8")
        templates = [{**settings.TEMPLATES[0], "DIRS": [root / "templates"]}]
        override = override_settings(
            DEBUG=False, TEMPLATES=templates, STATIC_ROOT=root / "static",
            WHITENOISE_AUTOREFRESH=False, WHITENOISE_USE_FINDERS=False,
        )
        override.enable()
        self.addCleanup(override.disable)

    def test_declared_pages_serve_the_same_uncached_entry_without_database_queries(self):
        for path in ("/", "/events/1", "/events/999999"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertContains(response, '<div id="root">')
                self.assertIn("no-store", response["Cache-Control"])
                self.assertTrue(response["Content-Type"].startswith("text/html"))

    def test_page_head_and_unsafe_methods(self):
        for path in ("/", "/events/1"):
            self.assertEqual(self.client.head(path).content, b"")
            self.assertEqual(self.client.head(path).status_code, 200)
            for method in ("post", "put", "patch", "delete"):
                with self.subTest(path=path, method=method):
                    response = getattr(self.client, method)(path)
                    self.assertEqual(response.status_code, 405)
                    self.assertEqual(response["Allow"], "GET, HEAD")

    def test_unknown_api_remains_json_even_when_accepting_html(self):
        for path in ("/api", "/api/", "/api/unknown/", "/api/events/not-an-id/"):
            with self.subTest(path=path):
                response = self.client.get(path, HTTP_ACCEPT="text/html")
                self.assertEqual(response.status_code, 404)
                self.assertTrue(response["Content-Type"].startswith("application/json"))
                self.assertIsInstance(response.json()["detail"], str)
                self.assertNotIn(b'id="root"', response.content)

    def test_unknown_pages_and_admin_paths_are_not_spa_fallbacks(self):
        for path in ("/unknown/", "/events/no", "/events/1/extra", "/events/1/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 404)
                self.assertNotIn(b'id="root"', response.content)
        response = self.client.get("/admin/unknown/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith("/admin/login/?next="))
        response = self.client.get("/admin/login/")
        self.assertContains(response, 'name="username"')
        self.assertNotIn(b'id="root"', response.content)

    def test_missing_build_returns_safe_503_instead_of_debug_details(self):
        templates = [{**settings.TEMPLATES[0], "DIRS": []}]
        with override_settings(TEMPLATES=templates):
            response = self.client.get("/")
        self.assertEqual(response.status_code, 503)
        self.assertContains(response, "We couldn't load this page. Please try again.", status_code=503)
        self.assertIn("no-store", response["Cache-Control"])
        self.assertNotIn(b"TemplateDoesNotExist", response.content)

    def test_whitenoise_serves_collected_js_css_and_missing_asset_is_not_html_entry(self):
        for filename, mime in (("fixture.js", "javascript"), ("fixture.css", "text/css")):
            with self.subTest(filename=filename):
                response = self.client.get(f"/static/frontend/assets/{filename}")
                self.assertEqual(response.status_code, 200)
                self.assertIn(mime, response["Content-Type"])
                self.assertTrue(b"".join(response.streaming_content))
                response.close()
        missing = self.client.get("/static/frontend/assets/missing.js")
        self.assertEqual(missing.status_code, 404)
        self.assertNotIn(b'id="root"', missing.content)


class MilestonePublicationTests(TestCase):
    def test_admin_add_and_link_is_visible_to_anonymous_api_on_next_read(self):
        event = Event.objects.create(
            title="Publication test talk", starts_at=datetime(2026, 12, 1, tzinfo=timezone.utc),
        )
        user = get_user_model().objects.create_superuser(
            username="milestone-test", email="test@example.org", password="test-only-password",
        )
        visitor = Client()
        detail_url = f"/api/events/{event.pk}/"
        self.assertEqual(visitor.get(detail_url).json()["resource_count"], 0)
        self.client.force_login(user)
        response = self.client.post(reverse("admin:events_resource_add"), {
            "title": "Publication test reading", "authors": "", "year": "",
            "original_url": "https://example.org/reading", "resource_type": "article",
            "_save": "Save",
        })
        self.assertEqual(response.status_code, 302)
        resource = Resource.objects.get(title="Publication test reading")
        response = self.client.post(reverse("admin:events_eventresource_add"), {
            "event": event.pk, "resource": resource.pk,
            "recommendation": "Read after the talk.", "display_order": -1, "_save": "Save",
        })
        self.assertEqual(response.status_code, 302)
        body = visitor.get(detail_url).json()
        self.assertEqual(body["resource_count"], 1)
        self.assertEqual(body["resources"][0]["resource_id"], resource.pk)
        self.assertEqual(body["resources"][0]["recommendation"], "Read after the talk.")
        self.assertEqual(body["resources"][0]["display_order"], -1)
        self.assertEqual(EventResource.objects.count(), 1)
