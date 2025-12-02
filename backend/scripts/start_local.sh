#!/usr/bin/env bash
set -euo pipefail

VENV_DIR=.venv
if [ ! -d "${VENV_DIR}" ]; then
  echo "Virtual environment '${VENV_DIR}' not found. Run 'make install' or './scripts/setup_dev.sh' first."
  exit 1
fi

# Start web server using the venv python
echo "Activating venv and starting web server (uvicorn)"
source ${VENV_DIR}/bin/activate
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
