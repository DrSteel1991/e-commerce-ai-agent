#!/usr/bin/env bash
# Ensures every backend service has a shared INTERNAL_SERVICE_API_KEY in its .env.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KEY_FILE="$ROOT/.internal_api_key"

if [[ ! -f "$KEY_FILE" ]]; then
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 32 >"$KEY_FILE"
  else
    python3 -c "import secrets; print(secrets.token_hex(32))" >"$KEY_FILE"
  fi
  echo "Created shared internal API key at .internal_api_key"
fi

SHARED_KEY="$(tr -d '[:space:]' <"$KEY_FILE")"

SERVICES=(
  api-gateway
  agent-service
  business-service
  rag-service
)

fix_corrupted_env_file() {
  local env_file="$1"
  python3 - "$env_file" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
if not path.exists():
    sys.exit(0)

text = path.read_text()
lines = []
changed = False

for line in text.splitlines():
    if (
        "INTERNAL_SERVICE_API_KEY=" in line
        and not line.startswith("INTERNAL_SERVICE_API_KEY=")
    ):
        prefix, suffix = line.split("INTERNAL_SERVICE_API_KEY=", 1)
        lines.append(prefix.rstrip())
        lines.append(f"INTERNAL_SERVICE_API_KEY={suffix}")
        changed = True
    else:
        lines.append(line)

fixed = "\n".join(lines)
if text.endswith("\n"):
    fixed += "\n"

if changed:
    path.write_text(fixed)
    print(f"  repaired malformed lines in {path.name}")
PY
}

set_or_append_key() {
  local env_file="$1"
  local key="$2"

  if grep -q "^INTERNAL_SERVICE_API_KEY=" "$env_file"; then
    if [[ "$OSTYPE" == darwin* ]]; then
      sed -i '' "s/^INTERNAL_SERVICE_API_KEY=.*/INTERNAL_SERVICE_API_KEY=$key/" "$env_file"
    else
      sed -i "s/^INTERNAL_SERVICE_API_KEY=.*/INTERNAL_SERVICE_API_KEY=$key/" "$env_file"
    fi
    return
  fi

  # Ensure file ends with a newline before appending.
  if [[ -s "$env_file" ]]; then
    last_char="$(tail -c 1 "$env_file" || true)"
    if [[ "$last_char" != "" ]]; then
      printf '\n' >>"$env_file"
    fi
  fi

  echo "INTERNAL_SERVICE_API_KEY=$key" >>"$env_file"
}

for service in "${SERVICES[@]}"; do
  env_file="$ROOT/backend/$service/.env"
  example_file="$ROOT/backend/$service/.env.example"

  if [[ ! -f "$env_file" ]]; then
    if [[ -f "$example_file" ]]; then
      cp "$example_file" "$env_file"
      echo "Created $env_file from .env.example"
    else
      touch "$env_file"
    fi
  fi

  fix_corrupted_env_file "$env_file"
  set_or_append_key "$env_file" "$SHARED_KEY"
  echo "Synced INTERNAL_SERVICE_API_KEY → backend/$service/.env"
done

echo "Done. Restart backend services: make dev"
