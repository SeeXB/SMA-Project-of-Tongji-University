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

	def generate_raw(
		self,
		concept: str | None,
		reason: str,
		trace_summary: str,
		nudge_type: str = "retrieval",
		rewrite_hint: str | None = None,
	) -> Dict[str, Any]:
		if not concept:
			return {
				"text": self.default_nudge(
					concept=None,
					nudge_type=nudge_type,
					language_hint=trace_summary,
				),
				"generation_info": {
					"source": "fallback_template",
					"fallback_reason": "no_target_concept",
					"llm_error": None,
					"nudge_type": nudge_type,
				},
			}

		system_prompt = self._load_prompt("nudge_system.txt")
		user_prompt = self._build_user_prompt(
			concept=concept,
			reason=reason,
			trace_summary=trace_summary,
			nudge_type=nudge_type,
			rewrite_hint=rewrite_hint,
		)
		result = self._call_llm(system_prompt=system_prompt, user_prompt=user_prompt)
		text = str(result.get("text", "")).strip()
		if text:
			return {
				"text": " ".join(text.split()),
				"generation_info": {
					"source": result.get("source", "llm"),
					"fallback_reason": result.get("fallback_reason"),
					"llm_error": result.get("llm_error"),
					"model": result.get("model"),
					"nudge_type": nudge_type,
				},
			}

		return {
			"text": self.default_nudge(
				concept=concept,
				nudge_type=nudge_type,
				language_hint=trace_summary,
			),
			"generation_info": {
				"source": "fallback_template",
				"fallback_reason": result.get("fallback_reason", "llm_unavailable"),
				"llm_error": result.get("llm_error"),
				"model": result.get("model"),
				"nudge_type": nudge_type,
			},
		}

	def default_nudge(
		self,
		concept: str | None = None,
		nudge_type: str = "retrieval",
		language_hint: str = "",
	) -> str:
		target = concept or "the target concept"
		if self._looks_cjk(language_hint):
			templates = {
				"retrieval": "请先闭卷，用 90 秒写出 {concept} 的核心步骤，再标出你最不确定的一步。",
				"comparison": "请用两句话比较 {concept} 中最容易混淆的两个点，再圈出你最拿不准的区别。",
				"reflection": "请先独立完成一个关于 {concept} 的小步骤，然后写一句你卡住的位置。",
				"correction": "请回到你在 {concept} 中做错的一步，重新写出修正后的第一步，并说明你为什么改它。",
			}
		else:
			templates = {
				"retrieval": "Close your notes and write the core steps of {concept} in under 90 seconds. Then mark the step you were least sure about.",
				"comparison": "Write two short bullets comparing the two most confusable parts of {concept}. Then mark which contrast still feels unstable.",
				"reflection": "Complete one tiny step on {concept} from memory, then write one sentence about where you hesitated.",
				"correction": "Return to one incorrect step in {concept}, rewrite the first corrected step, and say why you changed it.",
			}
		template = templates.get(nudge_type, templates["retrieval"])
		return template.format(concept=target)

	def generate(self, weak_concepts: List[Dict[str, Any]], trace_summary: str) -> Dict[str, Any]:
		if not weak_concepts:
			guarded = self.output_guard.review(self.default_nudge(language_hint=trace_summary))
			return {
				"nudge": guarded["nudge"],
				"concept": None,
				"reason": "no weak concept detected",
				"output_hygiene": guarded["hygiene"],
			}

		target = weak_concepts[0]
		concept = target.get("concept", "unknown")
		reason = target.get("reason", "weak performance")
		raw_result = self.generate_raw(
			concept=concept,
			reason=reason,
			trace_summary=trace_summary,
			nudge_type="retrieval",
		)
		nudge_text = raw_result["text"]
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

	@staticmethod
	def _build_user_prompt(
		concept: str,
		reason: str,
		trace_summary: str,
		nudge_type: str,
		rewrite_hint: str | None,
	) -> str:
		rewrite_block = ""
		if rewrite_hint:
			rewrite_block = f"Rewrite Constraints:\n{rewrite_hint}\n\n"
		return (
			f"Weak Concept:\n{concept}\n\n"
			f"Reason:\n{reason}\n\n"
			f"Nudge Type:\n{nudge_type}\n\n"
			f"Student Context:\n{trace_summary}\n\n"
			f"{rewrite_block}"
			"Generate one targeted nudge."
		)

	@staticmethod
	def _looks_cjk(text: str) -> bool:
		return any("\u4e00" <= ch <= "\u9fff" for ch in str(text or ""))

	def _call_llm(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
		if hasattr(self.llm_client, "generate_nudge_result"):
			return self.llm_client.generate_nudge_result(
				system_prompt=system_prompt,
				user_prompt=user_prompt,
			)

		text = self.llm_client.generate_nudge(
			system_prompt=system_prompt,
			user_prompt=user_prompt,
		)
		return {
			"text": text,
			"source": "llm",
			"fallback_reason": None,
			"llm_error": None,
			"model": None,
		}
