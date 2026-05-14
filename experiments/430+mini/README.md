**Patch summary:** Replace the original Chinese README with a comprehensive English README that includes project overview, architecture, data contracts, environment and .env examples, installation and run instructions (Windows/cmd), tests, progress, roadmap, and collaboration notes to help new contributors get started quickly.

# Action-Oriented Tutor — Prototype

This repository contains a working prototype of an Action-Oriented Tutor (AOT). The core idea is to drive learner activity through short, focused "nudges" (micro-tasks, provocations, reflection prompts) rather than providing long explanations or complete solutions.

Primary goals:
- Offer a minimal, composable pipeline: TraceIndexer → GapDetector → NudgeEngine
- Be runnable locally with deterministic fallbacks (local sentence-transformer embeddings and fallback LLM prompt behavior)
- Provide clear data contracts so collaborators can extend components (embeddings, storage, scoring, prompt engineering)

Table of contents
- Project overview
- Architecture
- Key components and data contracts
- Environment & configuration (.env)
- Installation & run instructions (Windows / cmd.exe shown)
- Tests
- Current progress and included modules
- Next steps and roadmap
- Contribution notes

---

## Project overview

This prototype is intended as a research / teaching scaffold that demonstrates:
- How to convert student traces (notes, exercise logs, error history) into indexed concept representations
- How to detect weak concepts using simple heuristics
- How to generate concise action-oriented nudges using an LLM with constraints (no full solutions, short prompts)

The implementation prioritizes developer productivity and reproducibility: it can run without cloud APIs (local embedding model) and gracefully uses OpenAI when configured.

---

## Architecture

High level flow:

- Gradio UI (frontend) — upload traces, view detected gaps and nudges
- Flask API (orchestrator) — central HTTP endpoints
- TraceIndexer — parse traces, extract concepts, generate embeddings, persist to ChromaDB (or in-memory fallback)
- GapDetector — score concepts for weakness (error density, forgetting, avoidance, hesitation)
- NudgeEngine — construct a short system + user prompt and call LLM (OpenAI) or fallback generator
- ChromaDB (vector storage) — store document chunks, embeddings, and metadata

ASCII overview:

    Gradio UI --> Flask API --> { TraceIndexer, GapDetector, NudgeEngine } --> ChromaDB
                                                     |
                                                     --> OpenAI (optional)

---

## Key components and data contracts

- Trace input (example JSON accepted by `/upload_trace`):

```json
{
  "student_id": "stu001",
  "notes": "I understand gradient descent but confuse chain rule during backpropagation.",
  "exercise_logs": [
    {"concept": "backpropagation", "correct": false, "timestamp": "2026-05-01T10:00:00"},
    {"concept": "gradient descent", "correct": true, "timestamp": "2026-05-02T12:00:00"}
  ],
  "error_history": ["forgot chain rule", "wrong derivative sign"]
}
```

- TraceIndexer output (indexed summary):

```json
{
  "student_id": "stu001",
  "concepts": [
    {
      "name": "backpropagation",
      "mastery": 0.23,
      "attempts": 10,
      "mistakes": 7,
      "last_seen": "2026-05-01",
      "revisit_gap_days": 13,
      "embedding": [/* vector floats */]
    }
  ],
  "trace_summary": "short human-readable summary"
}
```

- GapDetector output (example):

```json
{
  "weak_concepts": [
    {"concept": "backpropagation", "score": 0.82, "reason": "high error_rate + long_gap"}
  ]
}
```

- NudgeEngine input: the top weak concept + trace_summary. Output is a single short action-oriented prompt (JSON-safe):

```json
{ "nudge": "Close your notes and write the first step to compute the gradient for the final layer. Stop after the first expression and note where you hesitated." }
```

---

## Environment & configuration (.env)

Create a file named `.env` in the repository root. The prototype reads configuration from environment variables. Minimal recommended variables:

```
# OpenAI / LLM (optional)
OPENAI_API_KEY=sk-....
OPENAI_BASE_URL=https://api.openai.com/v1        # optional, used by some deployments
OPENAI_MODEL=gpt-4o-mini                         # optional default model name

# ChromaDB persistence path (optional)
CHROMA_DB_DIR=./data/chroma

# Embedding model (sentence-transformers name)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

Notes:
- If `OPENAI_API_KEY` is not provided, the project will use a safe deterministic fallback for nudge generation (so the system still runs).
- The code expects `EMBEDDING_MODEL` to be a Hugging Face sentence-transformers style model id. The repository includes a local deterministic fallback if the package is not installed.

---

## Installation (Windows / cmd.exe)

Prerequisites:
- Python 3.11+ recommended
- Git

Install dependencies (this project uses pip and the `requirements.txt` in the repo):

```bat
cd /d D:\source\PycharmProjects\action_tutor
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Notes about heavy packages:
- `sentence-transformers` may pull `transformers` and `torch`. If you run into installation or performance issues, consider installing a CPU-only `torch` wheel or using a smaller embedding model.
- If you don't want to install `sentence-transformers`, the project contains a lightweight deterministic fallback embedding class for development.

Optional (recommended for fastest local embedding inference):
- If you have a CUDA GPU, install a matching `torch` build per https://pytorch.org.

---

## Run the services

1) Start Flask API (single-process prototype):

```bat
cd /d D:\source\PycharmProjects\action_tutor
set FLASK_APP=app.py
python app.py
```

By default the app listens on 127.0.0.1:5000. Check `app.py` for configuration and to enable debug mode.

2) Start Gradio UI (optional, standalone runner included):

```bat
cd /d D:\source\PycharmProjects\action_tutor
python frontend\gradio_ui.py
```

The Gradio frontend interacts with the Flask API endpoints defined below.

---

## HTTP Endpoints

- POST /upload_trace — accepts a trace JSON and indexes it. Returns indexed summary.
- POST /detect_gap — accepts an indexed trace or trace id and returns ranked weak concepts.
- POST /generate_nudge — accepts detected gaps (or a trace) and returns a single nudge JSON.

Example: generate a nudge by calling the Flask route with a raw trace (the backend will index -> detect -> generate):

```bat
curl -X POST http://127.0.0.1:5000/generate_nudge -H "Content-Type: application/json" -d @data/traces/sample_trace.json
```

---

## Tests

Run the unit tests included in `tests/`:

```bat
cd /d D:\source\PycharmProjects\action_tutor
.venv\Scripts\activate
python -m unittest discover -s tests -v
```

The tests cover embedding behavior and a lightweight pipeline smoke test.

---

## Current progress (what's implemented in this repo)

- Flask API with the three main endpoints: `/upload_trace`, `/detect_gap`, `/generate_nudge`
- `backend/embed_model.py`: uses either `sentence-transformers/all-MiniLM-L6-v2` (if installed/configured) or a deterministic local fallback
- `backend/trace_indexer.py`: parsing traces, extracting concept-level stats and embeddings
- `backend/chroma_store.py`: ChromaDB wrapper with in-memory fallback
- `backend/gap_detector.py`: heuristic scoring for weak concepts
- `backend/llm_client.py`: reads `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL` from environment and calls OpenAI; falls back to deterministic generator
- `backend/nudge_engine.py`: prompt construction and JSON-safe output
- `frontend/gradio_ui.py`: simple Gradio UI for uploading traces and showing nudges
- `tests/`: embedding and pipeline smoke tests

---

## Next steps / roadmap (recommended contributions)

Short-term (high priority):
- Add a small sample dataset: `data/traces/sample_trace.json` and helper script to quickly demo the pipeline
- Improve GapDetector scoring using telemetry from multiple students and add calibration tests
- Add richer prompt templates for multi-step nudges (probe → reflect → retry)

Medium-term:
- Integrate user authentication and per-student persistent stores
- Build a simple curriculum generator which maps weak concepts to short practice sequences
- Add analytics dashboards (mastery over time, revisits) in Gradio UI

Long-term / research:
- Temporal models of forgetting and mastery (exponential decay / Bayesian Knowledge Tracing)
- Adaptive multi-turn nudges that form short guided learning episodes

---

## Collaboration notes & contribution guide

- Use GitHub issues to propose changes to heuristics or prompt templates.
- Keep changes to public APIs (Flask endpoints, TraceIndexer outputs) backward compatible where possible.
- Add tests for new scoring rules and new prompt behaviors.

Quick checklist for a new collaborator:
1. Clone repo
2. Create `.venv` and install requirements
3. Add `.env` with `EMBEDDING_MODEL` and optionally OpenAI keys
4. Run `python -m unittest discover -s tests -v` and fix failing tests locally
5. Start Flask and Gradio to do manual exploration

---

## Troubleshooting

- If embedding model download fails: either install `sentence-transformers` manually or set `EMBEDDING_MODEL` to a locally available model. The code has a fallback deterministic embedder for development.
- If OpenAI requests fail, verify `OPENAI_API_KEY` and `OPENAI_BASE_URL`. The prototype remains usable without OpenAI.

---

## License & attribution

This project is a prototype scaffold for education and research. Add a LICENSE file in the repo root before wide redistribution. Credit the authors and any model licenses (e.g., Hugging Face model licenses) when publishing.

---

If you'd like, I can now:
1) Add `data/traces/sample_trace.json` plus a `scripts/demo_pipeline.py` that runs the full pipeline end-to-end; or
2) Run the unit tests in this environment and report the results.

Pick 1 or 2 and I'll proceed.
