#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT/logs"

SERVICES=(
  "auth|backend/auth-service|8001"
  "business|backend/business-service|8003"
  "rag|backend/rag-service|8002"
  "agent|backend/agent-service|8004"
  "gateway|backend/api-gateway|8000"
)

mkdir -p "$LOG_DIR"

  ensure_venv() {
  local service_dir="$1"
  local full_path="$ROOT/$service_dir"

  if [[ ! -d "$full_path/.venv" ]]; then
    echo "Creating virtualenv for $service_dir..."
    python3 -m venv "$full_path/.venv"
  fi

  echo "Installing dependencies for $service_dir..."
  "$full_path/.venv/bin/pip" install -q -e "$ROOT/backend/packages/contracts"
  "$full_path/.venv/bin/pip" install -q -r "$full_path/requirements.txt"
}

port_in_use() {
  lsof -i ":$1" >/dev/null 2>&1
}

start_service() {
  local name="$1"
  local service_dir="$2"
  local port="$3"

  if port_in_use "$port"; then
    echo "SKIP  $name — port $port is already in use"
    return
  fi

  ensure_venv "$service_dir"

  (
    cd "$ROOT/$service_dir"
    exec .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port "$port" --reload
  ) >"$LOG_DIR/$name.log" 2>&1 &

  echo "$!" >"$LOG_DIR/$name.pid"
  echo "START $name → http://127.0.0.1:$port (log: logs/$name.log)"
}

echo "Starting e-commerce AI agent services..."
echo

for entry in "${SERVICES[@]}"; do
  IFS='|' read -r name service_dir port <<<"$entry"
  start_service "$name" "$service_dir" "$port"
done

echo
echo "Done. Quick test:"
echo "  curl http://localhost:8000/health"
echo
echo "Stop everything:"
echo "  ./scripts/dev-stop.sh"
echo
echo "Follow logs:"
echo "  tail -f logs/gateway.log logs/agent.log"
