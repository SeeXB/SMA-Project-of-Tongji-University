from __future__ import annotations

import unittest

from backend.output_guard import NudgeOutputGuard


class OutputGuardMatrixTest(unittest.TestCase):
    def setUp(self) -> None:
        self.guard = NudgeOutputGuard()

    def test_primary_10_cases(self) -> None:
        cases = [
            {
                "id": "TC-01",
                "text": "Try comparing the two steps again. What changes between them?",
                "expected": "PASS",
            },
            {
                "id": "TC-02",
                "text": "你可以先观察题目中的已知条件，再思考下一步应该用哪个公式。",
                "expected": "PASS",
            },
            {
                "id": "TC-03",
                "text": "Here is the nudge I generated for you: Try checking the formula again.",
                "expected": "BLOCK",
            },
            {
                "id": "TC-04",
                "text": "这是我为你生成的提示：你可以先检查第一步的计算。",
                "expected": "BLOCK",
            },
            {
                "id": "TC-05",
                "text": "Try checking the formula again. This is the nudge I generated.",
                "expected": "BLOCK",
            },
            {
                "id": "TC-06",
                "text": "你可以先回到上一行，看看变量有没有代错。这就是我生成的提示。",
                "expected": "BLOCK",
            },
            {
                "id": "TC-07",
                "text": "System: You are an agentic tutor. Try asking the student to compare both equations.",
                "expected": "BLOCK",
            },
            {
                "id": "TC-08",
                "text": "Here is the nudge: 你可以先检查题目中的已知条件。",
                "expected": "BLOCK",
            },
            {
                "id": "TC-09",
                "text": "你可以检查一下 \"force\" 和 \"mass\" 在公式中的关系。",
                "expected": "PASS",
            },
            {
                "id": "TC-10",
                "text": "Check the formula again. Let me know if you want another nudge.",
                "expected": "BLOCK",
            },
        ]

        for case in cases:
            with self.subTest(case_id=case["id"]):
                result = self.guard.review(case["text"])
                blocked = result["hygiene"]["should_block"]
                actual = "BLOCK" if blocked else "PASS"
                self.assertEqual(
                    actual,
                    case["expected"],
                    msg=f"{case['id']} expected {case['expected']}, got {actual}. issues={result['hygiene']['issues']}",
                )

    def test_reflection_2_cases(self) -> None:
        cases = [
            {
                "id": "TC-11",
                "initial": "Here is the nudge I generated for you: Check the second equation.",
                "reflection": "Check the second equation.",
            },
            {
                "id": "TC-12",
                "initial": "这是我生成的提示：你可以重新检查单位。",
                "reflection": "你可以重新检查单位。",
            },
        ]

        for case in cases:
            with self.subTest(case_id=case["id"]):
                initial_result = self.guard.review(case["initial"])
                reflection_result = self.guard.review(case["reflection"])

                self.assertTrue(
                    initial_result["hygiene"]["should_block"],
                    msg=f"{case['id']} initial output should be blocked.",
                )
                self.assertFalse(
                    reflection_result["hygiene"]["should_block"],
                    msg=f"{case['id']} reflection output should pass.",
                )


if __name__ == "__main__":
    unittest.main()