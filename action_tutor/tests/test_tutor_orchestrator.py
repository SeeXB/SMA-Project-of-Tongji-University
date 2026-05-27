from __future__ import annotations

import unittest

from backend.nudge_engine import NudgeEngine
from backend.nudge_planner import NudgePlanner
from backend.output_guard import NudgeOutputGuard
from backend.tutor_orchestrator import TutorOrchestrator


class FakeTraceIndexer:
    def process(self, trace):
        return {
            "student_id": trace.get("student_id", "stu001"),
            "concepts": [
                {
                    "name": "backpropagation",
                    "mastery": 0.2,
                    "last_seen": "2026-05-20",
                    "mistake_count": 3,
                    "attempts": 4,
                    "error_rate": 0.75,
                    "revisit_gap_days": 6,
                }
            ],
            "trace_summary": "Student keeps mixing up chain rule during backpropagation.",
        }


class FakeGapDetector:
    def detect(self, indexed_trace):
        return {
            "weak_concepts": [
                {
                    "concept": "backpropagation",
                    "score": 0.77,
                    "reason": "high error + low mastery",
                    "signals": {
                        "error_rate": 0.75,
                        "forgetting_score": 0.38,
                        "avoidance_score": 0.42,
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
    def __init__(self, responses):
        self.responses = list(responses)

    def generate_nudge(self, system_prompt: str, user_prompt: str) -> str:
        if not self.responses:
            return "Check the first step again and mark where you hesitated."
        if len(self.responses) == 1:
            return self.responses[0]
        return self.responses.pop(0)


class TutorOrchestratorTest(unittest.TestCase):
    def _build_orchestrator(self, responses) -> TutorOrchestrator:
        llm_client = FakeLLMClient(responses)
        return TutorOrchestrator(
            trace_indexer=FakeTraceIndexer(),
            gap_detector=FakeGapDetector(),
            nudge_planner=NudgePlanner(),
            nudge_engine=NudgeEngine(llm_client=llm_client),
            output_guard=NudgeOutputGuard(),
        )

    def test_returns_selected_plan_and_agent_trace(self) -> None:
        orchestrator = self._build_orchestrator(
            ["Check the derivative flow once more, then mark the step where the sign changes."]
        )

        result = orchestrator.run({"student_id": "stu001"})

        self.assertEqual(result["selected_plan"]["concept"], "backpropagation")
        self.assertEqual(result["selected_plan"]["nudge_type"], "correction")
        self.assertTrue(any(row["agent"] == "nudge_planner_agent" for row in result["agent_trace"]))
        self.assertFalse(result["output_hygiene"]["should_block"])

    def test_uses_fallback_after_blocked_rewrite(self) -> None:
        blocked = "Here is the nudge I generated for you: Check the chain rule again."
        orchestrator = self._build_orchestrator([blocked])

        result = orchestrator.run({"student_id": "stu001"})

        self.assertEqual(result["reflection"]["strategy"], "fallback_after_block")
        self.assertTrue(result["reflection"]["attempted"])
        self.assertFalse(result["output_hygiene"]["should_block"])
        self.assertNotIn("generated for you", result["nudge"].lower())
        generator_steps = [row for row in result["agent_trace"] if row["agent"] == "nudge_generator_agent"]
        self.assertEqual(len(generator_steps), 2)


if __name__ == "__main__":
    unittest.main()
