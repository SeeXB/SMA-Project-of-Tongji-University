from __future__ import annotations

import unittest

from app import create_app


class PipelineSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_generate_nudge_pipeline(self) -> None:
        payload = {
            "student_id": "stu001",
            "notes": "I understand gradient descent but keep confusing chain rule during backpropagation.",
            "exercise_logs": [
                {"concept": "backpropagation", "correct": False},
                {"concept": "gradient descent", "correct": True},
            ],
            "error_history": ["forgot chain rule", "wrong derivative sign"],
        }

        response = self.client.post("/generate_nudge", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertIn("weak_concepts", data)
        self.assertIn("nudge", data)
        self.assertTrue(isinstance(data["weak_concepts"], list))
        self.assertTrue(isinstance(data["nudge"], str))

    def test_upload_trace(self) -> None:
        response = self.client.post(
            "/upload_trace",
            json={
                "notes": "quick review of bayes theorem",
                "exercise_logs": [{"concept": "bayes theorem", "correct": False}],
                "error_history": ["mixed prior and likelihood"],
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("concepts", data)


if __name__ == "__main__":
    unittest.main()

