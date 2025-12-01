#!/usr/bin/env bash
# Setup development environment: create venv, upgrade pip, install dependencies
set -euo pipefail

PYTHON=${PYTHON:-python}
VENV_DIR=.venv

echo "Creating venv at ${VENV_DIR}..."
${PYTHON} -m venv ${VENV_DIR}

# Activate venv in this script
# shellcheck disable=SC1090
source ${VENV_DIR}/bin/activate

echo "Upgrading pip, setuptools, wheel..."
python -m pip install --upgrade pip setuptools wheel

echo "Installing main requirements..."
pip install -r requirements.txt

if [ -f dev-requirements.txt ]; then
  echo "Installing dev requirements..."
  pip install -r dev-requirements.txt
fi

echo "Development setup complete. Run: source ${VENV_DIR}/bin/activate" 

echo "Installed versions:"
python -c "import sys, pkgutil; import pydantic, pydantic_settings; print('python:', sys.version.split()[0]); print('pydantic:', pydantic.__version__); print('pydantic_settings:', pkgutil.find_loader('pydantic_settings') is not None)"
