#!/bin/sh
set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <backup-file.sql.gz>"
  exit 1
fi

BACKUP_FILE="$1"
if [ ! -f "$BACKUP_FILE" ]; then
  echo "Backup file not found: $BACKUP_FILE"
  exit 1
fi

PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_DIR"

POSTGRES_DB_NAME="${POSTGRES_DB:-mail_assistant}"
POSTGRES_USER_NAME="${POSTGRES_USER:-mail_assistant}"

echo "[restore] restoring $BACKUP_FILE into $POSTGRES_DB_NAME"
gzip -dc "$BACKUP_FILE" | docker compose exec -T db psql -U "$POSTGRES_USER_NAME" "$POSTGRES_DB_NAME"
echo "[restore] done"
