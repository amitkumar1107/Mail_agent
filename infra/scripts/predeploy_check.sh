#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE="${1:-.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "[ERROR] Env file not found: $ENV_FILE"
  exit 1
fi

echo "[INFO] Using env file: $ENV_FILE"

echo "[INFO] Basic required env checks"
required=(DJANGO_SECRET_KEY DJANGO_ALLOWED_HOSTS EMAIL_BACKEND)
for key in "${required[@]}"; do
  if ! grep -q "^${key}=" "$ENV_FILE"; then
    echo "[ERROR] Missing $key in $ENV_FILE"
    exit 1
  fi
done

if grep -Eq '^DJANGO_SECRET_KEY=(change-me|django-insecure-change-me|change-me-to-a-long-random-secret)$' "$ENV_FILE"; then
  echo "[ERROR] DJANGO_SECRET_KEY is still placeholder"
  exit 1
fi

if grep -q '^DJANGO_ALLOWED_HOSTS=\s*$' "$ENV_FILE"; then
  echo "[ERROR] DJANGO_ALLOWED_HOSTS is empty"
  exit 1
fi

echo "[INFO] Running Django system check"
(
  cd backend
  set -a
  source "$ROOT_DIR/$ENV_FILE"
  set +a
  python3 manage.py check
)

echo "[INFO] Pre-deploy checks passed"
