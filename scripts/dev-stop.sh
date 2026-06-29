#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT/logs"

PORTS=(8000 8001 8002 8003 8004)

stop_port() {
  local port="$1"
  local pids

  pids="$(lsof -ti ":$port" 2>/dev/null || true)"

  if [[ -z "$pids" ]]; then
    echo "SKIP  port $port — nothing running"
    return
  fi

  kill $pids 2>/dev/null || true
  echo "STOP  port $port"
}

echo "Stopping services..."

for port in "${PORTS[@]}"; do
  stop_port "$port"
done

rm -f "$LOG_DIR"/*.pid 2>/dev/null || true

echo
echo "All dev services stopped."
