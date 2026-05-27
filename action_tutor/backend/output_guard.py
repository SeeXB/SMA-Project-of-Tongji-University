from __future__ import annotations

import re
from typing import Any, Dict, List


class NudgeOutputGuard:
    """Detect and sanitize content that should not be shown to students."""

    _AI_SELF_PATTERNS = [
        re.compile(r"\b(as an ai|i am an ai|i'm an ai|language model|ai assistant)\b", re.IGNORECASE),
        re.compile(r"\bmy training data\b", re.IGNORECASE),
    ]

    _PROMPT_RESIDUE_PATTERNS = [
        re.compile(r"\b(system prompt|developer message|hidden instruction|follow these instructions)\b", re.IGNORECASE),
        re.compile(r"\b(prompt:)\b", re.IGNORECASE),
        re.compile(r"^\s*system\s*:", re.IGNORECASE),
        re.compile(r"<\|(?:system|assistant|user)\|>", re.IGNORECASE),
        re.compile(r"\[/?inst\]", re.IGNORECASE),
    ]

    _META_NARRATION_PATTERNS = [
        re.compile(
            r"^\s*(here is (?:the )?nudge(?: i generated(?: for you)?)?\s*[:：]?)",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(this is (?:the )?nudge(?: i generated(?: for you)?)?)\b",
            re.IGNORECASE,
        ),
        re.compile(r"^\s*(这是我(?:为你)?生成的提示\s*[:：]?)", re.IGNORECASE),
        re.compile(r"(这就是我生成的提示[。.!?]?)\s*$", re.IGNORECASE),
        re.compile(r"(let me know if you want another nudge[.?!]?)\s*$", re.IGNORECASE),
    ]

    _SPLIT_PUNCT = re.compile(r"[。！？.!?\n:：]")

    def review(self, text: str) -> Dict[str, Any]:
        raw = str(text or "").strip()
        issues: List[str] = []

        if self._contains_any(raw, self._AI_SELF_PATTERNS):
            issues.append("ai_self_reference")

        if self._contains_any(raw, self._PROMPT_RESIDUE_PATTERNS):
            issues.append("prompt_residue")

        if self._contains_any(raw, self._META_NARRATION_PATTERNS):
            issues.append("meta_narration")

        start_mismatch, end_mismatch = self._detect_edge_language_mismatch(raw)
        if start_mismatch:
            issues.append("start_language_mismatch")
        if end_mismatch:
            issues.append("end_language_mismatch")

        cleaned = self._sanitize(raw, start_mismatch=start_mismatch, end_mismatch=end_mismatch)
        if not cleaned:
            cleaned = "请先闭卷，用 90 秒写出该知识点的核心步骤，再标注你最犹豫的一步。"

        return {
            "nudge": cleaned,
            "hygiene": {
                "is_clean": len(issues) == 0,
                "should_block": len(issues) > 0,
                "issues": issues,
                "sanitized": cleaned != raw,
            },
        }

    @staticmethod
    def _contains_any(text: str, patterns: List[re.Pattern[str]]) -> bool:
        return any(p.search(text) for p in patterns)

    def _sanitize(self, text: str, start_mismatch: bool, end_mismatch: bool) -> str:
        cleaned = text

        for pattern in self._AI_SELF_PATTERNS + self._PROMPT_RESIDUE_PATTERNS + self._META_NARRATION_PATTERNS:
            cleaned = pattern.sub("", cleaned)

        if start_mismatch:
            cleaned = self._strip_first_clause(cleaned)
        if end_mismatch:
            cleaned = self._strip_last_clause(cleaned)

        cleaned = " ".join(cleaned.split())
        return cleaned.strip(" -:;,.。！？")

    def _detect_edge_language_mismatch(self, text: str) -> tuple[bool, bool]:
        if len(text) < 12:
            return False, False

        core = text[24:-24] if len(text) > 80 else text
        dominant = self._dominant_script(core)
        if dominant == "unknown":
            return False, False

        clauses = [part.strip() for part in self._SPLIT_PUNCT.split(text) if part.strip()]
        if not clauses:
            return False, False

        start_mismatch = self._is_edge_clause_mismatch(clauses[0], dominant)
        end_mismatch = len(clauses) > 1 and self._is_edge_clause_mismatch(clauses[-1], dominant)
        return start_mismatch, end_mismatch

    def _is_edge_clause_mismatch(self, clause: str, dominant: str) -> bool:
        clause_script = self._dominant_script(clause)
        if clause_script in ("unknown", dominant):
            return False
        return self._has_signal_chars(clause, clause_script)

    @staticmethod
    def _opposite_script(script: str) -> str:
        if script == "cjk":
            return "latin"
        if script == "latin":
            return "cjk"
        return "unknown"

    @staticmethod
    def _dominant_script(text: str) -> str:
        cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
        latin = sum(1 for ch in text if ("a" <= ch.lower() <= "z"))
        if cjk == 0 and latin == 0:
            return "unknown"
        return "cjk" if cjk >= latin else "latin"

    @staticmethod
    def _has_signal_chars(text: str, script: str) -> bool:
        if script == "cjk":
            return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff") >= 4
        if script == "latin":
            return sum(1 for ch in text if ("a" <= ch.lower() <= "z")) >= 6
        return False

    @staticmethod
    def _script_ratio(text: str, script: str) -> float:
        letters = [ch for ch in text if ("a" <= ch.lower() <= "z") or ("\u4e00" <= ch <= "\u9fff")]
        if not letters:
            return 0.0
        if script == "latin":
            count = sum(1 for ch in letters if "a" <= ch.lower() <= "z")
            return count / len(letters)
        if script == "cjk":
            count = sum(1 for ch in letters if "\u4e00" <= ch <= "\u9fff")
            return count / len(letters)
        return 0.0

    def _strip_first_clause(self, text: str) -> str:
        match = self._SPLIT_PUNCT.search(text)
        if not match:
            return text
        return text[match.end() :].strip()

    def _strip_last_clause(self, text: str) -> str:
        parts = self._SPLIT_PUNCT.split(text)
        if len(parts) <= 1:
            return text
        return "。".join(part.strip() for part in parts[:-1] if part.strip()).strip()
