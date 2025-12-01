# Algo Trading System

A monorepo containing a FastAPI backend service and an Expo React Native mobile app for algorithmic trading.

## Project Structure

```
.
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── api/            # API routes (auth, broker, strategies)
│   │   ├── core/           # Core configuration and security
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic services
│   │   └── workers/        # Redis workers for execution
│   ├── requirements.txt
│   └── Dockerfile
├── apps/
│   └── mobile/             # Expo React Native app
│       ├── app/            # App screens and navigation
│       ├── components/     # Reusable components
│       └── package.json
├── docker-compose.yml      # Postgres + Redis services
├── .env.example            # Environment variables template
└── README.md
```

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+ and npm
- Expo CLI (`npm install -g expo-cli`)
- Optional: `uv` CLI (`pip install --upgrade uv`) — used here for dev environment management

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/vivekbarsagadey/algo-trading-system.git
cd algo-trading-system
```

### 2. Set up environment variables

If you're using the `uv` workflow, `uv init` will copy `.env.example` to `.env`.
Otherwise copy the example file manually:

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start infrastructure services

```bash
docker-compose up -d
```

### 4. Set up the backend

You can use the `uv` CLI (recommended if you have it installed) or create a venv manually.

Option A — Using the `uv` CLI (recommended):

```bash
cd backend

# Install the `uv` CLI if you don't have it already (system or pipx)
pip install --upgrade uv

# Initialize the project: create a `.venv` and copy `.env.example` to `.env`
uv init

# Sync dependencies (installs from `requirements.txt`/`pyproject.toml`)
uv sync

# Run the development server
# NOTE: `uv run` expects a command to execute (like `uvicorn`). Passing `app.main:app` directly causes a spawn error.
# Use `uv run uvicorn <module>` to run the server via `uv`.
uv run uvicorn app.main:app --reload
```

Option B — Using a standard Python venv:

```bash
cd backend

# Create and activate a venv (POSIX):
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables file
cp .env.example .env

# Start the dev server (use `uv` if present; `uv run` needs the binary to spawn)
# Preferred (using `uv` to run `uvicorn`):
uv run uvicorn app.main:app --reload
# Alternative directly with uvicorn (no `uv` required):
uvicorn app.main:app --reload
# or
uvicorn app.main:app --reload
```

Troubleshooting
-----------------

- If you see an error like `ImportError: email-validator is not installed, run pip install pydantic[email]` when starting the app, install the missing dependency:

```bash
# If you're using the uv workflow:
uv sync

# Or install manually in your venv:
pip install 'pydantic[email]'
# or:
pip install email-validator
```

- If you're using Docker, update your `backend/requirements.txt` (this project now pins `pydantic[email]` and `email-validator`) and rebuild the image:

```bash
docker-compose build backend
docker-compose up -d
```

### 5. Set up the mobile app

```bash
cd apps/mobile
npm install
npx expo start
```

## Features

### Backend (FastAPI)
- **Authentication**: JWT-based user authentication
- **Broker Connect**: Integration with trading brokers
- **Strategies**: Create and manage trading strategies
- **Workers**: Redis-backed workers for trade execution

### Mobile App (Expo React Native)
- **Login**: User authentication screen
- **Broker Setup**: Configure broker connections
- **Strategy Management**: View and manage trading strategies

## License

MIT