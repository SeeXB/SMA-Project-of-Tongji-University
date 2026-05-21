from __future__ import annotations

import os
from typing import Any, Dict, List

from backend.output_guard import NudgeOutputGuard


class NudgeEngine:
	def __init__(
		self,
		llm_client: Any,
		prompts_dir: str | None = None,
		output_guard: NudgeOutputGuard | None = None,
	) -> None:
		self.llm_client = llm_client
		self.prompts_dir = prompts_dir or os.path.join(
			os.path.dirname(os.path.dirname(__file__)), "prompts"
		)
		self.output_guard = output_guard or NudgeOutputGuard()

	def generate(self, weak_concepts: List[Dict[str, Any]], trace_summary: str) -> Dict[str, Any]:
		if not weak_concepts:
			guarded = self.output_guard.review(
				"Pick one concept you studied today and retrieve its core formula from memory in under 90 seconds."
			)
			return {
				"nudge": guarded["nudge"],
				"concept": None,
				"reason": "no weak concept detected",
				"output_hygiene": guarded["hygiene"],
			}

		target = weak_concepts[0]
		concept = target.get("concept", "unknown")
		reason = target.get("reason", "weak performance")

		system_prompt = self._load_prompt("nudge_system.txt")
		user_prompt = (
			f"Weak Concept:\n{concept}\n\n"
			f"Reason:\n{reason}\n\n"
			f"Student Context:\n{trace_summary}\n\n"
			"Generate one targeted nudge."
		)
		nudge_text = self.llm_client.generate_nudge(system_prompt=system_prompt, user_prompt=user_prompt)
		guarded = self.output_guard.review(" ".join(str(nudge_text).split()))

		return {
			"nudge": guarded["nudge"],
			"concept": concept,
			"reason": reason,
			"output_hygiene": guarded["hygiene"],
		}

	def _load_prompt(self, filename: str) -> str:
		path = os.path.join(self.prompts_dir, filename)
		try:
			with open(path, "r", encoding="utf-8") as f:
				return f.read().strip()
		except FileNotFoundError:
			return (
				"You are an action-oriented AI tutor. Never explain directly. "
				"Generate one concise retrieval or reflection task."
			)
