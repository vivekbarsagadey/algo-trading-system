#!/usr/bin/env bash
set -euo pipefail

echo "Starting docker-compose services: db and redis..."
docker-compose up -d db redis

echo "Running migrations via 'migrate' service..."
docker-compose run --rm migrate

echo "Starting web and celery services..."
docker-compose up -d web celery

echo "Dev stack started."
