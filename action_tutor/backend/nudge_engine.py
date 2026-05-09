from __future__ import annotations

import os
from typing import Any, Dict, List


class NudgeEngine:
	def __init__(self, llm_client: Any, prompts_dir: str | None = None) -> None:
		self.llm_client = llm_client
		self.prompts_dir = prompts_dir or os.path.join(
			os.path.dirname(os.path.dirname(__file__)), "prompts"
		)

	def generate(self, weak_concepts: List[Dict[str, Any]], trace_summary: str) -> Dict[str, Any]:
		if not weak_concepts:
			return {
				"nudge": "Pick one concept you studied today and retrieve its core formula from memory in under 90 seconds.",
				"concept": None,
				"reason": "no weak concept detected",
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

		return {
			"nudge": " ".join(str(nudge_text).split()),
			"concept": concept,
			"reason": reason,
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
