import os
import unittest

from fastapi.testclient import TestClient

import main


class LeadQualificationContractTest(unittest.TestCase):
    def setUp(self):
        main.GOOGLE_API_KEY = ""
        self.client = TestClient(main.app)

    def test_form_contains_soft_qualification_fields_and_budget_anchor(self):
        index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")

        with open(index_path, encoding="utf-8") as handle:
            html = handle.read()

        self.assertIn('id="datum"', html)
        self.assertIn('id="momente"', html)
        self.assertIn('id="investitionsrahmen"', html)
        self.assertIn("Ich brauche erst ein Gefühl für die Pakete", html)
        self.assertIn("ab 799 €", html)
        self.assertIn("1.000-1.500 €", html)
        self.assertIn("1.500 €+", html)
        self.assertNotIn("unter 799", html.lower())
        self.assertNotIn("unter 500", html.lower())

    def test_api_accepts_extended_qualification_payload(self):
        response = self.client.post(
            "/api/qualify",
            json={
                "name": "Sophie & Leon",
                "instagram": "@sophieundleon",
                "website": "https://example.com",
                "fokus": "Hochzeit",
                "datum": "September 2026",
                "momente": "Die Reaktion beim First Look und die kleinen Momente mit der Familie.",
                "investitionsrahmen": "ab 799 €",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

    def test_frontend_checks_form_validity_before_submission(self):
        app_path = os.path.join(os.path.dirname(__file__), "static", "app.js")

        with open(app_path, encoding="utf-8") as handle:
            script = handle.read()

        self.assertIn("leadForm.checkValidity()", script)
        self.assertIn("leadForm.reportValidity()", script)


if __name__ == "__main__":
    unittest.main()
