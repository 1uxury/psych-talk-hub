"""Promotion images: safe addresses, permissions, API and durable demo artwork."""

from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from events.demo_seed import load_demo_manifest, seed_demo_data
from events.models import Event, EventResource, Resource


class EventCoverTests(TestCase):
    def event(self, **fields):
        return Event.objects.create(title="Image talk", starts_at=datetime(2026, 11, 1, tzinfo=timezone.utc), **fields)

    def test_accepted_image_addresses_and_blank_defaults(self):
        for url in ("", "https://images.example.org/photo.jpg", "/static/events/posters/sleep.svg"):
            self.assertEqual(self.event(cover_image_url=url).cover_image_url, url)

    def test_invalid_image_addresses_never_save(self):
        for url in ("javascript:alert(1)", "data:image/png,abc", "http://example.org/x", "//example.org/x",
                    "https://user:pass@example.org/x", "https://example.org/with space", "https://example.org\\@evil.org/x",
                    "/static/events/posters/../secret.svg", "/static/events/posters/%2e%2e.svg", "/static/other.svg"):
            with self.subTest(url=url), self.assertRaises(ValidationError):
                self.event(cover_image_url=url)
        self.assertEqual(Event.objects.count(), 0)

    def test_alt_length_validation(self):
        with self.assertRaises(ValidationError):
            self.event(cover_image_alt="x" * 256)

    def test_image_fields_match_in_both_public_endpoints_without_server_fetch(self):
        event = self.event(cover_image_url="https://example.org/poster.png", cover_image_alt="A psychology poster")
        with patch("requests.sessions.Session.request", side_effect=AssertionError("No image download")):
            listed = self.client.get("/api/events/").json()[0]
            detail = self.client.get(f"/api/events/{event.pk}/").json()
        for field in ("cover_image_url", "cover_image_alt"):
            self.assertEqual(listed[field], getattr(event, field))
            self.assertEqual(detail[field], listed[field])

    def test_admin_edits_publish_image_and_reject_unsafe_url(self):
        user = get_user_model().objects.create_superuser(username="cover-admin", password="test-password")
        self.client.force_login(user)
        event = self.event()
        url = reverse("admin:events_event_change", args=[event.pk])
        data = {"title": event.title, "starts_at_0": "2026-11-01", "starts_at_1": "00:00:00",
                "cover_image_url": "https://example.org/image.png", "cover_image_alt": "Original artwork", "_save": "Save"}
        self.assertEqual(self.client.post(url, data).status_code, 302)
        event.refresh_from_db()
        self.assertEqual(event.cover_image_url, data["cover_image_url"])
        self.assertEqual(event.cover_image_alt, data["cover_image_alt"])
        rejected = self.client.post(url, {**data, "cover_image_url": "javascript:alert(1)"})
        self.assertContains(rejected, "Use an HTTPS image URL")
        event.refresh_from_db()
        self.assertEqual(event.cover_image_url, data["cover_image_url"])

    def test_staff_without_event_change_permission_cannot_edit_image(self):
        event = self.event()
        user = get_user_model().objects.create_user(username="cover-staff", is_staff=True)
        self.client.force_login(user)
        self.assertEqual(self.client.post(reverse("admin:events_event_change", args=[event.pk]),
                                         {"cover_image_url": "https://example.org/x"}).status_code, 403)
        event.refresh_from_db()
        self.assertEqual(event.cover_image_url, "")

    def test_demo_expansion_and_explicit_backfill_preserve_old_fields(self):
        manifest = load_demo_manifest()
        old = manifest["events"][0]
        fields = {k: v for k, v in old["fields"].items() if not k.startswith("cover_")}
        event = Event.objects.create(seed_key=old["seed_key"], starts_at=datetime(2026, 10, 2, tzinfo=timezone.utc), **fields)
        before = Event.objects.values().get(pk=event.pk)
        counts = seed_demo_data(fill_missing_covers=True)
        self.assertEqual(counts, {"events": 7, "resources": 11, "associations": 24, "covers": 1})
        event.refresh_from_db()
        after = Event.objects.values().get(pk=event.pk)
        self.assertEqual({k: v for k, v in after.items() if not k.startswith("cover_")},
                         {k: v for k, v in before.items() if not k.startswith("cover_")})
        self.assertEqual(event.cover_image_url, old["fields"]["cover_image_url"])
        self.assertEqual((Event.objects.count(), Resource.objects.count(), EventResource.objects.count()), (8, 11, 24))
        snapshot = list(Event.objects.order_by("id").values())
        output = StringIO()
        call_command("seed_demo", "--fill-missing-covers", stdout=output)
        self.assertIn("Filled 0 existing empty demo covers", output.getvalue())
        self.assertEqual(list(Event.objects.order_by("id").values()), snapshot)

    def test_backfill_skips_custom_image_alt_title_and_real_events(self):
        seed_demo_data()
        events = list(Event.objects.order_by("id"))
        variants = [{"cover_image_url": "https://example.org/custom.png"}, {"cover_image_url": "", "cover_image_alt": "Keep this"},
                    {"cover_image_url": "", "title": "Edited title"}, {"cover_image_url": "", "is_example": False}]
        for event, fields in zip(events, variants):
            for key, value in fields.items():
                setattr(event, key, value)
            event.save()
        before = list(Event.objects.order_by("id").values())
        self.assertEqual(seed_demo_data(fill_missing_covers=True)["covers"], 0)
        self.assertEqual(list(Event.objects.order_by("id").values()), before)

    def test_default_seed_preserves_deliberately_cleared_cover(self):
        seed_demo_data()
        event = Event.objects.first()
        event.cover_image_url = event.cover_image_alt = ""
        event.save()
        seed_demo_data()
        event.refresh_from_db()
        self.assertEqual(event.cover_image_url, "")

    def test_every_demo_poster_is_local_self_contained_vector_art(self):
        root = Path(__file__).resolve().parents[1] / "static"
        for entry in load_demo_manifest()["events"]:
            url = entry["fields"]["cover_image_url"]
            text = (root / url.removeprefix("/static/")).read_text(encoding="utf-8")
            self.assertIn('viewBox="0 0 1200 675"', text)
            self.assertNotIn("<script", text)
            self.assertNotIn("href=", text)
