#!/usr/bin/env bash
set -euo pipefail

echo "Stopping dev services..."
docker-compose down

echo "Done."
