#!/bin/sh
set -e

echo "Starting container..."

# Wait for PostgreSQL
if [ -n "$POSTGRES_HOST" ]; then
  echo "Waiting for database at $POSTGRES_HOST:${POSTGRES_PORT:-5432}..."
  
  until nc -z "$POSTGRES_HOST" "${POSTGRES_PORT:-5432}"; do
    echo "Database is unavailable - sleeping"
    sleep 2
  done

  echo "Database is up!"
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting Gunicorn..."
exec "$@"