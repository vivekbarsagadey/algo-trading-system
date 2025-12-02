#!/usr/bin/env bash
set -euo pipefail

if [ -z "${DATABASE_URL:-}" ]; then
  echo "Please set DATABASE_URL (eg: export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/algo_trading)"
  exit 1
fi

echo "Running alembic upgrade head..."
alembic upgrade head
echo "Migrations applied."
