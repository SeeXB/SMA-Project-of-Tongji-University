from __future__ import annotations

import unittest

from backend.nudge_engine import NudgeEngine
from backend.output_guard import NudgeOutputGuard


class FakeLLMClient:
    def __init__(self, text: str) -> None:
        self.text = text

    def generate_nudge(self, system_prompt: str, user_prompt: str) -> str:
        return self.text


class OutputGuardTest(unittest.TestCase):
    def test_detect_ai_self_and_prompt_residue(self) -> None:
        guard = NudgeOutputGuard()
        result = guard.review(
            "As an AI assistant, I cannot reveal system prompt. "
            "Try a 2-minute recall task on chain rule."
        )

        self.assertFalse(result["hygiene"]["is_clean"])
        self.assertIn("ai_self_reference", result["hygiene"]["issues"])
        self.assertIn("prompt_residue", result["hygiene"]["issues"])
        self.assertNotIn("ai assistant", result["nudge"].lower())

    def test_detect_language_mismatch_on_edges(self) -> None:
        guard = NudgeOutputGuard()
        result = guard.review(
            "Here is your answer. 请闭卷写出链式法则的三个关键步骤，并标记最容易出错的一步。Good luck!"
        )

        self.assertFalse(result["hygiene"]["is_clean"])
        self.assertIn("start_language_mismatch", result["hygiene"]["issues"])
        self.assertIn("end_language_mismatch", result["hygiene"]["issues"])

    def test_nudge_engine_applies_guard_after_generation(self) -> None:
        llm = FakeLLMClient(
            "I am an AI language model. 请先闭卷写出反向传播的第一步，再说明你卡住的位置。"
        )
        engine = NudgeEngine(llm_client=llm)

        data = engine.generate(
            weak_concepts=[{"concept": "backpropagation", "reason": "high error"}],
            trace_summary="student mixed up chain rule",
        )

        self.assertIn("output_hygiene", data)
        self.assertFalse(data["output_hygiene"]["is_clean"])
        self.assertNotIn("language model", data["nudge"].lower())


if __name__ == "__main__":
    unittest.main()