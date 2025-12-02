# Algo Trading System (Backend)

This repository contains the backend API for an algorithmic trading system built with FastAPI. It includes authentication, broker integrations, strategy management, Celery background tasks, and SQLAlchemy models for persistence.

---

## 🚀 Quick Start

Prerequisites:
- Python 3.11+
- Redis (for Celery broker and backend)
- PostgreSQL (optional, for persistent storage)

Clone and install dependencies:

```bash
git clone <repo-url>
cd backend
python -m venv .venv
source .venv/bin/activate
# Ensure pip, setuptools & wheel are up-to-date and available inside the venv
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r dev-requirements.txt  # optional: install lint/test tools
# If you want editor/CI tools for linting or type-checking, install dev dependencies
pip install -r dev-requirements.txt
```

Create an environment variables file `.env` (copy from `.env.example`) and update with your configuration.
The application uses Pydantic `BaseSettings` and loads `.env` automatically from the project root.

Run the server locally using the `uv` wrapper (development):

```bash
./uv --reload
```

Open docs: `http://localhost:8000/docs`

---

## ⚙️ Environment Configuration

Create a `.env` file at the repository root with the following environment variables (or use `DATABASE_URL` directly):

```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=algo_trading
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

BROKER_API_KEY=
BROKER_API_SECRET=
```

- `SECRET_KEY` must be a strong random secret in production.
- `ALGORITHM` and `ACCESS_TOKEN_EXPIRE_MINUTES` control JWT behavior.
- If you set `DATABASE_URL` (e.g. a Neon or Heroku-provided URL), the app will prefer it over individual POSTGRES_* fields.
Notes:
- `SECRET_KEY` must be a strong random secret in production.
- `ALGORITHM` and `ACCESS_TOKEN_EXPIRE_MINUTES` control JWT behavior.
- If you set `DATABASE_URL` (e.g. a Neon or Heroku-provided URL), the app will prefer it over individual POSTGRES_* fields.
If your editor (e.g. VS Code) reports "Unable to import 'pydantic'" or similar problems, it usually means the editor is not using the project's virtual environment. To fix:

1. Ensure you've installed dependencies in the virtual environment (see above).
2. In VS Code: open the Command Palette (Cmd+Shift+P) -> `Python: Select Interpreter` and choose the venv at `./.venv/bin/python`.
3. Restart the editor so linters like `pylint`/`mypy` use the environment's installed packages.

If issues persist, install dev tools in the venv and restart the editor:
```bash
pip install -r dev-requirements.txt

You can test quickly whether `pydantic` is available in your active Python by running:

```bash
python -c "import pydantic; print('pydantic', pydantic.__version__)"
```

If `mypy` was complaining about missing stubs, we've added a `mypy.ini` that enables `ignore_missing_imports` — you can remove that later once your environment and dev dependencies are stable.

If you need the editor to always pick the venv, ensure the `.vscode/settings.json` is used or set the interpreter path in the workspace settings.
```
- `SECRET_KEY` must be a strong random secret in production.
- `ALGORITHM` and `ACCESS_TOKEN_EXPIRE_MINUTES` control JWT behavior.

---

## 🗄 Database Setup

This app uses SQLAlchemy with a PostgreSQL backend by default. You can use SQLite or any SQL database supported by SQLAlchemy by changing `database_url` in `app/core/config.py`.

To initialize the database (creating tables):

```bash
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

For migrations, Alembic is included in `requirements.txt` — set up alembic with `alembic init` and configure `env.py` to import `app.core.database` models.

---

## 🧩 Celery (Background Tasks)

Celery is configured with Redis as the broker + backend. The Celery app is available at `app/workers/celery_app.py`.

Run a worker (from repo root):

```bash
celery -A app.workers.celery_app.celery_app worker -l info
```

Example tasks are defined in `app/workers/tasks.py`:
- `execute_strategy` - simulate executing a trading strategy
- `process_market_data` - process market events
- `send_trade_notification` - send notifications about trades

---

## 🧾 Docker

Build and run the Docker image (the `uv` wrapper runs inside the container):

```bash
docker build -t algo-trading-backend .
docker run -d -p 8000:8000 --env-file .env --name algo-trading-server algo-trading-backend
```

Notes:
- Ensure Redis and Postgres are accessible from the container (via network or host host.docker.internal for macOS).

---

## 🔐 Authentication

The app uses JWT access tokens with OAuth2 password flow for login.

Endpoints:
- `POST /api/v1/auth/register` — register new user (email + password + full_name)
- `POST /api/v1/auth/login` — login using form (`username` and `password`) and return `access_token`
- `GET /api/v1/auth/me` — get current user profile (requires bearer token header)

Example registration:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"secret","full_name":"Test User"}'
```

Login (NOTE: OAuth2 password request requires `username` and `password` in form data):

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=test@example.com&password=secret'
```

Copy the returned `access_token` and use it as an Authorization header for protected endpoints:

```
Authorization: Bearer <access_token>
```

---

## 🔌 Broker Integration API

These endpoints manage broker connections (demo in-memory store):

- `POST /api/v1/broker/connect`
  - Payload: `{ "broker_name": "fyers", "api_key": "...", "api_secret": "...", "user_id": "123" }`
  - Response: `broker_name`, `user_id`, `is_connected`

- `DELETE /api/v1/broker/disconnect/{user_id}`
  - Disconnect broker for the user.

- `GET /api/v1/broker/status/{user_id}`
  - Get status of connected broker for the user.

- `GET /api/v1/broker/supported`
  - Returns list of supported brokers

Broker adapters are implemented under `app/brokers/`:
- `angel_one.py` — uses `smartapi-python` and optional TOTP
- `fyers.py` — integrates with `fyers_apiv3`
- `dhan.py` — integrates via `httpx` calls to Dhan API

In production, broker connections should be persisted in the database and credentials handled securely — the in-memory store is for demo only.

---

## 📈 Strategies API

Manage trading strategies (DB-backed):

- `POST /api/v1/strategies/` — create a strategy
- `GET /api/v1/strategies/` — list strategies, optional `?user_id=` to filter
- `GET /api/v1/strategies/{id}` — get single strategy
- `PATCH /api/v1/strategies/{id}` — update name, params, or status
- `DELETE /api/v1/strategies/{id}` — delete a strategy
- `POST /api/v1/strategies/{id}/start` — set status to active
- `POST /api/v1/strategies/{id}/stop` — set status to stopped

Example create:

```bash
curl -X POST http://localhost:8000/api/v1/strategies/ \
  -H 'Content-Type: application/json' \
  -d '{"name":"Mean rev","strategy_type":"mean_reversion","symbol":"SBIN","parameters":{"lookback":20},"user_id":1}'
```

Notes:

- Strategies are persisted in the database using `app/models/strategy.py` and SQLAlchemy. We newly implemented DB CRUD for strategies (migrated off the in-memory `strategies_db`).

- Use Alembic to create the database tables and run migrations before starting the service (see Migration section below).

### Database Migrations (Alembic)

Alembic is included and the repository contains a `alembic` folder with an initial migration that creates `users` and `strategies` tables.

To create a database and run migrations locally:

```bash
# 1) For local dev using Docker Compose: start DB and Redis
docker-compose up -d db redis

# 2) Ensure DATABASE_URL env var points at the running dev DB (docker-compose sets host 'db')
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/algo_trading

# 3) Run migrations
./scripts/migrate_db.sh
```

Alternatively, if you’re running the web service inside Docker Compose, you can run the migration step via an ephemeral container:

```bash
docker-compose run --rm web ./scripts/migrate_db.sh
```

Or run the `migrate` service directly which reads `DATABASE_URL` from env:

```bash
docker-compose run --rm migrate
```

---

## 🧪 Testing

No tests are included at the moment. You can add PyTest and build CI for unit tests, integration tests, and API contract tests.

---

## 🧭 Development Tips

- Use `--reload` with Uvicorn for code autoreload (dev only).
- Use `--reload` with Uvicorn for code autoreload (dev only).

```bash
./uv --reload
```

### Makefile & Dev scripts

To simplify common workflows, a `Makefile` and convenience scripts are included. Typical commands:

```bash
# Create venv and install dependencies
make install
# Create venv and install dev dependencies (formatters/lint/test tools)
make install-dev
# Start local Postgres & Redis and start web + celery using docker-compose
make up
# Run database migrations
make migrate
# Run the application in the current venv
make web
# Run the worker
make celery
```

You can also use the `scripts` helper scripts:

- `scripts/dev_up.sh` — starts docker compose, runs migrations, and starts services (web & celery).
- `scripts/dev_down.sh` — stops docker compose services.
- `scripts/start_local.sh` — run the web server locally using venv.


- Create an alias for convenience (optional):

```bash
# Add alias for current terminal session
alias uv='./uv'

# Or create a symlink to /usr/local/bin (requires sudo on macOS)
sudo ln -s "$(pwd)/uv" /usr/local/bin/uv
```

### Linting and Formatting (development)

All tools are configured to use a maximum line length of 200 characters to support long lines commonly used in configuration or multi-line SQL snippets.

You can validate formatting and lint rules locally. We provide configurations for Black (200 char line), Flake8 (200 char), and Pylint.

```bash
# Check code formatting with Black
python -m black --check .

# Run Flake8 using the repo .flake8 configuration
python -m flake8 --config .flake8

# Run Pylint (note: config in .pylintrc)
python -m pylint --rcfile=.pylintrc app
```

Additionally, we include a `pre-commit` configuration. To install the git hook and run it locally:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

- For background tasks, run Celery worker and ensure Redis is up and accessible.
- Use a separate environment for production, and never commit `.env` with secrets.

## 🧾 Notes & Next Steps

- Replace in-memory stores (users, brokers, strategies) with DB-backed storage for production.
- Implement robust error handling and secrets management for broker credentials.
- Add logging + observability (Prometheus, Sentry) for real-world usage.

---

## 🔌 Pre-commit Configuration

Additionally, we include a `pre-commit` configuration. To install the git hook and run it locally:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

- For background tasks, run Celery worker and ensure Redis is up and accessible.

- Use a separate environment for production, and never commit `.env` with secrets.
If you'd like, I can:
- Add sample Docker Compose for running Postgres + Redis + Backend.
- Add Alembic migrations config and an initial migration.
- Add basic unit tests and a sample Postman collection for the API.

Note: `requirements.txt` and `dev-requirements.txt` packages have been updated to the latest versions available on PyPI as of 2025-12-02. If you run into compatibility issues, you can adjust versions in the files accordingly.

Happy to continue — tell me which of the optional items you'd like next! ✅
