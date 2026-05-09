# Action-Oriented Tutor (Action Tutor)

A compact, action-first tutoring prototype built on Flask + Gradio + ChromaDB + OpenAI-compatible LLMs.
It focuses on nudges, micro-tasks, and reflection instead of full explanations.

---

## Quick Checklist
- [ ] Create a Python environment and install dependencies
- [ ] Create a `.env` file with API credentials (and optional base URL/model)
- [ ] Run tests to validate the pipeline
- [ ] Start the Flask API, then launch the Gradio UI

---

## Project Goals
- Do **not** teach with long explanations
- Do **not** provide full solutions
- Only generate:
  - Action nudges
  - Thinking provocations
  - Micro-tasks
  - Reflection questions

---

## Architecture

```
                +----------------------+
                |      Gradio UI       |
                |  upload / interact   |
                +----------+-----------+
                           |
                           v
                +----------------------+
                |      Flask API       |
                |     orchestrator     |
                +----------+-----------+
                           |
        +------------------+------------------+
        v                  v                  v
+---------------+  +---------------+  +---------------+
| TraceIndexer  |  | GapDetector   |  | NudgeEngine   |
+-------+-------+  +-------+-------+  +-------+-------+
        |                  |                  |
        v                  v                  v
+-----------------------------------------------------+
|                    ChromaDB                         |
|        learning traces / embeddings / concepts      |
+-----------------------------------------------------+
                           |
                           v
                +----------------------+
                |  OpenAI-compatible   |
                |        LLM           |
                +----------------------+
```

---

## Functional Design

### 1) Trace Indexer
**Purpose**: Parse student traces and build concept-level summaries and embeddings.

**Input** (example):
```json
{
  "student_id": "stu001",
  "notes": "...",
  "exercise_logs": [...],
  "error_history": [...],
  "timestamps": [...]
}
```

**Output** (example):
```json
{
  "concepts": [
    {
      "name": "gradient descent",
      "mastery": 0.42,
      "last_seen": "2026-05-07",
      "mistake_count": 8
    }
  ]
}
```

**Implementation highlights**:
- Local embedding with `sentence-transformers/all-MiniLM-L6-v2`
- ChromaDB for concept indexing
- Lightweight stats: attempts, mistakes, error rate, revisit gap

### 2) Gap Detector
**Purpose**: Rank weak concepts using heuristic scoring.

Heuristic:
```
score =
  0.4 * error_rate +
  0.3 * forgetting_score +
  0.2 * avoidance_score +
  0.1 * hesitation_score
```

**Output** (example):
```json
{
  "weak_concepts": [
    {"concept": "backpropagation", "reason": "high error + low revisit"}
  ]
}
```

### 3) Nudge Engine
**Purpose**: Generate short, action-oriented prompts.

System prompt (see `prompts/nudge_system.txt`) enforces:
- No direct explanations
- No full solutions
- Concise, single-concept focus

---

## Repository Layout

```
action_tutor/
├── app.py
├── requirements.txt
├── .env
├── backend/
│   ├── trace_indexer.py
│   ├── gap_detector.py
│   ├── nudge_engine.py
│   ├── chroma_store.py
│   ├── embed_model.py
│   └── llm_client.py
├── frontend/
│   └── gradio_ui.py
├── data/
│   ├── traces/
│   └── chroma/
└── prompts/
    ├── nudge_system.txt
    └── gap_analysis.txt
```

---

## Environment Setup

### 1) Create environment
```bash
conda create -n action_tutor python=3.11
conda activate action_tutor
pip install -r requirements.txt
```

### 2) .env
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.your-provider.com/v1
OPENAI_MODEL=your-model-name
```

Notes:
- `OPENAI_BASE_URL` and `OPENAI_MODEL` are optional and support OpenAI-compatible providers.
- If `OPENAI_API_KEY` is missing, the system falls back to a deterministic nudge generator (for offline demo).

---

## Run the Project

### 1) Run tests
```bash
python -m unittest discover -s tests -v
```

### 2) Start Flask API
```bash
python app.py
```

### 3) Start Gradio UI (separate terminal)
```bash
python frontend/gradio_ui.py
```

Default endpoints:
- Flask API: `http://127.0.0.1:5000`
- Gradio UI: `http://127.0.0.1:7860`

---

## API Endpoints
- `POST /upload_trace`
- `POST /detect_gap`
- `POST /generate_nudge`

Example payload:
```json
{
  "notes": "I understand gradient descent but keep confusing chain rule.",
  "exercise_logs": [
    {"concept": "backpropagation", "correct": false},
    {"concept": "gradient descent", "correct": true}
  ],
  "error_history": ["forgot chain rule", "wrong derivative sign"]
}
```

---

## Project Status
**Implemented**:
- Full Trace → Gap → Nudge pipeline
- Local MiniLM embeddings
- ChromaDB storage + fallback
- Flask API orchestration
- Gradio UI demo
- Smoke tests

**Known constraints**:
- If existing Chroma collections use a different embedding dimension, you may see a mismatch error. You can delete `data/chroma/` or use a new collection name in `app.py`.

---

## Next Steps (Suggested)
- Add batch embedding (`embed_texts`) for faster ingestion
- Expand prompt templates and add prompt quality tests
- Add Dockerfile + GitHub Actions CI
- Add a memory timeline view and per-concept learning history
- Introduce multi-step guided interaction (probe → reflection → retry)

---

## Collaboration Tips (AI Agent Friendly)
- Keep modules small and testable
- Add tests for new heuristics or prompt changes
- Prefer structured JSON outputs at module boundaries
- If adding a new model or provider, use `.env` for configuration

---

## License
Add a license file (`LICENSE`) that matches your team or institution requirements.
