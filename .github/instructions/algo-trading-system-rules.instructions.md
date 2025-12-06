---
applyTo: "**"
---

# Algo Trading System Project-Specific Rules

> **LLM Knowledge Assumption**: This guide assumes you already know Python, FastAPI, React Native, Redis, PostgreSQL, and common design patterns. It contains **ONLY Algo Trading System-specific rules, conventions, and implementations** that differ from standard practices.

**Last Updated**: December 7, 2025  
**Stack**: FastAPI • Python 3.11+ • React Native/Expo • Redis • PostgreSQL • AWS

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Critical Policies](#critical-policies)
3. [Project Structure](#project-structure)
4. [Code Patterns](#code-patterns)
5. [Data Models](#data-models)
6. [Security & Compliance](#security--compliance)
7. [Quick Reference](#quick-reference)

---

## 1. Architecture Overview

### System Purpose

Algo Trading System is a **high-speed, multi-tenant automated trading platform** that provides:

- **Mobile app** for retail traders to create and manage simple strategies
- **Backend execution engine** with Redis-based in-memory runtime
- **Broker integrations** (Zerodha, Dhan, Fyers, Angel One)
- **Real-time market monitoring** via WebSockets
- **Automated order execution** with mandatory stop-loss protection
- **Multi-tenant isolation** for secure strategy execution

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                     Mobile App (React Native)                   │
│                  (Expo-based Trading Interface)                 │
│                                                                 │
│   Strategy Creation ----> API Calls ----> Backend Services     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                             │
│                (Auth, Strategy, Broker Services)                │
│                                                                 │
│   ┌───────────────┐     ┌───────────────────────────────┐      │
│   │  Auth Service │ --> │  Strategy Validation          │      │
│   └───────────────┘     └───────────────────────────────┘      │
│           │                         │                           │
│           ▼                         ▼                           │
│   ┌───────────────┐     ┌───────────────────────────────┐      │
│   │ Broker Service│     │  Redis Runtime Store          │      │
│   └───────────────┘     └───────────────────────────────┘      │
│           │                         │                           │
│           ▼                         ▼                           │
│   ┌─────────────────────────────────────────────────────┐      │
│   │        Execution Engine (Order Placement)           │      │
│   └─────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                     PostgreSQL (Persistent Storage)
```

### Key Actors

- **Retail Traders** – End users creating and running automated strategies
- **Backend Developers** – Building FastAPI services and execution logic
- **Mobile Developers** – Developing React Native app interface
- **DevOps Engineers** – Managing AWS infrastructure and deployments
- **QA Testers** – Ensuring system reliability and safety
- **Broker Integrations** – Handling API connections to trading platforms

### Technology Stack

| Component         | Technology                      |
| ----------------- | ------------------------------- |
| Backend API       | FastAPI (Python 3.11+)          |
| Mobile App        | React Native / Expo             |
| In-Memory Runtime | Redis                           |
| Database          | PostgreSQL                      |
| Message Queue     | Celery + Redis                  |
| Authentication    | JWT                             |
| Encryption        | AES-256 for credentials         |
| Cloud Platform    | AWS (ECS/EKS, RDS, ElastiCache) |
| Monitoring        | CloudWatch                      |
| WebSocket Feeds   | Broker-specific APIs            |

---

## 2. Critical Policies

### ⚠️ Policy 1: Multi-Tenancy - Always Filter by user_id

**Every database query MUST filter by `user_id` for data isolation between users.**

```python
# ❌ FORBIDDEN - Security vulnerability (data leakage)
strategies = db.query(Strategy).all()

# ✅ REQUIRED - User isolation
strategies = db.query(Strategy).filter(
    Strategy.user_id == current_user.id
).all()
```

### ⚠️ Policy 2: Secure Broker Credential Storage

**All broker API keys, secrets, and tokens MUST be encrypted with AES-256 before storage.**

```python
# ❌ FORBIDDEN - Plain text storage
broker.api_key = request.api_key

# ✅ REQUIRED - Encrypted storage
encrypted_key = encrypt_aes256(request.api_key, master_key)
broker.encrypted_api_key = encrypted_key
db.commit()
```

### ⚠️ Policy 3: Mandatory Stop-Loss Protection

**Every strategy MUST have a stop-loss defined and enforced.**

```python
# ✅ REQUIRED - Stop-loss validation
if not strategy.stop_loss:
    raise HTTPException(status_code=400, detail="Stop-loss is mandatory")

# Execution engine must monitor and trigger stop-loss
if current_price <= strategy.stop_loss:
    place_sell_order(strategy)
```

### ⚠️ Policy 4: Failsafe Execution

**Execution engine MUST handle failures gracefully without losing orders.**

```python
# ✅ REQUIRED - Circuit breaker pattern
try:
    order_response = broker_api.place_order(order_data)
    log_success(order_response)
except Exception as e:
    log_failure(e)
    # Queue for retry or manual intervention
    queue_failed_order(order_data)
```

### ⚠️ Policy 5: Independent Strategy Execution

**Strategies MUST run in isolated contexts with no cross-contamination.**

```python
# ✅ REQUIRED - Redis key isolation
redis_key = f"strategy:{strategy.id}:state"
# Each strategy has its own Redis namespace
```

### ⚠️ Policy 6: Audit Fields on All Models

**Every model MUST have these fields:**

```python
class BaseModel:
    id: str                    # Primary key (e.g., sess_xxx, sum_xxx)
    created_at: datetime       # Auto-set on creation
    updated_at: datetime       # Auto-update on modification
    deleted_at: datetime       # Soft delete timestamp
    created_by: str           # User who created
    updated_by: str           # User who last updated
    deleted_by: str           # User who deleted
    status: str               # ACTIVE, DELETED, etc.
    tenant_id: str            # Multi-tenancy (REQUIRED)
```

### ⚠️ Policy 7: Use Functional Services Over Classes

**Algo Trading System Philosophy**: Functional composition by default.

```python
# ✅ PREFERRED - Functional service
def create_strategy_service(db: Session, redis_client: Redis):
    def validate_strategy(strategy_data: dict) -> List[str]:
        errors = []
        if not strategy_data.get('symbol'):
            errors.append("Symbol is required")
        if not strategy_data.get('stop_loss'):
            errors.append("Stop-loss is mandatory")
        return errors

    def execute_strategy(strategy_id: str, market_data: dict) -> dict:
        # Load strategy from Redis
        strategy = redis_client.get(f"strategy:{strategy_id}")
        # Execute logic
        return process_order(strategy, market_data)

    return {
        "validate_strategy": validate_strategy,
        "execute_strategy": execute_strategy,
    }

# Usage
strategy_service = create_strategy_service(db, redis_client)
result = strategy_service["execute_strategy"](strategy_id, market_data)
```

### ⚠️ Policy 6: Schema Changes Require Synchronization

**When modifying SQLAlchemy models, update all layers:**

1. **SQLAlchemy Model** (`models/*.py`)
2. **Pydantic Schema** (`schemas/*.py`)
3. **Alembic Migration** (`migrations/versions/`)
4. **Service Layer** (`services/*.py`)
5. **API Routes** (`api/v1/*.py`)

```bash
# After model changes:
alembic revision --autogenerate -m "add_new_field"
alembic upgrade head
```

### ⚠️ Policy 7: Never Store Private Keys in Code

```python
# ❌ FORBIDDEN
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----..."""

# ✅ REQUIRED - Load from environment/KMS
private_key = load_private_key_from_env("SIGNING_PRIVATE_KEY")
```

---

## 3. Project Structure

### Directory Layout

```
algo-trading-system/
├── backend/
│   ├── alembic.ini
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry point
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Authentication routes
│   │   │   ├── broker.py         # Broker integration routes
│   │   │   └── strategies.py     # Strategy management routes
│   │   ├── brokers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # Base broker class
│   │   │   ├── angel_one.py      # Angel One broker integration
│   │   │   ├── dhan.py           # Dhan broker integration
│   │   │   ├── fyers.py          # Fyers broker integration
│   │   │   └── zerodha.py        # Zerodha broker integration
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py         # Configuration settings
│   │   │   ├── database.py       # Database connection
│   │   │   └── security.py       # Security utilities
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py           # User model
│   │   │   ├── broker.py         # Broker credentials model
│   │   │   └── strategy.py       # Trading strategy model
│   │   ├── services/
│   │   │   └── __init__.py       # Service layer (functional)
│   │   ├── workers/
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py     # Celery configuration
│   │   │   └── tasks.py          # Background tasks
│   │   └── utils/
│   │       └── __init__.py
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_integration_strategies.py
│   ├── requirements.txt
│   └── pyproject.toml
├── docs/
│   ├── SRS.MD                   # Software Requirements Specification
│   ├── HLD.MD                   # High-Level Design
│   ├── LLD.MD                   # Low-Level Design
│   └── ...                      # Other documentation
├── scripts/
│   ├── dev_up.sh
│   ├── dev_down.sh
│   └── migrate_db.sh
└── docker-compose.yml
│       │   ├── designer/
│       │   │   └── page.tsx          # Workflow designer
│       │   ├── sources/
│       │   │   └── page.tsx          # Source manager
│       │   ├── settings/
│       │   │   └── page.tsx
│       │   └── api/
│       │       ├── workflows/
│       │       │   └── route.ts      # Proxy to backend
│       │       └── execute/
│       │           └── route.ts
│       ├── components/
│       │   ├── WorkflowCanvas.tsx
│       │   ├── NodePalette.tsx
│       │   ├── QueueEditor.tsx
│       │   ├── SourceEditor.tsx
│       │   ├── PropertiesPanel.tsx
│       │   └── JsonPreview.tsx
│       ├── lib/
│       │   ├── types.ts
│       │   ├── schema.ts
│       │   └── mappers.ts
│       ├── styles/
│       └── package.json
├── shared/
│   ├── examples/
│   │   ├── workflow_basic.json
│   │   └── workflow_extended.json
│   └── docs/
├── scripts/
│   ├── build_backend.sh
│   ├── start_backend.sh
│   ├── start_frontend.sh
│   └── deploy.sh
└── docs/
    ├── srs.md
    ├── hld.md
    ├── lld.md
    ├── API_Spec.md
    ├── BACKEND-SPEC.md
    ├── FRONTEND-SPEC.md
    └── WORKFLOW-SCHEMA.md
```

### File Naming Conventions

```
backend/app/api/auth.py          # API routes (snake_case)
backend/app/brokers/zerodha.py   # Broker integrations
backend/app/models/user.py       # SQLAlchemy models
backend/app/workers/tasks.py     # Background tasks
```

---

## 4. Code Patterns

### API Route Pattern

```python
# api/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Validate and create user
    hashed_password = hash_password(user_data.password)
    new_user = User(email=user_data.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}
```

### Service Pattern

```python
# services/strategy_service.py
from sqlalchemy.orm import Session
from redis import Redis
from app.models.strategy import Strategy

def create_strategy_service(db: Session, redis_client: Redis):
    def validate_strategy(strategy_data: dict) -> list[str]:
        errors = []
        if not strategy_data.get('symbol'):
            errors.append("Symbol is required")
        if not strategy_data.get('buy_time'):
            errors.append("Buy time is required")
        if not strategy_data.get('sell_time'):
            errors.append("Sell time is required")
        if not strategy_data.get('stop_loss'):
            errors.append("Stop-loss is mandatory")
        return errors

    def create_strategy(user_id: str, strategy_data: dict) -> Strategy:
        # Validate first
        errors = validate_strategy(strategy_data)
        if errors:
            raise ValueError(f"Validation errors: {errors}")

        # Create strategy
        strategy = Strategy(
            user_id=user_id,
            symbol=strategy_data['symbol'],
            buy_time=strategy_data['buy_time'],
            sell_time=strategy_data['sell_time'],
            stop_loss=strategy_data['stop_loss'],
            quantity=strategy_data['quantity']
        )
        db.add(strategy)
        db.commit()
        return strategy

    return {
        "validate_strategy": validate_strategy,
        "create_strategy": create_strategy,
    }
```

### Pydantic Schema Pattern

```python
# schemas/strategy.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import time

class StrategyCreate(BaseModel):
    symbol: str = Field(..., description="Trading symbol (e.g., RELIANCE)")
    buy_time: str = Field(..., description="Buy time in HH:MM:SS format")
    sell_time: str = Field(..., description="Sell time in HH:MM:SS format")
    stop_loss: float = Field(..., gt=0, description="Stop-loss price (mandatory)")
    quantity: int = Field(..., gt=0, description="Quantity to trade")

class StrategyResponse(BaseModel):
    id: str
    user_id: str
    symbol: str
    buy_time: str
    sell_time: str
    stop_loss: float
    quantity: int
    status: str  # ACTIVE, STOPPED, RUNNING
    created_at: str
    updated_at: str

class BrokerCredentials(BaseModel):
    api_key: str
    secret_key: str
    access_token: Optional[str] = None
```

### Execution State Pattern

```python
# workers/execution_state.py
from typing import TypedDict, Any, Optional

class ExecutionState(TypedDict, total=False):
    strategy_id: str
    symbol: str
    current_price: float
    buy_time: str
    sell_time: str
    stop_loss: float
    quantity: int
    status: str  # WAITING, BOUGHT, SOLD, STOPPED
    buy_order_id: Optional[str]
    sell_order_id: Optional[str]
    last_action: str
    market_data: dict
    errors: list[str]
```

---

## 5. Data Models

### Core Models

```python
# models/user.py
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String, default="ACTIVE")
```

```python
# models/strategy.py
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False)
    buy_time = Column(String, nullable=False)  # HH:MM:SS
    sell_time = Column(String, nullable=False)  # HH:MM:SS
    stop_loss = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String, default="ACTIVE")  # ACTIVE, RUNNING, STOPPED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

```python
# models/broker.py
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class BrokerCredentials(Base):
    __tablename__ = "broker_credentials"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    broker_name = Column(String, nullable=False)  # zerodha, angel_one, etc.
    encrypted_api_key = Column(Text, nullable=False)
    encrypted_secret_key = Column(Text, nullable=False)
    encrypted_access_token = Column(Text)
    status = Column(String, default="ACTIVE")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

    image_result: Any
    db_result: Any
    final_output: Any
    tokens_used: int
    cost: float
    metadata: dict

````

---

## 6. Security & Compliance

### Authentication

**API Key Authentication (Server-to-Server):**

```python
# core/security.py
from fastapi import Header, HTTPException

async def get_api_key(x_api_key: str = Header(...)):
    """Validate API key for workflow operations."""
    if not validate_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
````

### Environment Variables

```python
# Load sensitive configuration from environment
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
AES_MASTER_KEY = os.getenv("AES_MASTER_KEY")
```

### Error Handling

```python
# Common HTTP error responses
400 Bad Request   # Invalid strategy data
401 Unauthorized  # Invalid JWT token
403 Forbidden     # User not authorized for strategy
404 Not Found     # Strategy or broker not found
422 Unprocessable # Validation errors
500 Internal      # Unexpected errors
```

---

## 7. Quick Reference

### Most Common Operations

| Task                    | Code                                              |
| ----------------------- | ------------------------------------------------- |
| **Validate strategy**   | `errors = validate_strategy(data)`                |
| **Create strategy**     | `strategy = create_strategy(user_id, data)`       |
| **Execute order**       | `result = place_order(broker, order_data)`        |
| **Check stop-loss**     | `if price <= strategy.stop_loss: sell()`          |
| **Encrypt credentials** | `encrypted = encrypt_aes256(api_key, master_key)` |

### ID Prefixes

| Entity   | Prefix   | Example        |
| -------- | -------- | -------------- |
| User     | `usr_`   | `usr_abc123`   |
| Strategy | `str_`   | `str_xyz789`   |
| Broker   | `brk_`   | `brk_def456`   |
| Order    | `ord_`   | `ord_ghi012`   |
| Queue    | `queue_` | `queue_def456` |
| Source   | `src_`   | `src_ghi012`   |

### Environment Variables

```bash
# Database (optional)
DATABASE_URL="postgresql://user:pass@localhost:5432/algo_trading"

# AI Services
OPENAI_API_KEY="sk-..."
OPENAI_MODEL="gpt-4"

# Redis (for rate limiting)
REDIS_URL="redis://localhost:6379"

# Backend
ALGO_TRADING_CORE_URL="http://localhost:8000"

# Frontend
NEXT_PUBLIC_CORE_URL="http://localhost:8000"
```

### Docker Commands

```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f backend

# Run tests
docker-compose exec backend pytest

# Start frontend (if applicable)
# cd mobile && expo start
```

---

## Summary

**Key Takeaways**:

1. ✅ High-speed multi-tenant trading automation
2. ✅ Redis-based in-memory execution runtime
3. ✅ Mandatory stop-loss protection for safety
4. ✅ AES-256 encrypted broker credentials
5. ✅ Functional services over classes
6. ✅ JWT authentication with user isolation
7. ✅ React Native mobile app interface

**Questions?** See existing code in `/backend/app`, `/docs`, or `/tests` for real examples.

---

**Last Updated**: December 7, 2025  
**Maintained by**: Algo Trading System Engineering Team
