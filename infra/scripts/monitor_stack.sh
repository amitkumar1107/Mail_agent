#!/bin/sh
set -e

PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_DIR"

echo "[monitor] docker compose ps"
docker compose ps

echo "[monitor] app health"
if curl -fsS http://localhost/health/ >/dev/null; then
  echo "[monitor] health: OK"
else
  echo "[monitor] health: FAIL"
  exit 1
fi

echo "[monitor] recent web logs"
docker compose logs --tail=40 web
