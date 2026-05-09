from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List


class TraceIndexer:
	def __init__(self, embed_model: Any, store: Any) -> None:
		self.embed_model = embed_model
		self.store = store

	def process(self, trace: Dict[str, Any]) -> Dict[str, Any]:
		notes = trace.get("notes", "")
		exercise_logs = trace.get("exercise_logs", []) or []
		error_history = trace.get("error_history", []) or []

		concept_stats: Dict[str, Dict[str, Any]] = {}

		for row in exercise_logs:
			concept = (row.get("concept") or "unknown").strip().lower()
			stat = concept_stats.setdefault(concept, self._empty_stat())
			stat["attempts"] += 1
			if not bool(row.get("correct", False)):
				stat["mistake_count"] += 1

			row_ts = self._parse_ts(row.get("timestamp"))
			if row_ts is not None:
				stat["timestamps"].append(row_ts)

		for text in error_history:
			msg = str(text).lower()
			for concept in concept_stats.keys() or ["unknown"]:
				if concept != "unknown" and concept in msg:
					concept_stats[concept]["mistake_count"] += 1

		if not concept_stats:
			for concept in self._extract_note_concepts(notes):
				concept_stats.setdefault(concept, self._empty_stat())

		now = datetime.now(timezone.utc).date()
		concepts: List[Dict[str, Any]] = []

		for concept, stat in concept_stats.items():
			attempts = stat["attempts"]
			mistakes = stat["mistake_count"]
			error_rate = mistakes / attempts if attempts else 0.0
			mastery = max(0.0, min(1.0, 1.0 - error_rate))

			last_seen_date = max(stat["timestamps"]).date() if stat["timestamps"] else now
			revisit_gap_days = (now - last_seen_date).days
			last_seen = last_seen_date.isoformat()

			concept_record = {
				"name": concept,
				"mastery": round(mastery, 4),
				"last_seen": last_seen,
				"mistake_count": mistakes,
				"attempts": attempts,
				"error_rate": round(error_rate, 4),
				"revisit_gap_days": revisit_gap_days,
			}
			concepts.append(concept_record)

			text_blob = f"{notes}\nErrors: {'; '.join(map(str, error_history))}"
			embedding = self.embed_model.embed_text(f"{concept}\n{text_blob}")
			self.store.add_concept(
				concept=concept,
				embedding=embedding,
				metadata={
					"concept": concept,
					"mistakes": mistakes,
					"attempts": attempts,
					"last_seen": last_seen,
				},
				document=text_blob,
			)

		concepts.sort(key=lambda row: (row["mastery"], -row["mistake_count"]))
		return {
			"student_id": trace.get("student_id", "unknown"),
			"concepts": concepts,
			"trace_summary": self._build_trace_summary(notes, concepts),
		}

	@staticmethod
	def _empty_stat() -> Dict[str, Any]:
		return {"attempts": 0, "mistake_count": 0, "timestamps": []}

	@staticmethod
	def _parse_ts(value: Any) -> datetime | None:
		if not value:
			return None
		text = str(value).replace("Z", "+00:00")
		try:
			return datetime.fromisoformat(text)
		except ValueError:
			return None

	@staticmethod
	def _extract_note_concepts(notes: str) -> List[str]:
		tokens = re.findall(r"[A-Za-z][A-Za-z\-]{3,}", (notes or "").lower())
		stop = {"this", "that", "with", "from", "without", "have", "into"}
		uniq = []
		for token in tokens:
			if token in stop or token in uniq:
				continue
			uniq.append(token)
		return uniq[:6]

	@staticmethod
	def _build_trace_summary(notes: str, concepts: List[Dict[str, Any]]) -> str:
		weakest = ", ".join(c["name"] for c in concepts[:3]) if concepts else "none"
		return f"Notes: {notes[:220]} | Weakest concepts: {weakest}"
