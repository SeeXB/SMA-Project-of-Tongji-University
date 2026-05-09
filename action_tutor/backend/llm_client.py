from __future__ import annotations

import os
import re
from typing import Optional

from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam


class LLMClient:
	def __init__(self, model: str | None = None, base_url: str | None = None, temperature: float = 0.3) -> None:
		self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
		self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
		self.temperature = temperature
		self._client = None

		api_key = os.getenv("OPENAI_API_KEY")
		if api_key:
			try:
				from openai import OpenAI

				client_kwargs = {"api_key": api_key}
				if self.base_url:
					client_kwargs["base_url"] = self.base_url
				self._client = OpenAI(**client_kwargs)
			except Exception:
				self._client = None

	def generate_nudge(self, system_prompt: str, user_prompt: str) -> str:
		if self._client is not None:
			try:
				messages: list[ChatCompletionSystemMessageParam | ChatCompletionUserMessageParam] = [
					{"role": "system", "content": system_prompt},
					{"role": "user", "content": user_prompt},
				]
				response = self._client.chat.completions.create(
					model=self.model,
					temperature=self.temperature,
					messages=messages,
                    extra_body={"reasoning_split": True},
				)
				text = response.choices[0].message.content or ""
				cleaned = " ".join(text.split())
				if cleaned:
					return cleaned
			except Exception:
				pass

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

