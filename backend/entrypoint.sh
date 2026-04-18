#!/bin/sh
set -e

echo "Starting container..."

bool_true() {
  case "$(echo "$1" | tr '[:upper:]' '[:lower:]')" in
    1|true|yes|on) return 0 ;;
    *) return 1 ;;
  esac
}

DB_ENGINE=${DB_ENGINE:-sqlite}
RUN_MIGRATIONS=${RUN_MIGRATIONS:-true}
COLLECT_STATIC=${COLLECT_STATIC:-true}

# Wait for PostgreSQL only when using postgres.
if [ "$DB_ENGINE" = "postgres" ] && [ -n "$POSTGRES_HOST" ]; then
  echo "Waiting for database at $POSTGRES_HOST:${POSTGRES_PORT:-5432}..."

  until nc -z "$POSTGRES_HOST" "${POSTGRES_PORT:-5432}"; do
    echo "Database is unavailable - sleeping"
    sleep 2
  done

  echo "Database is up!"
fi

if bool_true "$RUN_MIGRATIONS"; then
  echo "Running migrations..."
  python manage.py migrate --noinput
else
  echo "Skipping migrations (RUN_MIGRATIONS=$RUN_MIGRATIONS)"
fi

if bool_true "$COLLECT_STATIC"; then
  echo "Collecting static files..."
  python manage.py collectstatic --noinput
else
  echo "Skipping static collection (COLLECT_STATIC=$COLLECT_STATIC)"
fi

# Start server/process
exec "$@"
