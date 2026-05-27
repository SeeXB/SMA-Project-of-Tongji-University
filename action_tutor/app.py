from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from backend.chroma_store import ChromaStore
from backend.embed_model import EmbeddingModel
from backend.gap_detector import GapDetector
from backend.llm_client import LLMClient
from backend.nudge_engine import NudgeEngine
from backend.nudge_planner import NudgePlanner
from backend.output_guard import NudgeOutputGuard
from backend.trace_indexer import TraceIndexer
from backend.tutor_orchestrator import TutorOrchestrator


def create_app(
	embed_model: EmbeddingModel | None = None,
	store: ChromaStore | None = None,
	trace_indexer: TraceIndexer | None = None,
	gap_detector: GapDetector | None = None,
	llm_client: LLMClient | None = None,
	output_guard: NudgeOutputGuard | None = None,
	nudge_planner: NudgePlanner | None = None,
	nudge_engine: NudgeEngine | None = None,
	orchestrator: TutorOrchestrator | None = None,
) -> Flask:
	load_dotenv()

	app = Flask(__name__)

	if trace_indexer is None:
		embed_model = embed_model or EmbeddingModel()
		store = store or ChromaStore(
			persist_dir=str(Path(__file__).resolve().parent / "data" / "chroma"),
			collection_name="learning_traces_minilm_l6_v2",
		)
		trace_indexer = TraceIndexer(embed_model=embed_model, store=store)

	gap_detector = gap_detector or GapDetector()
	llm_client = llm_client or LLMClient()
	output_guard = output_guard or NudgeOutputGuard()
	nudge_planner = nudge_planner or NudgePlanner()
	nudge_engine = nudge_engine or NudgeEngine(llm_client=llm_client, output_guard=output_guard)
	orchestrator = orchestrator or TutorOrchestrator(
		trace_indexer=trace_indexer,
		gap_detector=gap_detector,
		nudge_planner=nudge_planner,
		nudge_engine=nudge_engine,
		output_guard=output_guard,
	)

	@app.get("/health")
	def health() -> Any:
		return jsonify({"status": "ok"})

	@app.post("/upload_trace")
	def upload_trace() -> Any:
		trace: Dict[str, Any] = request.get_json(silent=True) or {}
		indexed = trace_indexer.process(trace)
		return jsonify(indexed)

	@app.post("/detect_gap")
	def detect_gap() -> Any:
		trace: Dict[str, Any] = request.get_json(silent=True) or {}
		indexed = trace_indexer.process(trace)
		gaps = gap_detector.detect(indexed)
		return jsonify(gaps)

	@app.post("/generate_nudge")
	def generate_nudge() -> Any:
		trace: Dict[str, Any] = request.get_json(silent=True) or {}
		result = orchestrator.run(trace)
		return jsonify(result)

	@app.errorhandler(Exception)
	def handle_error(error: Exception) -> Any:
		return jsonify({"error": type(error).__name__, "message": str(error)}), 500

	return app


if __name__ == "__main__":
	application = create_app()
	application.run(host="0.0.0.0", port=6000, debug=True)

