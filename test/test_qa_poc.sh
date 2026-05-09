#!/usr/bin/env bash

set -euo pipefail

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$TEST_DIR/.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
OUTPUT_DIR="${OUTPUT_DIR:-$TEST_DIR/output}"
GATEWAY_URL="${GATEWAY_URL:-http://localhost:9000}"
COURSE_ID="${COURSE_ID:-course_cs101}"
USER_ID="${USER_ID:-student_123}"
POC_ENV_FILE="$OUTPUT_DIR/poc.env"
AI_PORT="${AI_PORT:-18000}"
RAG_PORT="${RAG_PORT:-18001}"
COURSE_PORT="${COURSE_PORT:-18081}"
ASSIGNMENT_PORT="${ASSIGNMENT_PORT:-18082}"
QA_PORT="${QA_PORT:-18083}"
MODERATION_PORT="${MODERATION_PORT:-18084}"
UNIFIED_GATEWAY_PORT="${UNIFIED_GATEWAY_PORT:-19000}"

mkdir -p "$OUTPUT_DIR"

load_env() {
  if [[ -f "$ENV_FILE" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
  fi
}

prepare_poc_env_file() {
  cp "$ENV_FILE" "$POC_ENV_FILE"
  python3 - "$POC_ENV_FILE" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines()

overrides = {
    "EMBEDDING_PROVIDER": "local",
    "EMBEDDING_MODEL": "text-embedding-v3",
}

seen = set()
new_lines = []
for line in lines:
    if "=" not in line or line.lstrip().startswith("#"):
        new_lines.append(line)
        continue
    key, _ = line.split("=", 1)
    if key in overrides:
        new_lines.append(f"{key}={overrides[key]}")
        seen.add(key)
    else:
        new_lines.append(line)

for key, value in overrides.items():
    if key not in seen:
        new_lines.append(f"{key}={value}")

path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
PY
}

wait_for_http() {
  local url="$1"
  local retries="${2:-60}"

  for _ in $(seq 1 "$retries"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
  done

  return 1
}

json_get() {
  local file="$1"
  local expr="$2"
  python3 - "$file" "$expr" <<'PY'
import json
import sys

file_path = sys.argv[1]
expr = sys.argv[2]

with open(file_path, "r", encoding="utf-8") as handle:
    data = json.load(handle)

current = data
for part in expr.split("."):
    if part.isdigit():
        current = current[int(part)]
    else:
        current = current.get(part)
    if current is None:
        break

if isinstance(current, (dict, list)):
    print(json.dumps(current, ensure_ascii=False))
elif current is None:
    print("")
else:
    print(str(current))
PY
}

seed_rag() {
  curl -fsS -X POST "$GATEWAY_URL/rag/store" \
    -H "Content-Type: application/json" \
    -d "{
      \"knowledgeBase\": \"$COURSE_ID\",
      \"documentId\": \"ddd_week4_slides\",
      \"metadata\": {
        \"courseId\": \"$COURSE_ID\",
        \"sourceTitle\": \"Week 4 DDD Slides\",
        \"documentType\": \"slide-deck\"
      },
      \"chunks\": [
        {
          \"chunkId\": \"ddd-week4-1\",
          \"text\": \"Bounded contexts define clear boundaries around a domain model. Each bounded context should own its own ubiquitous language and reduce conceptual confusion between teams.\",
          \"sequence\": 1
        },
        {
          \"chunkId\": \"ddd-week4-2\",
          \"text\": \"An aggregate is a consistency boundary. Updates inside an aggregate should preserve business invariants, and external references should usually point to the aggregate root.\",
          \"sequence\": 2
        },
        {
          \"chunkId\": \"ddd-week4-3\",
          \"text\": \"Repositories provide a collection-like abstraction for loading and saving aggregates. They help keep domain logic independent from persistence concerns.\",
          \"sequence\": 3
        }
      ]
    }" | tee "$OUTPUT_DIR/rag_store.json"
}

run_qa_calls() {
  curl -fsS -X POST "$GATEWAY_URL/qa/ask" \
    -H "Content-Type: application/json" \
    -d "{
      \"courseId\": \"$COURSE_ID\",
      \"userId\": \"$USER_ID\",
      \"question\": \"What is a bounded context?\",
      \"topK\": 3
    }" | tee "$OUTPUT_DIR/qa_ask_1.json"

  local history_id
  history_id="$(json_get "$OUTPUT_DIR/qa_ask_1.json" "historyId")"
  if [[ -z "$history_id" ]]; then
    echo "Failed to extract historyId from first QA response." >&2
    exit 1
  fi

  curl -fsS -X POST "$GATEWAY_URL/qa/ask" \
    -H "Content-Type: application/json" \
    -d "{
      \"courseId\": \"$COURSE_ID\",
      \"userId\": \"$USER_ID\",
      \"historyId\": \"$history_id\",
      \"question\": \"How is it different from an aggregate?\",
      \"topK\": 3
    }" | tee "$OUTPUT_DIR/qa_ask_2.json"

  curl -fsS "$GATEWAY_URL/qa/history-list?userId=$USER_ID&courseId=$COURSE_ID" \
    | tee "$OUTPUT_DIR/qa_history_list.json"

  curl -fsS "$GATEWAY_URL/qa/history/$history_id" \
    | tee "$OUTPUT_DIR/qa_history_detail.json"
}

print_summary() {
  local history_id
  history_id="$(json_get "$OUTPUT_DIR/qa_ask_1.json" "historyId")"

  cat <<EOF

PoC execution completed.
Artifacts saved in: $OUTPUT_DIR

Key results:
- historyId: $history_id
- first answer: $(json_get "$OUTPUT_DIR/qa_ask_1.json" "answer")
- second answer: $(json_get "$OUTPUT_DIR/qa_ask_2.json" "answer")
- first citation title: $(json_get "$OUTPUT_DIR/qa_ask_1.json" "citations.0.sourceTitle")
- history list count: $(python3 - "$OUTPUT_DIR/qa_history_list.json" <<'PY'
import json
import sys
with open(sys.argv[1], "r", encoding="utf-8") as handle:
    data = json.load(handle)
print(len(data.get("histories", [])))
PY
)
- history detail message count: $(python3 - "$OUTPUT_DIR/qa_history_detail.json" <<'PY'
import json
import sys
with open(sys.argv[1], "r", encoding="utf-8") as handle:
    data = json.load(handle)
print(len(data.get("messages", [])))
PY
)
EOF
}

main() {
  load_env
  prepare_poc_env_file

  export AI_PORT
  export RAG_PORT
  export COURSE_PORT
  export ASSIGNMENT_PORT
  export QA_PORT
  export MODERATION_PORT
  export UNIFIED_GATEWAY_PORT
  export GATEWAY_URL="http://localhost:$UNIFIED_GATEWAY_PORT"
  export AI_GATEWAY_BASE_URL="http://127.0.0.1:$AI_PORT"
  export RAG_SERVICE_BASE_URL="http://127.0.0.1:$RAG_PORT"
  export AI_GATEWAY_SERVICE_URL="http://127.0.0.1:$AI_PORT"
  export RAG_SERVICE_URL="http://127.0.0.1:$RAG_PORT"
  export COURSE_SERVICE_URL="http://127.0.0.1:$COURSE_PORT"
  export ASSIGNMENT_SERVICE_URL="http://127.0.0.1:$ASSIGNMENT_PORT"
  export QA_SERVICE_URL="http://127.0.0.1:$QA_PORT"
  export MODERATION_SERVICE_URL="http://127.0.0.1:$MODERATION_PORT"
  export ENV_FILE="$POC_ENV_FILE"

  echo "Restarting services..."
  bash "$ROOT_DIR/run_services.sh" restart

  echo "Waiting for unified gateway..."
  if ! wait_for_http "$GATEWAY_URL/health" 90; then
    echo "Unified gateway did not become ready in time." >&2
    exit 1
  fi

  echo "Seeding RAG knowledge base..."
  seed_rag

  echo
  echo "Running QA PoC calls..."
  run_qa_calls

  print_summary
}

main "$@"
