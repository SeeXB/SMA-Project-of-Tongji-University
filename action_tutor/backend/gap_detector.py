from __future__ import annotations

import math
from typing import Any, Dict, List


class GapDetector:
	def __init__(self, lambda_decay: float = 0.08) -> None:
		self.lambda_decay = lambda_decay
		self.weights = {
			"error_rate": 0.4,
			"forgetting": 0.3,
			"avoidance": 0.2,
			"hesitation": 0.1,
		}

	def detect(self, indexed_trace: Dict[str, Any]) -> Dict[str, Any]:
		weak: List[Dict[str, Any]] = []

		for concept in indexed_trace.get("concepts", []):
			attempts = concept.get("attempts", 0)
			error_rate = float(concept.get("error_rate", 0.0))
			revisit_gap_days = int(concept.get("revisit_gap_days", 0))
			mastery = float(concept.get("mastery", 0.0))

			retention = math.exp(-self.lambda_decay * max(0, revisit_gap_days))
			forgetting_score = 1.0 - retention

			mentions = max(1, concept.get("mistake_count", 0))
			avoidance_score = mentions / (mentions + attempts + 1)
			hesitation_score = 1.0 / (attempts + 1)

			score = (
				self.weights["error_rate"] * error_rate
				+ self.weights["forgetting"] * forgetting_score
				+ self.weights["avoidance"] * avoidance_score
				+ self.weights["hesitation"] * hesitation_score
			)

			weak.append(
				{
					"concept": concept["name"],
					"score": round(score, 4),
					"reason": self._reason(error_rate, forgetting_score, avoidance_score, mastery),
					"signals": {
						"error_rate": round(error_rate, 4),
						"forgetting_score": round(forgetting_score, 4),
						"avoidance_score": round(avoidance_score, 4),
						"hesitation_score": round(hesitation_score, 4),
					},
				}
			)

		weak.sort(key=lambda row: row["score"], reverse=True)
		return {"weak_concepts": weak, "weights": self.weights}

	@staticmethod
	def _reason(error_rate: float, forgetting: float, avoidance: float, mastery: float) -> str:
		pairs = [
			("high error", error_rate),
			("low revisit", forgetting),
			("avoidance pattern", avoidance),
			("low mastery", 1.0 - mastery),
		]
		top = sorted(pairs, key=lambda item: item[1], reverse=True)[:2]
		return " + ".join(label for label, _ in top)
