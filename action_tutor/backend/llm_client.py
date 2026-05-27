from __future__ import annotations

import os
import re
from typing import Any, Dict, Optional

from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam


class LLMClient:
	def __init__(self, model: str | None = None, base_url: str | None = None, temperature: float = 0.3) -> None:
		self.model = model or os.getenv("DEEPSEEK_MODEL") or os.getenv("OPENAI_MODEL", "deepseek-v4-flash")
		self.base_url = (
			base_url
			or os.getenv("DEEPSEEK_BASE_URL")
			or os.getenv("OPENAI_BASE_URL")
			or "https://api.deepseek.com"
		)
		self.temperature = temperature
		self._client = None
		self._client_error: str | None = None

		api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
		if not api_key:
			self._client_error = "DEEPSEEK_API_KEY is not set"
			return

		try:
			from openai import OpenAI

			client_kwargs = {"api_key": api_key}
			if self.base_url:
				client_kwargs["base_url"] = self.base_url
			self._client = OpenAI(**client_kwargs)
		except Exception as exc:
			self._client = None
			self._client_error = f"{type(exc).__name__}: {exc}"

	def generate_nudge_result(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
		if self._client is None:
			return {
				"text": "",
				"source": "fallback_template",
				"fallback_reason": "client_unavailable",
				"llm_error": self._client_error,
				"model": self.model,
			}

		try:
			messages: list[ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam] = [
				{"role": "system", "content": system_prompt},
				{"role": "user", "content": user_prompt},
			]
			response = self._client.chat.completions.create(
				model=self.model,
				temperature=self.temperature,
				messages=messages,
				stream=False,
				extra_body={"thinking": {"type": "disabled"}},
			)
			text = response.choices[0].message.content or ""
			cleaned = " ".join(text.split())
			if cleaned:
				return {
					"text": cleaned,
					"source": "llm",
					"fallback_reason": None,
					"llm_error": None,
					"model": self.model,
				}
			return {
				"text": "",
				"source": "fallback_template",
				"fallback_reason": "empty_llm_response",
				"llm_error": "The model returned an empty response",
				"model": self.model,
			}
		except Exception as exc:
			return {
				"text": "",
				"source": "fallback_template",
				"fallback_reason": "llm_request_failed",
				"llm_error": f"{type(exc).__name__}: {exc}",
				"model": self.model,
			}

	def generate_nudge(self, system_prompt: str, user_prompt: str) -> str:
		result = self.generate_nudge_result(system_prompt=system_prompt, user_prompt=user_prompt)
		if result.get("text"):
			return str(result["text"])

		concept = self._extract_field(user_prompt, "Weak Concept") or "the target concept"
		return (
			f"Close your notes and solve one 2-minute micro-task on {concept}: "
			f"write the first step only, then state where you hesitated."
		)

	@staticmethod
	def _extract_field(prompt: str, label: str) -> Optional[str]:
		pattern = rf"{re.escape(label)}:\s*(.+)"
		match = re.search(pattern, prompt)
		if not match:
			return None
		return match.group(1).strip()

