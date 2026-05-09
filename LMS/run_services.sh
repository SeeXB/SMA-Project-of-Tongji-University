#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_DIR="$ROOT_DIR/ai-gateway-service"
RAG_DIR="$ROOT_DIR/rag-service"
COURSE_DIR="$ROOT_DIR/course-service"
ASSIGNMENT_DIR="$ROOT_DIR/assignment-service"
QA_DIR="$ROOT_DIR/qa-service"
MODERATION_DIR="$ROOT_DIR/moderation-service"
UNIFIED_GATEWAY_DIR="$ROOT_DIR/api-gateway-service"
RUN_DIR="$ROOT_DIR/.run"
LOG_DIR="$RUN_DIR/logs"
MAVEN_REPO_DIR="$RUN_DIR/m2repo"
MILVUS_DATA_DIR="$RUN_DIR/milvus"
MILVUS_COMPOSE_FILE="$ROOT_DIR/milvus-compose.yml"
AI_PID_FILE="$RUN_DIR/ai-gateway.pid"
RAG_PID_FILE="$RUN_DIR/rag-service.pid"
COURSE_PID_FILE="$RUN_DIR/course-service.pid"
ASSIGNMENT_PID_FILE="$RUN_DIR/assignment-service.pid"
QA_PID_FILE="$RUN_DIR/qa-service.pid"
MODERATION_PID_FILE="$RUN_DIR/moderation-service.pid"
UNIFIED_GATEWAY_PID_FILE="$RUN_DIR/api-gateway-service.pid"

AI_PORT="${AI_PORT:-8000}"
RAG_PORT="${RAG_PORT:-8001}"
COURSE_PORT="${COURSE_PORT:-8081}"
ASSIGNMENT_PORT="${ASSIGNMENT_PORT:-8082}"
QA_PORT="${QA_PORT:-8083}"
MODERATION_PORT="${MODERATION_PORT:-8084}"
UNIFIED_GATEWAY_PORT="${UNIFIED_GATEWAY_PORT:-9000}"
JAVA_VERSION_PREFERENCE="${JAVA_VERSION_PREFERENCE:-25}"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
AI_HOST="${AI_HOST:-127.0.0.1}"
MILVUS_MODE="${MILVUS_MODE:-lite}"
MILVUS_MANAGED="${MILVUS_MANAGED:-false}"

mkdir -p "$RUN_DIR" "$LOG_DIR" "$MAVEN_REPO_DIR" "$MILVUS_DATA_DIR"

print_usage() {
  cat <<'EOF'
Usage:
  ./run_services.sh start
  ./run_services.sh stop
  ./run_services.sh restart
  ./run_services.sh status

Environment variables:
  JAVA_VERSION_PREFERENCE   Preferred JDK version for Course Service (default: 25)
  AI_PORT                   AI Gateway port (default: 8000)
  RAG_PORT                  RAG Service port (default: 8001)
  COURSE_PORT               Course Service port (default: 8081)
  ASSIGNMENT_PORT           Assignment Service port (default: 8082)
  QA_PORT                   QA Service port (default: 8083)
  MODERATION_PORT           Moderation Service port (default: 8084)
  UNIFIED_GATEWAY_PORT      Public unified gateway port (default: 9000)
  AI_HOST                   AI Gateway host (default: 127.0.0.1)
  MILVUS_MODE               lite or server (default: lite)
  MILVUS_MANAGED            Start/stop Milvus server via docker compose when MILVUS_MODE=server (default: false)
  ENV_FILE                  Optional env file path (default: ./.env)
EOF
}

require_command() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd"
    exit 1
  fi
}

load_env_file() {
  if [[ -f "$ENV_FILE" ]]; then
    echo "Loading environment from $ENV_FILE"
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
  fi
}

docker_compose_cmd() {
  if docker compose version >/dev/null 2>&1; then
    echo "docker compose"
    return 0
  fi
  if command -v docker-compose >/dev/null 2>&1; then
    echo "docker-compose"
    return 0
  fi
  echo "Docker Compose is required to manage Milvus."
  exit 1
}

resolve_java_home() {
  if /usr/libexec/java_home -v "$JAVA_VERSION_PREFERENCE" >/dev/null 2>&1; then
    /usr/libexec/java_home -v "$JAVA_VERSION_PREFERENCE"
    return 0
  fi

  if /usr/libexec/java_home -v 17 >/dev/null 2>&1; then
    /usr/libexec/java_home -v 17
    return 0
  fi

  echo "Unable to find a suitable JDK. Install JDK 17+ first."
  exit 1
}

is_running() {
  local pid_file="$1"
  if [[ ! -f "$pid_file" ]]; then
    return 1
  fi

  local pid
  pid="$(cat "$pid_file")"
  if [[ -z "$pid" ]]; then
    return 1
  fi

  kill -0 "$pid" >/dev/null 2>&1
}

wait_for_port() {
  local host="$1"
  local port="$2"
  local retries="${3:-30}"

  for _ in $(seq 1 "$retries"); do
    if python3 - "$host" "$port" <<'PY' >/dev/null 2>&1
import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])
sock = socket.socket()
sock.settimeout(1)
try:
    sock.connect((host, port))
except OSError:
    sys.exit(1)
finally:
    sock.close()
sys.exit(0)
PY
    then
      return 0
    fi
    sleep 2
  done

  return 1
}

start_milvus() {
  if [[ "$MILVUS_MODE" == "lite" ]]; then
    mkdir -p "$MILVUS_DATA_DIR"
    return
  fi

  if [[ "$MILVUS_MANAGED" != "true" ]]; then
    return
  fi

  require_command docker
  local compose_cmd
  compose_cmd="$(docker_compose_cmd)"

  echo "Starting Milvus dependencies via Docker Compose..."
  $compose_cmd -f "$MILVUS_COMPOSE_FILE" up -d

  echo "Waiting for Milvus on 127.0.0.1:19530..."
  if ! wait_for_port "127.0.0.1" "19530" 45; then
    echo "Milvus did not become ready in time."
    exit 1
  fi
}

stop_milvus() {
  if [[ "$MILVUS_MODE" == "lite" ]]; then
    return
  fi

  if [[ "$MILVUS_MANAGED" != "true" ]]; then
    return
  fi

  require_command docker
  local compose_cmd
  compose_cmd="$(docker_compose_cmd)"

  echo "Stopping Milvus Docker Compose stack..."
  $compose_cmd -f "$MILVUS_COMPOSE_FILE" down
}

status_milvus() {
  if [[ "$MILVUS_MODE" == "lite" ]]; then
    echo "Milvus: lite ($MILVUS_DATA_DIR)"
    return
  fi

  if [[ "$MILVUS_MANAGED" != "true" ]]; then
    echo "Milvus: unmanaged"
    return
  fi

  require_command docker
  local compose_cmd
  compose_cmd="$(docker_compose_cmd)"
  local status
  status="$($compose_cmd -f "$MILVUS_COMPOSE_FILE" ps --status running --services 2>/dev/null || true)"
  if [[ -n "$status" ]]; then
    echo "Milvus: running"
  else
    echo "Milvus: stopped"
  fi
}

start_ai_gateway() {
  if is_running "$AI_PID_FILE"; then
    echo "AI Gateway is already running with PID $(cat "$AI_PID_FILE")."
    return
  fi

  require_command python3
  load_env_file

  if [[ "${LLM_PROVIDER:-openai}" == "openai" && -z "${OPENAI_API_KEY:-}" ]]; then
    echo "OPENAI_API_KEY is required when LLM_PROVIDER=openai."
    echo "Create $ENV_FILE or export OPENAI_API_KEY before starting."
    exit 1
  fi

  if [[ ! -d "$AI_DIR/.venv" ]]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$AI_DIR/.venv"
  fi

  echo "Installing AI Gateway dependencies..."
  "$AI_DIR/.venv/bin/pip" install -r "$AI_DIR/requirements.txt" >/dev/null

  echo "Starting AI Gateway on $AI_HOST:$AI_PORT..."
  (
    cd "$AI_DIR"
    export LLM_PROVIDER="${LLM_PROVIDER:-openai}"
    export OPENAI_API_KEY="${OPENAI_API_KEY:-}"
    export OPENAI_BASE_URL="${OPENAI_BASE_URL:-}"
    export OPENAI_MODEL="${OPENAI_MODEL:-gpt-4o-mini}"
    exec "$AI_DIR/.venv/bin/uvicorn" app.main:app --host "$AI_HOST" --port "$AI_PORT"
  ) >"$LOG_DIR/ai-gateway.log" 2>&1 &

  echo $! >"$AI_PID_FILE"
  echo "AI Gateway started with PID $(cat "$AI_PID_FILE"). Log: $LOG_DIR/ai-gateway.log"
}

start_rag_service() {
  if is_running "$RAG_PID_FILE"; then
    echo "RAG Service is already running with PID $(cat "$RAG_PID_FILE")."
    return
  fi

  require_command python3
  load_env_file

  if [[ -z "${OPENAI_API_KEY:-}" ]]; then
    echo "OPENAI_API_KEY is required for RAG embeddings."
    echo "Create $ENV_FILE or export OPENAI_API_KEY before starting."
    exit 1
  fi

  if [[ -z "${RAG_MILVUS_URI:-${MILVUS_URI:-}}" ]]; then
    echo "RAG_MILVUS_URI is required for RAG service."
    echo "Create $ENV_FILE or export RAG_MILVUS_URI before starting."
    exit 1
  fi

  if [[ ! -d "$RAG_DIR/.venv" ]]; then
    echo "Creating RAG Python virtual environment..."
    python3 -m venv "$RAG_DIR/.venv"
  fi

  echo "Installing RAG dependencies..."
  "$RAG_DIR/.venv/bin/pip" install -r "$RAG_DIR/requirements.txt" >/dev/null

  echo "Starting RAG Service on $AI_HOST:$RAG_PORT..."
  (
    cd "$RAG_DIR"
    unset MILVUS_URI
    export OPENAI_API_KEY="${OPENAI_API_KEY:-}"
    export OPENAI_BASE_URL="${OPENAI_BASE_URL:-}"
    export EMBEDDING_MODEL="${EMBEDDING_MODEL:-text-embedding-3-small}"
    export MILVUS_MODE="${MILVUS_MODE:-lite}"
    export RAG_MILVUS_URI="${RAG_MILVUS_URI:-${MILVUS_URI:-$MILVUS_DATA_DIR/canvas_ai.db}}"
    export MILVUS_TOKEN="${MILVUS_TOKEN:-}"
    export MILVUS_COLLECTION_PREFIX="${MILVUS_COLLECTION_PREFIX:-canvas_rag_}"
    export MILVUS_VECTOR_DIM="${MILVUS_VECTOR_DIM:-1536}"
    exec "$RAG_DIR/.venv/bin/uvicorn" app.main:app --host "$AI_HOST" --port "$RAG_PORT"
  ) >"$LOG_DIR/rag-service.log" 2>&1 &

  echo $! >"$RAG_PID_FILE"
  echo "RAG Service started with PID $(cat "$RAG_PID_FILE"). Log: $LOG_DIR/rag-service.log"
}

start_unified_gateway() {
  if is_running "$UNIFIED_GATEWAY_PID_FILE"; then
    echo "Unified Gateway is already running with PID $(cat "$UNIFIED_GATEWAY_PID_FILE")."
    return
  fi

  require_command python3
  load_env_file

  if [[ ! -d "$UNIFIED_GATEWAY_DIR/.venv" ]]; then
    echo "Creating Unified Gateway Python virtual environment..."
    python3 -m venv "$UNIFIED_GATEWAY_DIR/.venv"
  fi

  echo "Installing Unified Gateway dependencies..."
  "$UNIFIED_GATEWAY_DIR/.venv/bin/pip" install -r "$UNIFIED_GATEWAY_DIR/requirements.txt" >/dev/null

  echo "Starting Unified Gateway on $AI_HOST:$UNIFIED_GATEWAY_PORT..."
  (
    cd "$UNIFIED_GATEWAY_DIR"
    export COURSE_SERVICE_URL="${COURSE_SERVICE_URL:-http://127.0.0.1:$COURSE_PORT}"
    export ASSIGNMENT_SERVICE_URL="${ASSIGNMENT_SERVICE_URL:-http://127.0.0.1:$ASSIGNMENT_PORT}"
    export QA_SERVICE_URL="${QA_SERVICE_URL:-http://127.0.0.1:$QA_PORT}"
    export MODERATION_SERVICE_URL="${MODERATION_SERVICE_URL:-http://127.0.0.1:$MODERATION_PORT}"
    export AI_GATEWAY_SERVICE_URL="${AI_GATEWAY_SERVICE_URL:-http://127.0.0.1:$AI_PORT}"
    export RAG_SERVICE_URL="${RAG_SERVICE_URL:-http://127.0.0.1:$RAG_PORT}"
    exec "$UNIFIED_GATEWAY_DIR/.venv/bin/uvicorn" app.main:app --host "$AI_HOST" --port "$UNIFIED_GATEWAY_PORT"
  ) >"$LOG_DIR/api-gateway-service.log" 2>&1 &

  echo $! >"$UNIFIED_GATEWAY_PID_FILE"
  echo "Unified Gateway started with PID $(cat "$UNIFIED_GATEWAY_PID_FILE"). Log: $LOG_DIR/api-gateway-service.log"
}

start_spring_service() {
  local name="$1"
  local pid_file="$2"
  local workdir="$3"
  local port="$4"
  local log_file="$5"

  if is_running "$pid_file"; then
    echo "$name is already running with PID $(cat "$pid_file")."
    return
  fi

  require_command mvn

  local java_home
  java_home="$(resolve_java_home)"

  echo "Using JAVA_HOME=$java_home"
  echo "Starting $name on port $port..."
  (
    cd "$workdir"
    export JAVA_HOME="$java_home"
    export PATH="$JAVA_HOME/bin:$PATH"
    exec mvn -Dmaven.repo.local="$MAVEN_REPO_DIR" \
      -Dspring-boot.run.jvmArguments="-Dserver.port=$port" \
      spring-boot:run
  ) >"$log_file" 2>&1 &

  echo $! >"$pid_file"
  echo "$name started with PID $(cat "$pid_file"). Log: $log_file"
}

start_course_service() {
  start_spring_service "Course Service" "$COURSE_PID_FILE" "$COURSE_DIR" "$COURSE_PORT" "$LOG_DIR/course-service.log"
}

start_assignment_service() {
  start_spring_service "Assignment Service" "$ASSIGNMENT_PID_FILE" "$ASSIGNMENT_DIR" "$ASSIGNMENT_PORT" "$LOG_DIR/assignment-service.log"
}

start_qa_service() {
  start_spring_service "QA Service" "$QA_PID_FILE" "$QA_DIR" "$QA_PORT" "$LOG_DIR/qa-service.log"
}

start_moderation_service() {
  start_spring_service "Moderation Service" "$MODERATION_PID_FILE" "$MODERATION_DIR" "$MODERATION_PORT" "$LOG_DIR/moderation-service.log"
}

stop_service() {
  local name="$1"
  local pid_file="$2"

  if ! is_running "$pid_file"; then
    rm -f "$pid_file"
    echo "$name is not running."
    return
  fi

  local pid
  pid="$(cat "$pid_file")"
  echo "Stopping $name (PID $pid)..."
  kill "$pid" >/dev/null 2>&1 || true
  rm -f "$pid_file"
}

status_service() {
  local name="$1"
  local pid_file="$2"

  if is_running "$pid_file"; then
    echo "$name: running (PID $(cat "$pid_file"))"
  else
    echo "$name: stopped"
  fi
}

start_all() {
  start_milvus
  start_ai_gateway
  start_rag_service
  start_course_service
  start_assignment_service
  start_qa_service
  start_moderation_service
  start_unified_gateway
  echo
  echo "Services started."
  echo "Unified API:  http://localhost:$UNIFIED_GATEWAY_PORT"
  if [[ "$MILVUS_MODE" == "lite" ]]; then
    echo "Milvus:      lite ($MILVUS_DATA_DIR/canvas_ai.db)"
  else
    echo "Milvus:      http://127.0.0.1:19530"
  fi
  echo "AI Gateway:  http://localhost:$AI_PORT"
  echo "RAG API:     http://localhost:$RAG_PORT"
  echo "Course API:  http://localhost:$COURSE_PORT"
  echo "Assignment:  http://localhost:$ASSIGNMENT_PORT"
  echo "QA API:      http://localhost:$QA_PORT"
  echo "Moderation:  http://localhost:$MODERATION_PORT"
  echo "Swagger UI:  http://localhost:$UNIFIED_GATEWAY_PORT/swagger-ui/index.html"
}

stop_all() {
  stop_service "Unified Gateway" "$UNIFIED_GATEWAY_PID_FILE"
  stop_service "Moderation Service" "$MODERATION_PID_FILE"
  stop_service "QA Service" "$QA_PID_FILE"
  stop_service "Assignment Service" "$ASSIGNMENT_PID_FILE"
  stop_service "Course Service" "$COURSE_PID_FILE"
  stop_service "RAG Service" "$RAG_PID_FILE"
  stop_service "AI Gateway" "$AI_PID_FILE"
  stop_milvus
}

status_all() {
  status_milvus
  status_service "Unified Gateway" "$UNIFIED_GATEWAY_PID_FILE"
  status_service "AI Gateway" "$AI_PID_FILE"
  status_service "RAG Service" "$RAG_PID_FILE"
  status_service "Course Service" "$COURSE_PID_FILE"
  status_service "Assignment Service" "$ASSIGNMENT_PID_FILE"
  status_service "QA Service" "$QA_PID_FILE"
  status_service "Moderation Service" "$MODERATION_PID_FILE"
  echo "Logs:"
  echo "  $LOG_DIR/api-gateway-service.log"
  echo "  $LOG_DIR/ai-gateway.log"
  echo "  $LOG_DIR/rag-service.log"
  echo "  $LOG_DIR/course-service.log"
  echo "  $LOG_DIR/assignment-service.log"
  echo "  $LOG_DIR/qa-service.log"
  echo "  $LOG_DIR/moderation-service.log"
}

main() {
  local command="${1:-}"

  case "$command" in
    start)
      start_all
      ;;
    stop)
      stop_all
      ;;
    restart)
      stop_all
      start_all
      ;;
    status)
      status_all
      ;;
    *)
      print_usage
      exit 1
      ;;
  esac
}

main "$@"
