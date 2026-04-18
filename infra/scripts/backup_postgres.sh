#!/bin/sh
set -e

PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_DIR"

BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
POSTGRES_DB_NAME="${POSTGRES_DB:-mail_assistant}"
POSTGRES_USER_NAME="${POSTGRES_USER:-mail_assistant}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUT_FILE="$BACKUP_DIR/postgres_${POSTGRES_DB_NAME}_$TIMESTAMP.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "[backup] creating dump: $OUT_FILE"
docker compose exec -T db pg_dump -U "$POSTGRES_USER_NAME" "$POSTGRES_DB_NAME" | gzip > "$OUT_FILE"

echo "[backup] pruning files older than $RETENTION_DAYS days"
find "$BACKUP_DIR" -type f -name "postgres_*.sql.gz" -mtime +"$RETENTION_DAYS" -delete

echo "[backup] done"
