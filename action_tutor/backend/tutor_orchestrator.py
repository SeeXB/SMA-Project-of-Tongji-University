from __future__ import annotations

from time import perf_counter
from typing import Any, Dict, List
from uuid import uuid4


class TutorOrchestrator:
    """Coordinate the MAS-lite tutoring flow through explicit agent roles."""

    def __init__(
        self,
        trace_indexer: Any,
        gap_detector: Any,
        nudge_planner: Any,
        nudge_engine: Any,
        output_guard: Any,
        max_reflection_rounds: int = 1,
    ) -> None:
        self.trace_indexer = trace_indexer
        self.gap_detector = gap_detector
        self.nudge_planner = nudge_planner
        self.nudge_engine = nudge_engine
        self.output_guard = output_guard
        self.max_reflection_rounds = max(0, max_reflection_rounds)

    def run(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        started_at = perf_counter()
        task_id = uuid4().hex
        agent_trace: List[Dict[str, Any]] = []

        indexed = self._run_indexer(trace, agent_trace)
        gaps = self._run_gap_detector(indexed, agent_trace)
        selected_plan = self._run_planner(gaps.get("weak_concepts", []), agent_trace)

        generation = self._run_generation_cycle(
            trace_summary=indexed.get("trace_summary", ""),
            selected_plan=selected_plan,
            agent_trace=agent_trace,
        )

        latency_ms = int((perf_counter() - started_at) * 1000)
        return {
            "task_id": task_id,
            "student_id": indexed.get("student_id", trace.get("student_id", "unknown")),
            **gaps,
            **generation,
            "selected_plan": selected_plan,
            "agent_trace": agent_trace,
            "latency_ms": latency_ms,
        }

    def _run_indexer(self, trace: Dict[str, Any], agent_trace: List[Dict[str, Any]]) -> Dict[str, Any]:
        started_at = perf_counter()
        indexed = self.trace_indexer.process(trace)
        self._append_trace(
            agent_trace,
            agent="trace_indexer_agent",
            status="ok",
            started_at=started_at,
            summary=f"concepts={len(indexed.get('concepts', []))}",
        )
        return indexed

    def _run_gap_detector(
        self,
        indexed_trace: Dict[str, Any],
        agent_trace: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        started_at = perf_counter()
        gaps = self.gap_detector.detect(indexed_trace)
        self._append_trace(
            agent_trace,
            agent="gap_diagnosis_agent",
            status="ok",
            started_at=started_at,
            summary=f"weak_concepts={len(gaps.get('weak_concepts', []))}",
        )
        return gaps

    def _run_planner(
        self,
        weak_concepts: List[Dict[str, Any]],
        agent_trace: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        started_at = perf_counter()
        plan = self.nudge_planner.plan(weak_concepts)
        concept = plan.get("concept") or "none"
        nudge_type = plan.get("nudge_type", "retrieval")
        self._append_trace(
            agent_trace,
            agent="nudge_planner_agent",
            status="ok",
            started_at=started_at,
            summary=f"concept={concept}, type={nudge_type}",
        )
        return plan

    def _run_generation_cycle(
        self,
        trace_summary: str,
        selected_plan: Dict[str, Any],
        agent_trace: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        concept = selected_plan.get("concept")
        reason = selected_plan.get("reason", "weak performance")
        nudge_type = selected_plan.get("nudge_type", "retrieval")

        raw_text = self._generate_candidate(
            trace_summary=trace_summary,
            concept=concept,
            reason=reason,
            nudge_type=nudge_type,
            agent_trace=agent_trace,
            stage="initial",
        )
        reviewed = self._review_candidate(raw_text["text"], agent_trace=agent_trace, stage="initial")

        reflection = {
            "attempted": False,
            "retries_used": 0,
            "strategy": "clean_first_pass",
            "initial_issues": [],
        }
        final_review = reviewed
        generation_attempts = [
            {
                "stage": "initial",
                **raw_text["generation_info"],
            }
        ]
        final_generation_info = dict(raw_text["generation_info"])

        if reviewed["hygiene"]["should_block"] and self.max_reflection_rounds > 0:
            reflection["attempted"] = True
            reflection["retries_used"] = 1
            reflection["initial_issues"] = list(reviewed["hygiene"]["issues"])

            rewrite_hint = self._build_rewrite_hint(reviewed["hygiene"]["issues"])
            self._append_trace(
                agent_trace,
                agent="reflection_agent",
                status="rewrite_requested",
                started_at=None,
                summary=", ".join(reviewed["hygiene"]["issues"]) or "blocked output",
            )

            rewrite_text = self._generate_candidate(
                trace_summary=trace_summary,
                concept=concept,
                reason=reason,
                nudge_type=nudge_type,
                agent_trace=agent_trace,
                stage="rewrite",
                rewrite_hint=rewrite_hint,
            )
            generation_attempts.append(
                {
                    "stage": "rewrite",
                    **rewrite_text["generation_info"],
                }
            )
            rewrite_review = self._review_candidate(
                rewrite_text["text"],
                agent_trace=agent_trace,
                stage="rewrite",
            )

            if rewrite_review["hygiene"]["should_block"]:
                reflection["strategy"] = "fallback_after_block"
                self._append_trace(
                    agent_trace,
                    agent="reflection_agent",
                    status="fallback_used",
                    started_at=None,
                    summary="deterministic fallback",
                )
                fallback_text = {
                    "text": self.nudge_engine.default_nudge(
                        concept=concept,
                        nudge_type=nudge_type,
                        language_hint=trace_summary,
                    ),
                    "generation_info": {
                        "source": "fallback_template",
                        "fallback_reason": "blocked_after_rewrite",
                        "llm_error": rewrite_text["generation_info"].get("llm_error"),
                        "model": rewrite_text["generation_info"].get("model"),
                        "nudge_type": nudge_type,
                    },
                }
                generation_attempts.append(
                    {
                        "stage": "fallback",
                        **fallback_text["generation_info"],
                    }
                )
                final_review = self._review_candidate(
                    fallback_text["text"],
                    agent_trace=agent_trace,
                    stage="fallback",
                )
                final_generation_info = dict(fallback_text["generation_info"])
            else:
                reflection["strategy"] = "rewrite_passed"
                final_review = rewrite_review
                final_generation_info = dict(rewrite_text["generation_info"])

        return {
            "nudge": final_review["nudge"],
            "concept": concept,
            "reason": reason,
            "output_hygiene": final_review["hygiene"],
            "reflection": reflection,
            "generation_info": {
                **final_generation_info,
                "attempts": generation_attempts,
            },
        }

    def _generate_candidate(
        self,
        trace_summary: str,
        concept: str | None,
        reason: str,
        nudge_type: str,
        agent_trace: List[Dict[str, Any]],
        stage: str,
        rewrite_hint: str | None = None,
    ) -> Dict[str, Any]:
        started_at = perf_counter()
        result = self.nudge_engine.generate_raw(
            concept=concept,
            reason=reason,
            trace_summary=trace_summary,
            nudge_type=nudge_type,
            rewrite_hint=rewrite_hint,
        )
        source = result["generation_info"].get("source", "unknown")
        summary = f"stage={stage}, concept={concept or 'none'}, type={nudge_type}, source={source}"
        self._append_trace(
            agent_trace,
            agent="nudge_generator_agent",
            status="ok",
            started_at=started_at,
            summary=summary,
            generation_info=result["generation_info"],
        )
        return result

    def _review_candidate(
        self,
        text: str,
        agent_trace: List[Dict[str, Any]],
        stage: str,
    ) -> Dict[str, Any]:
        started_at = perf_counter()
        reviewed = self.output_guard.review(text)
        hygiene = reviewed["hygiene"]
        if hygiene["should_block"]:
            status = "blocked"
        elif hygiene["sanitized"]:
            status = "sanitized"
        else:
            status = "clean"
        summary = f"stage={stage}, issues={len(hygiene.get('issues', []))}"
        self._append_trace(
            agent_trace,
            agent="output_hygiene_agent",
            status=status,
            started_at=started_at,
            summary=summary,
            issues=list(hygiene.get("issues", [])),
        )
        return reviewed

    @staticmethod
    def _build_rewrite_hint(issues: List[str]) -> str:
        joined = ", ".join(issues) if issues else "blocked quality checks"
        return (
            "The last draft was blocked for these issues: "
            f"{joined}. Return one concise student-facing nudge only. "
            "Do not mention AI, system prompts, or internal instructions. "
            "Keep the language consistent with the student context."
        )

    @staticmethod
    def _append_trace(
        agent_trace: List[Dict[str, Any]],
        agent: str,
        status: str,
        started_at: float | None,
        summary: str,
        **extra: Any,
    ) -> None:
        entry: Dict[str, Any] = {
            "agent": agent,
            "status": status,
            "summary": summary,
            "time_ms": 0 if started_at is None else int((perf_counter() - started_at) * 1000),
        }
        entry.update(extra)
        agent_trace.append(entry)
