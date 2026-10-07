"""Step 17: actual Vite bundle with DEBUG=False, not fixture-only proof."""

from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings

from scripts.deploy import EntryAssets


class ProductionBuildTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.directory = TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.override = override_settings(
            DEBUG=False, STATIC_ROOT=Path(cls.directory.name) / "collected",
            WHITENOISE_AUTOREFRESH=False, WHITENOISE_USE_FINDERS=False,
        )
        cls.override.enable()
        cls.addClassCleanup(cls.override.disable)
        cls.entry = (settings.FRONTEND_DIST / "index.html").read_text(encoding="utf-8")
        cls.parser = EntryAssets()
        cls.parser.feed(cls.entry)
        call_command("collectstatic", interactive=False, verbosity=0, stdout=StringIO())

    def test_real_entry_and_direct_detail_use_built_asset_prefix_without_vite(self):
        self.assertIn('<div id="root">', self.entry)
        self.assertTrue(self.parser.urls)
        self.assertNotIn("/src/main.jsx", self.entry)
        self.assertNotIn("/@vite/client", self.entry)
        self.assertTrue(any(url.endswith(".js") for url in self.parser.urls))
        self.assertTrue(any(url.endswith(".css") for url in self.parser.urls))
        for url in self.parser.urls:
            self.assertTrue(url.startswith("/static/frontend/assets/"))
        for path in ("/", "/events/1"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content.decode(), self.entry)
            self.assertIn("no-store", response["Cache-Control"])

    def test_actual_collected_frontend_and_admin_assets_are_served_with_correct_types(self):
        urls = self.parser.urls + ["/static/admin/css/base.css", "/static/admin/js/core.js"]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                expected = "text/css" if url.endswith(".css") else "javascript"
                self.assertIn(expected, response["Content-Type"])
                actual = b"".join(response.streaming_content)
                expected_file = Path(settings.STATIC_ROOT) / url.removeprefix("/static/")
                self.assertEqual(actual, expected_file.read_bytes())
                response.close()
