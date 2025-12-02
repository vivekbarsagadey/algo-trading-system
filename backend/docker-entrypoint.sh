#!/usr/bin/env bash
set -euo pipefail

function wait_for_db() {
  local database_url=${DATABASE_URL:-}
  if [ -z "$database_url" ]; then
    echo "DATABASE_URL is not set — skipping DB wait"
    return 0
  fi

  echo "Waiting for database to be available..."
  # Parse out host & port from DATABASE_URL (basic parsing for postgres)
  # Example: postgresql://user:pass@host:5432/db
  host=$(echo "$database_url" | sed -E 's#.*@([^:/]+):([0-9]+).*#\1#' || true)
  port=$(echo "$database_url" | sed -E 's#.*@[^:/]+:([0-9]+).*#\1#' || true)
  if [ -z "$host" ] || [ -z "$port" ]; then
    echo "Could not detect host/port from DATABASE_URL — skipping DB wait"
    return 0
  fi
  while ! nc -z "$host" "$port"; do
    echo "Database not ready ($host:$port); sleeping 1s"
    sleep 1
  done
  echo "Database appears ready!"
}

echo "Running docker-entrypoint: run DB migrations then start server"
wait_for_db

if command -v alembic >/dev/null 2>&1; then
  echo "Running alembic upgrade head"
  alembic upgrade head
else
  echo "alembic not found; skipping migrations"
fi

echo "Starting uvicorn"
exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} ${UV_ARGS:-}
