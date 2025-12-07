# 🚀 Algo Trading System

**High-Speed, Multi-Tenant Automated Trading Platform**

A production-ready algorithmic trading system that enables retail traders to automate simple trading strategies through a mobile app, with backend execution powered by Redis-based in-memory computation.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![React Native](https://img.shields.io/badge/React%20Native-Expo-purple.svg)](https://expo.dev)
[![Redis](https://img.shields.io/badge/Redis-7.0+-red.svg)](https://redis.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [API Endpoints](#-api-endpoints)
- [Strategy Workflow](#-strategy-workflow)
- [Security](#-security)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

Algo Trading System allows retail traders to:

- **Register/Login** with secure JWT authentication
- **Connect Broker** accounts (Zerodha, Dhan, Fyers, Angel One)
- **Create Simple Strategies** with:
  - Symbol (e.g., RELIANCE, NIFTY)
  - Buy Time & Sell Time
  - Mandatory Stop-Loss
  - Quantity
- **Start/Stop** automated trading
- **Monitor** live execution status

The backend ensures **microsecond-level Redis access**, **exact execution timing**, **fail-safe order placement**, and **multi-tenant isolation**.

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Mobile App (React Native)                   │
│              Register → Connect Broker → Create Strategy        │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTPS/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                             │
│   ┌───────────────┐   ┌───────────────┐   ┌─────────────────┐  │
│   │  Auth Service │   │Strategy Service│   │ Broker Connector│  │
│   └───────────────┘   └───────────────┘   └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────────┐
│  Redis Cache  │     │   Scheduler   │     │  Market Listener  │
│ (Runtime State)│     │ (Time Triggers)│     │ (WebSocket Feed)  │
└───────────────┘     └───────────────┘     └───────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                    ┌─────────────────────┐
                    │  Execution Engine   │
                    │  (Order Placement)  │
                    └─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   PostgreSQL (RDS)  │
                    │  Users / Strategies │
                    └─────────────────────┘
```

---

## ✨ Features

### Backend (FastAPI + Redis)
| Feature | Description |
|---------|-------------|
| **JWT Authentication** | Secure user registration and login |
| **Broker Integration** | Zerodha, Dhan, Fyers, Angel One support |
| **Strategy Management** | Create, update, start/stop strategies |
| **Time-Based Execution** | APScheduler for BUY/SELL triggers |
| **Event-Based Execution** | WebSocket price monitoring for stop-loss |
| **Redis Runtime** | In-memory state for sub-300ms execution |
| **Multi-Tenant Isolation** | User A never affects User B |
| **Fail-Safe Orders** | Retry logic, circuit breakers |

### Mobile App (React Native / Expo)
| Feature | Description |
|---------|-------------|
| **Minimal UI** | Simple, beginner-friendly interface |
| **Secure Storage** | JWT tokens in SecureStore |
| **Strategy Creator** | Symbol, times, SL, quantity inputs |
| **Live Status** | Real-time strategy status updates |
| **Broker Setup** | Easy API key configuration |

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend API** | FastAPI (Python 3.11+) |
| **Mobile App** | React Native / Expo |
| **In-Memory Runtime** | Redis |
| **Database** | PostgreSQL |
| **Task Scheduler** | APScheduler / Celery |
| **Authentication** | JWT (JSON Web Tokens) |
| **Encryption** | AES-256 for broker credentials |
| **Deployment** | AWS (ECS/EKS, RDS, ElastiCache) |
| **Monitoring** | AWS CloudWatch |

---

## 📁 Project Structure

```
algo-trading-system/
├── backend/                    # FastAPI backend service
│   ├── app/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── api/               # API routes
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── broker.py      # Broker connection endpoints
│   │   │   └── strategies.py  # Strategy management endpoints
│   │   ├── brokers/           # Broker integrations
│   │   │   ├── base.py        # Base broker class
│   │   │   ├── zerodha.py     # Zerodha integration
│   │   │   ├── dhan.py        # Dhan integration
│   │   │   ├── fyers.py       # Fyers integration
│   │   │   └── angel_one.py   # Angel One integration
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py      # Environment settings
│   │   │   ├── database.py    # Database connection
│   │   │   └── security.py    # Security utilities
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── user.py        # User model
│   │   │   ├── broker.py      # Broker credentials model
│   │   │   └── strategy.py    # Strategy model
│   │   ├── services/          # Business logic
│   │   └── workers/           # Background workers
│   │       ├── celery_app.py  # Celery configuration
│   │       └── tasks.py       # Background tasks
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Test suite
│   ├── requirements.txt
│   └── Dockerfile
├── apps/
│   └── mobile/                # React Native Expo app
│       ├── app/               # Screens and navigation
│       ├── components/        # Reusable UI components
│       ├── store/             # Zustand state management
│       ├── services/          # API client services
│       └── package.json
├── docs/                      # Documentation
│   ├── SRS.MD                 # Software Requirements Specification
│   ├── HLD.MD                 # High-Level Design
│   ├── LLD.MD                 # Low-Level Design
│   ├── API DOCUMENTATION.MD   # API reference
│   └── ...                    # Additional docs
├── docker-compose.yml         # Postgres + Redis services
├── .env.example               # Environment template
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 20+ (LTS) and npm
- Expo CLI (`npm install -g expo-cli`)
- Optional: `uv` CLI for faster Python dependency management

### 1. Clone the Repository

```bash
git clone https://github.com/vivekbarsagadey/algo-trading-system.git
cd algo-trading-system
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/algo_trading

# Redis
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET_KEY=your-secret-key
AES_MASTER_KEY=your-32-byte-encryption-key

# Broker APIs (optional for development)
ZERODHA_API_KEY=your-zerodha-key
```

### 3. Start Infrastructure Services

```bash
docker-compose up -d
```

This starts PostgreSQL and Redis containers.

### 4. Set Up the Backend

**Option A: Using `uv` (recommended)**

```bash
cd backend
pip install --upgrade uv
uv sync
uv run uvicorn app.main:app --reload
```

**Option B: Using standard venv**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 5. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### 6. Set Up the Mobile App

```bash
cd apps/mobile
npm install
npx expo start
```

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get JWT |
| GET | `/auth/me` | Get current user |

### Broker
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/broker/connect` | Add broker credentials |
| GET | `/broker/status` | Validate broker connection |
| DELETE | `/broker/{broker_id}` | Remove broker |

### Strategies
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/strategy/create` | Create new strategy |
| GET | `/strategy/list` | List user strategies |
| POST | `/strategy/{id}/start` | Start strategy execution |
| POST | `/strategy/{id}/stop` | Stop strategy execution |
| GET | `/strategy/{id}/status` | Get strategy status |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/health/ready` | Readiness check |

---

## 📊 Strategy Workflow

```
User Creates Strategy
        │
        ▼
┌───────────────────┐
│  Validate Inputs  │ ← Symbol, Buy Time, Sell Time, SL, Qty
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Store in Redis   │ ← Active runtime state
│  Store in Postgres│ ← Persistent storage
└───────────────────┘
        │
        ▼
┌───────────────────┐
│ Register Scheduler│ ← APScheduler jobs for buy/sell times
└───────────────────┘
        │
        ▼
┌───────────────────────────────────────────┐
│           EXECUTION PHASE                 │
├───────────────────────────────────────────┤
│ • At Buy Time → Place BUY order           │
│ • Market Listener → Monitor price         │
│ • If Price ≤ SL → Place SELL (Stop-Loss)  │
│ • At Sell Time → Place SELL order         │
└───────────────────────────────────────────┘
        │
        ▼
┌───────────────────┐
│   Log & Update    │ ← Order logs, status updates
└───────────────────┘
```

---

## 🔐 Security

| Aspect | Implementation |
|--------|----------------|
| **Authentication** | JWT tokens with expiration |
| **Broker Credentials** | AES-256 encryption at rest |
| **API Security** | HTTPS, rate limiting |
| **Multi-Tenancy** | User isolation via `user_id` filtering |
| **Stop-Loss** | Mandatory for all strategies |
| **Password Storage** | Bcrypt/Argon2 hashing |

---

## 📚 Documentation

Comprehensive documentation is available in the `docs/` folder:

| Document | Description |
|----------|-------------|
| [SRS.MD](docs/SRS.MD) | Software Requirements Specification |
| [HLD.MD](docs/HLD.MD) | High-Level Design |
| [LLD.MD](docs/LLD.MD) | Low-Level Design |
| [API DOCUMENTATION.MD](docs/API%20DOCUMENTATION.MD) | Database & Redis Schema |
| [BACKEND-SPEC.md](docs/BACKEND-SPEC.md) | Backend architecture details |
| [FRONTEND-SPEC.md](docs/FRONTEND-SPEC.md) | Mobile app specification |
| [USER-JOURNEY.md](docs/USER-JOURNEY.md) | End-to-end user journey |
| [BROKER-INTEGRATION-SEQUENCE.md](docs/BROKER-INTEGRATION-SEQUENCE.md) | Broker API flow |
| [EXECUTION-ENGINE-INTEGRATION.MD](docs/EXECUTION-ENGINE-INTEGRATION.MD) | Execution engine design |
| [STATE-MACHINE.md](docs/STATE-MACHINE.md) | Strategy state transitions |

---

## 🧪 Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_integration_strategies.py
```

---

## 🐳 Docker Deployment

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 📞 Support

- **Documentation**: Check the `docs/` folder
- **Issues**: Open a GitHub issue
- **Email**: Contact the maintainers

---

**Built with ❤️ for retail traders who want simple, reliable trading automation.**