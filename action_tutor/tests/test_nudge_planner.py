from __future__ import annotations

import unittest

from backend.nudge_planner import NudgePlanner


class NudgePlannerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.planner = NudgePlanner()

    def test_returns_default_plan_when_no_weak_concepts(self) -> None:
        plan = self.planner.plan([])

        self.assertIsNone(plan["concept"])
        self.assertEqual(plan["nudge_type"], "retrieval")

    def test_picks_correction_for_high_error_rate(self) -> None:
        plan = self.planner.plan(
            [
                {
                    "concept": "backpropagation",
                    "reason": "high error",
                    "score": 0.8,
                    "signals": {"error_rate": 0.8},
                }
            ]
        )

        self.assertEqual(plan["nudge_type"], "correction")

    def test_picks_comparison_for_avoidance_pattern(self) -> None:
        plan = self.planner.plan(
            [
                {
                    "concept": "chain rule",
                    "reason": "avoidance pattern",
                    "score": 0.6,
                    "signals": {
                        "error_rate": 0.2,
                        "forgetting_score": 0.2,
                        "avoidance_score": 0.6,
                        "hesitation_score": 0.1,
                    },
                }
            ]
        )

        self.assertEqual(plan["nudge_type"], "comparison")

    def test_picks_reflection_for_high_hesitation(self) -> None:
        plan = self.planner.plan(
            [
                {
                    "concept": "bayes theorem",
                    "reason": "hesitation",
                    "score": 0.4,
                    "signals": {
                        "error_rate": 0.1,
                        "forgetting_score": 0.2,
                        "avoidance_score": 0.2,
                        "hesitation_score": 0.45,
                    },
                }
            ]
        )

        self.assertEqual(plan["nudge_type"], "reflection")


if __name__ == "__main__":
    unittest.main()
