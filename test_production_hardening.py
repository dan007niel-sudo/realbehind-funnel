import os
import stat
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import main
from schemas import TrackingEvent
from services.storage import LeadRepository


class ProductionHardeningTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "leads.db")
        self.repository = LeadRepository(self.db_path)
        main.lead_repository = self.repository
        main.GOOGLE_API_KEY = ""
        main.SMTP_USER = ""
        main.SMTP_PASSWORD = ""
        main.NOTIFICATION_EMAIL = ""
        self.client = TestClient(main.app)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_qualify_stores_lead_before_background_processing(self):
        response = self.client.post(
            "/api/qualify",
            json={
                "name": "Sophie & Leon",
                "instagram": "@sophieundleon",
                "website": "https://example.com",
                "fokus": "Hochzeit",
                "datum": "September 2026",
                "momente": "First Look und kleine Familienmomente.",
                "investitionsrahmen": "ab 799 €",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "success")
        self.assertIsInstance(payload["lead_id"], int)

        stored = self.repository.get_lead(payload["lead_id"])
        self.assertEqual(stored["name"], "Sophie & Leon")
        self.assertEqual(stored["instagram"], "@sophieundleon")
        self.assertIn(stored["status"], {"received", "briefing_skipped", "email_skipped"})

    def test_tracking_event_endpoint_persists_frontend_events(self):
        response = self.client.post(
            "/api/events",
            json={
                "event": "cta_clicked",
                "session_id": "session-123",
                "metadata": {"step": 1, "label": "Jetzt Kennenlernen anfragen"},
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "success")
        self.assertIsInstance(payload["event_id"], int)

        events = self.repository.list_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event"], "cta_clicked")
        self.assertEqual(events[0]["session_id"], "session-123")
        self.assertEqual(events[0]["metadata"]["step"], 1)

    def test_tracking_event_schema_rejects_empty_event_names(self):
        with self.assertRaises(ValueError):
            TrackingEvent(event="", session_id="session-123")

    def test_deploy_script_exists_and_runs_reproducible_steps(self):
        script = Path(__file__).resolve().parent / "deploy.sh"

        self.assertTrue(script.exists())
        mode = script.stat().st_mode
        self.assertTrue(mode & stat.S_IXUSR)

        contents = script.read_text(encoding="utf-8")
        self.assertIn("git fetch origin main", contents)
        self.assertIn("docker compose up -d --build realbehind", contents)
        self.assertIn('wait_for_url "http://127.0.0.1:8010/health" "Internal"', contents)
        self.assertIn('wait_for_url "https://realbehind.com/health" "Public"', contents)
        self.assertIn("https://realbehind.com/health", contents)

    def test_frontend_records_key_funnel_events(self):
        script = (Path(__file__).resolve().parent / "static" / "app.js").read_text(
            encoding="utf-8"
        )

        self.assertIn("trackEvent('cta_clicked'", script)
        self.assertIn("trackEvent('form_started'", script)
        self.assertIn("trackEvent('form_submitted'", script)
        self.assertIn("trackEvent('calendly_loaded'", script)
        self.assertIn("calendly.event_scheduled", script)
        self.assertIn("fetch('/api/events'", script)


if __name__ == "__main__":
    unittest.main()
