# 行动导向型辅导系统（Action-Oriented Tutor）原型实现方案

目标：基于 `Flask + Gradio + OpenAI + ChromaDB`，快速构建一个类似 DeepTutor 的行动导向型 AI Tutor 原型，并尽可能利用 GitHub Copilot 进行 “vibe coding”。

系统核心思想：

- 不直接讲解知识
# Action-Oriented Tutor — Prototype

This repository implements an action-oriented tutoring prototype (Action-Oriented Tutor). The goal is to quickly assemble a minimally viable pipeline that turns student learning traces into ranked knowledge gaps and then produces concise, action-oriented "nudges" rather than full explanations.

This project is designed as a research/teaching prototype that is easy to run locally and extend by collaborators.

Key technologies used:
- Flask (API orchestrator)
- Gradio (lightweight UI)
- sentence-transformers (local embedding model: all-MiniLM-L6-v2)
- ChromaDB (local vector store, optional)
- OpenAI (optional LLM for nudge generation)

Contents of this README:
- Project overview
- Architecture and components
- Data contracts and examples
- Environment and .env configuration
- How to run (backend, frontend, tests)
- Progress status
- Next steps and roadmap
- Contribution guidance

---

## 1. Overview

Action-Oriented Tutor emphasizes short, actionable prompts that trigger active retrieval, reflection, or a tiny practice step. The system does not give full solutions or long-form explanations. The core pipeline is:

- TraceIndexer: parse and index student traces (notes, exercise logs, error history)
- GapDetector: compute heuristic scores to identify weak concepts
- NudgeEngine: generate a targeted action prompt (nudge) for the top weak concept

The system can run entirely locally: embeddings are produced by a local SentenceTransformers model and stored in ChromaDB (or in-memory fallback). If you provide OpenAI credentials, the project can use an LLM to craft nudges; otherwise a deterministic fallback nudge generator is used.

---

## 2. Architecture

High-level flow:

```
User (Gradio UI)
  ↓
Flask orchestrator (app.py)
  ↓
TraceIndexer -> ChromaStore (embeddings stored)
  ↓
GapDetector -> ranked weak concepts
  ↓
NudgeEngine -> generate short, actionable nudge (optionally via LLM)
  ↓
Gradio UI displays nudge + gap diagnostics
```

Core modules (located in `backend/`):
- `trace_indexer.py` — parse incoming traces, extract simple concept statistics, push concept vectors into the store
- `gap_detector.py` — heuristic scoring (error density, forgetting, avoidance, hesitation)
- `nudge_engine.py` — read prompt templates and produce a single short nudge
- `embed_model.py` — wrapper around `sentence-transformers/all-MiniLM-L6-v2` (mean-pooling + L2 normalize)
- `chroma_store.py` — ChromaDB wrapper with simple fallback to in-memory store
- `llm_client.py` — optional OpenAI client; reads configuration from `.env`

Frontend: `frontend/gradio_ui.py` provides a simple page to upload traces and see results.

APIs (in `app.py`):
- `GET /health` — health check
- `POST /upload_trace` — accept learning trace JSON and index it
- `POST /detect_gap` — run gap detection on stored/indexed traces or supplied trace
- `POST /generate_nudge` — produce a nudge for a supplied trace (runs the full pipeline)

---

## 3. Data contracts and examples

Input trace example (JSON body):

```json
{
  "student_id": "stu001",
  "notes": "I understand gradient descent but keep confusing chain rule during backpropagation.",
  "exercise_logs": [
    {"concept": "backpropagation", "correct": false, "timestamp": "2026-05-01"},
    {"concept": "gradient descent", "correct": true, "timestamp": "2026-05-02"}
  ],
  "error_history": ["forgot chain rule", "wrong derivative sign"]
}
```

Index output (example simplified):

```json
{
  "concepts": [
    {"name": "backpropagation", "mastery": 0.18, "last_seen": "2026-05-01", "mistake_count": 3}
  ],
  "trace_summary": "..."
}
```

Gap detection output:

```json
{
  "weak_concepts": [
    {"concept": "backpropagation", "score": 0.83, "reason": "high error_rate + low revisit"}
  ]
}
```

Nudge example:

```json
{ "nudge": "Close your notes and derive only the gradient flow from loss to the final hidden layer." }
```

---

## 4. Environment configuration

Requirements:
- Python 3.10+ (3.11 recommended)
- Conda (optional) or a virtual environment

Key Python dependencies are in `requirements.txt`. Important packages that may require additional downloads:
- `sentence-transformers` (for `all-MiniLM-L6-v2` local embeddings)
- `transformers`, `torch` (installed as part of sentence-transformers; CPU-only or GPU installation recommended if available)
- `chromadb` (optional for persistent vector store)

Windows CMD example to create environment and install dependencies:

```bat
cd /d D:\source\PycharmProjects\action_tutor
conda create -n action_tutor python=3.11 -y
conda activate action_tutor
pip install -r requirements.txt
```

If you don't use conda, use python -m venv:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

.env file (create at project root):

```
# Optional: OpenAI configuration. Leave blank to use local/fallback generation.
OPENAI_API_KEY=your_openai_api_key_here
# If you use an OpenAI-compatible endpoint (e.g., OA-hosted or self-hosted), set this.
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# Optional: change chroma persistence directory
CHROMA_DB_DIR=./data/chroma
```

Notes:
- The project now uses the local `sentence-transformers/all-MiniLM-L6-v2` model for embeddings. The first run will download the model weights (a few hundred MB). If running in an air-gapped environment, pre-download the model using `sentence-transformers` on a connected machine and copy the cache directory.
- If you plan to use GPU acceleration for embeddings, install a PyTorch build that supports CUDA.

---

## 5. Running the project

Start the Flask backend (simple single-process server used for development):

```bat
cd /d D:\source\PycharmProjects\action_tutor
python app.py
```

Start the Gradio frontend (it will call the local Flask APIs):

```bat
python frontend\gradio_ui.py
```

Run tests:

```bat
python -m unittest discover -s tests -v
```

Basic API usage examples (Windows cmd / PowerShell friendly):

Upload a trace and generate a nudge (curl example):

```bat
curl -X POST "http://127.0.0.1:5000/generate_nudge" -H "Content-Type: application/json" -d "@sample_trace.json"
```

Or using Python `requests`:

```py
import requests
trace = { ... }  # load the JSON shown earlier
resp = requests.post('http://127.0.0.1:5000/generate_nudge', json=trace)
print(resp.json())
```

---

## 6. Project status (progress)

Completed for MVP:
- Core backend modules implemented: `TraceIndexer`, `GapDetector`, `NudgeEngine`
- Local embedding via `sentence-transformers/all-MiniLM-L6-v2` implemented in `backend/embed_model.py`
- `LLMClient` updated to read OpenAI settings from `.env` (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`) with safe fallback behavior
- Simple ChromaDB wrapper with in-memory fallback
- Gradio UI to upload traces and display nudges
- Unit smoke tests in `tests/` covering embedding and the pipeline

---

## 7. Next steps / roadmap

Short-term (next 1–2 sprints):
- Add more robust concept extraction (e.g., noun-phrase chunking + named entity recognition)
- Improve gap scoring with calibrated forgetting curve and time-decay
- Add batch indexing API and streaming ingestion for multiple traces
- Provide a demo dataset under `data/traces/` and a simple script to replay traces

Medium-term:
- Personalization: model student mastery curves and adapt nudge difficulty
- Add multi-step guided interaction (probe → reflection → retry → escalate)
- Integrate basic CI: run unit tests and lint on pull requests

Long-term:
- Experiment with retrieval-augmented nudges that reference student's past attempts (but still avoid full solutions)
- Add analytics dashboard for teachers

---

## 8. Contribution guide

Suggested workflow for collaborators:

1. Fork the repository and create a feature branch: `git checkout -b feat/your-feature`
2. Follow the existing code style and add unit tests for new logic
3. Open a Pull Request and describe the change and rationale

Coding conventions:
- Keep modules small and single-responsibility
- Add unit tests for any scoring or transformation logic

Recommended PR checklist:
- [ ] Tests added (or rationale for why not)
- [ ] Documentation updated (README or module docstring)
- [ ] No sensitive keys in commit history

---

## 9. Troubleshooting & Tips

- If embeddings are slow on first run: model weights are being downloaded; be patient.
- If you have GPU and want faster embeddings, install a CUDA-enabled PyTorch wheel.
- If `chromadb` fails to initialize, the project will fall back to an in-memory store; check logs for path issues and ensure `CHROMA_DB_DIR` is writeable.
- If OpenAI calls fail, verify `OPENAI_API_KEY` and optionally `OPENAI_BASE_URL`. The system will fallback to a deterministic nudge generator if the LLM is unavailable.

---

## 10. License

This project is intended for academic and educational use. Consider adding an open-source license such as MIT.

---

If you want, I can:
1. Commit this README into the repository now (I can update `README.md`) and run the test suite.
2. Create a `sample_trace.json` under `data/traces/` and a one-click demo script to run the pipeline.

Tell me which of the two you'd like me to do next and I'll proceed.

------

### 2. Learning Trace → Gap → Nudge Pipeline

这是最关键的研究逻辑。

------

### 3. “不解释，只推动思考”

这是区别于普通 ChatBot Tutor 的核心。