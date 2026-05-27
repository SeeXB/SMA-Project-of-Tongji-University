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

### MAS-lite flow

The current prototype keeps the original tutoring pipeline small, but now makes the agent roles explicit:

- `TutorOrchestrator`: central coordinator for request routing, aggregation, and fallback
- `TraceIndexer`: trace interpretation and concept indexing
- `GapDetector`: weak-concept diagnosis
- `NudgePlanner`: target concept selection + nudge type planning
- `NudgeEngine`: nudge generation
- `Output Hygiene Agent`: post-generation review and one-shot reflection / fallback

This is still a lightweight prototype rather than a full MAS runtime, but it is now structured around clear agent responsibilities and traceable orchestration.

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

Output hygiene guard (post-generation):
- Detects and sanitizes content that should not reach students
- Covers AI self-references, prompt residue, and language mismatch at text edges
- Returns `output_hygiene` metadata in API response for observability

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
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

Notes:
- Put this file at `action_tutor/.env`, in the same directory as `app.py`.
- `DEEPSEEK_BASE_URL` and `DEEPSEEK_MODEL` are optional. The current defaults are `https://api.deepseek.com` and `deepseek-v4-flash`.
- The code still accepts `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL` as backward-compatible fallbacks.
- If the API key is missing or the request fails, the system falls back to a deterministic nudge generator for demo use.

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
- Flask API: `http://127.0.0.1:6000`
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

`POST /generate_nudge` response includes:
- `nudge`: sanitized student-facing nudge text
- `output_hygiene`: `{ "is_clean": bool, "issues": string[], "sanitized": bool }`
- `selected_plan`: selected concept, reason, and `nudge_type`
- `agent_trace`: lightweight execution trace for the main agent roles
- `task_id`, `latency_ms`, `reflection`: observability fields for debugging and demo use

---

## Project Status
**Implemented**:
- Full Trace → Gap → Nudge pipeline
- MAS-lite `TutorOrchestrator` with explicit agent roles
- `NudgePlanner` for target selection and nudge-type routing
- Output hygiene review with one-shot reflection and fallback
- Agent trace / task-level observability fields
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
