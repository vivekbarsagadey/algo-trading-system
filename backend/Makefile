SHELL := /bin/bash

VENV ?= .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: help venv install install-dev up down migrate run web celery fmt lint test clean

help:
	@echo "Available targets:"
	@sed -n '1,120p' Makefile | grep -E '^\S+:' | sed 's/:.*//' | xargs -n1 -I{} echo "  - {}"

venv:
	@echo "Creating virtual environment $(VENV) and upgrading pip..."
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip setuptools wheel

install: venv
	@echo "Installing application dependencies..."
	$(PIP) install -r requirements.txt

install-dev: install
	@echo "Installing dev dependencies..."
	$(PIP) install -r dev-requirements.txt

up:
	@echo "Starting local development services (db, redis) with docker-compose..."
	docker-compose up -d db redis

down:
	@echo "Stopping local development services (docker-compose down)..."
	docker-compose down

migrate:
	@echo "Running Alembic migrations using scripts/migrate_db.sh"
	./scripts/migrate_db.sh

web:
	@echo "Starting the web server in the current environment..."
	$(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

celery:
	@echo "Starting a celery worker in the current environment"
	celery -A app.workers.celery_app worker -l info

fmt:
	@echo "Formatting repository (isort + black)"
	$(PYTHON) -m isort .
	$(PYTHON) -m black .

lint:
	@echo "Running static analysis (flake8 + pylint + mypy)"
	$(PYTHON) -m flake8 --config .flake8 || true
	$(PYTHON) -m pylint --rcfile=.pylintrc app || true
	$(PYTHON) -m mypy --config-file mypy.ini app || true

test:
	@echo "Running tests (pytest)"
	$(PYTHON) -m pytest -q

clean:
	@echo "Cleaning development artifacts"
	rm -rf $(VENV)

run:
	@echo "Alias for 'web' to match other developer expectations"
	$(MAKE) web

dev-up:
	@echo "Start local containers, migrations, and app via docker-compose"
	./scripts/dev_up.sh

dev-down:
	@echo "Stop dev services via docker-compose"
	./scripts/dev_down.sh

