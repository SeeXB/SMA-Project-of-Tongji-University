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
from backend.trace_indexer import TraceIndexer


def create_app() -> Flask:
	load_dotenv()

	app = Flask(__name__)

	embed_model = EmbeddingModel()
	store = ChromaStore(
		persist_dir=str(Path(__file__).resolve().parent / "data" / "chroma"),
		collection_name="learning_traces_minilm_l6_v2",
	)
	trace_indexer = TraceIndexer(embed_model=embed_model, store=store)
	gap_detector = GapDetector()
	llm_client = LLMClient()
	nudge_engine = NudgeEngine(llm_client=llm_client)

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
		indexed = trace_indexer.process(trace)
		gaps = gap_detector.detect(indexed)
		nudge = nudge_engine.generate(
			weak_concepts=gaps.get("weak_concepts", []),
			trace_summary=indexed.get("trace_summary", ""),
		)
		return jsonify({**gaps, **nudge})

	@app.errorhandler(Exception)
	def handle_error(error: Exception) -> Any:
		return jsonify({"error": type(error).__name__, "message": str(error)}), 500

	return app


if __name__ == "__main__":
	application = create_app()
	application.run(host="0.0.0.0", port=6000, debug=True)

