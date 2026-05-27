from __future__ import annotations

import unittest

from app import create_app


class FakeTraceIndexer:
    def process(self, trace):
        concept = "backpropagation"
        if trace.get("exercise_logs"):
            concept = trace["exercise_logs"][0].get("concept", concept)
        return {
            "student_id": trace.get("student_id", "stu001"),
            "concepts": [
                {
                    "name": concept,
                    "mastery": 0.25,
                    "last_seen": "2026-05-20",
                    "mistake_count": 2,
                    "attempts": 3,
                    "error_rate": 0.6667,
                    "revisit_gap_days": 4,
                }
            ],
            "trace_summary": f"Notes: {trace.get('notes', '')}",
        }


class FakeGapDetector:
    def detect(self, indexed_trace):
        concept = indexed_trace["concepts"][0]["name"]
        return {
            "weak_concepts": [
                {
                    "concept": concept,
                    "score": 0.71,
                    "reason": "high error + low mastery",
                    "signals": {
                        "error_rate": 0.6667,
                        "forgetting_score": 0.3,
                        "avoidance_score": 0.35,
                        "hesitation_score": 0.2,
                    },
                }
            ],
            "weights": {
                "error_rate": 0.4,
                "forgetting": 0.3,
                "avoidance": 0.2,
                "hesitation": 0.1,
            },
        }


class FakeLLMClient:
    def generate_nudge(self, system_prompt: str, user_prompt: str) -> str:
        return "Check the first derivative step again, then mark where the sign flips."


class PipelineSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        app = create_app(
            trace_indexer=FakeTraceIndexer(),
            gap_detector=FakeGapDetector(),
            llm_client=FakeLLMClient(),
        )
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
        self.assertIn("task_id", data)
        self.assertIn("selected_plan", data)
        self.assertIn("agent_trace", data)
        self.assertIn("latency_ms", data)
        self.assertIn("reflection", data)
        self.assertTrue(isinstance(data["weak_concepts"], list))
        self.assertTrue(isinstance(data["nudge"], str))
        self.assertTrue(isinstance(data["agent_trace"], list))

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
