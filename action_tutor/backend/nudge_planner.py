from __future__ import annotations

from typing import Any, Dict, List


class NudgePlanner:
    """Select a target concept and a lightweight nudge strategy."""

    def plan(self, weak_concepts: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not weak_concepts:
            return {
                "concept": None,
                "reason": "no weak concept detected",
                "nudge_type": "retrieval",
                "score": 0.0,
                "signals": {},
            }

        target = weak_concepts[0]
        signals = target.get("signals", {})
        return {
            "concept": target.get("concept", "unknown"),
            "reason": target.get("reason", "weak performance"),
            "nudge_type": self._pick_nudge_type(signals),
            "score": float(target.get("score", 0.0)),
            "signals": signals,
        }

    @staticmethod
    def _pick_nudge_type(signals: Dict[str, Any]) -> str:
        error_rate = float(signals.get("error_rate", 0.0))
        forgetting_score = float(signals.get("forgetting_score", 0.0))
        avoidance_score = float(signals.get("avoidance_score", 0.0))
        hesitation_score = float(signals.get("hesitation_score", 0.0))

        if error_rate >= 0.6:
            return "correction"
        if forgetting_score >= 0.55:
            return "retrieval"
        if avoidance_score >= 0.45:
            return "comparison"
        if hesitation_score >= 0.3:
            return "reflection"
        return "retrieval"
