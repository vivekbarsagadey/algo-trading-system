````chatagent
# Algo Trading System Agent Context

> **For AI Agents**: This file contains Algo Trading System-specific context that all agents should be aware of. Modern LLMs already know Python, FastAPI, React Native, Redis, and PostgreSQL fundamentals - this document focuses ONLY on what makes Algo Trading System unique.

## Project Identity

**Algo Trading System**: High-Speed, Multi-Tenant Automated Trading Platform
**Stack**: FastAPI (Python 3.11+) • React Native/Expo • Redis • PostgreSQL • AWS
**Primary Instruction File**: `.github/instructions/accubrief-rules.instructions.md`

---

## Critical Algo Trading System-Specific Patterns

### 1. Strategy-First Trading Automation

**All trading strategies are defined with mandatory safety parameters:**

```json
{
  "symbol": "RELIANCE",
  "buy_time": "09:15:00",
  "sell_time": "15:30:00",
  "stop_loss": 2500.0,
  "quantity": 10
}
````

**Hierarchy:**

```
Strategy
  ├── Symbol (trading instrument)
  ├── Buy/Sell Times (execution schedule)
  ├── Stop Loss (mandatory safety)
  └── Quantity (trade size)
```

### 2. Multi-Tenant Isolation

**Every operation must filter by user_id:**

```python
# Always filter by user_id for security
strategies = db.query(Strategy).filter(
    Strategy.user_id == current_user.id
).all()
```

### 3. Redis Runtime Execution

**Strategies are executed with Redis-based state management:**

```python
# workers/execution_engine.py
def execute_strategy(strategy_id: str, market_data: dict) -> dict:
    # Load strategy from Redis
    strategy = redis_client.get(f"strategy:{strategy_id}")

    # Check execution conditions
    if should_buy(strategy, market_data):
        return place_buy_order(strategy)
    elif should_sell(strategy, market_data):
        return place_sell_order(strategy)

    return {"status": "waiting"}
```

### 4. Execution State Pattern

**State maintained for each running strategy:**

```python
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

### 5. Broker Integration Pattern

**Standardized broker API interface:**

```python
# brokers/base.py
class BaseBroker:
    def authenticate(self, credentials: dict) -> bool:
        pass

    def get_market_data(self, symbol: str) -> dict:
        pass

    def place_order(self, order_data: dict) -> dict:
        pass

    def get_order_status(self, order_id: str) -> dict:
        pass
```

### 6. Credential Encryption

**AES-256 encryption for all broker credentials:**

```python
# core/security.py
def encrypt_aes256(plain_text: str, master_key: str) -> str:
    # AES-256 encryption implementation
    pass

def decrypt_aes256(encrypted_text: str, master_key: str) -> str:
    # AES-256 decryption implementation
    pass
```

---

## System Architecture

### Main Components

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

│ │ Queue Manager │ │ Node Registry (LLM, DB, etc.)│ │
│ └───────────────┘ └───────────────────────────────┘ │
│ │ │ │
│ ▼ ▼ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Executor (LangGraph runtime.invoke) │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
│
▼
Final State JSON Output

```

### Directory Structure

```

backend/app/
├── api/ # FastAPI routes
│ ├── auth.py # Authentication endpoints
│ ├── broker.py # Broker management
│ └── strategies.py # Strategy CRUD
├── brokers/ # Broker integrations
│ ├── base.py # Base broker class
│ ├── zerodha.py # Zerodha API
│ ├── dhan.py # Dhan API
│ └── fyers.py # Fyers API
├── core/ # Core utilities
│ ├── config.py # Configuration
│ ├── database.py # DB connection
│ └── security.py # Encryption, JWT
├── models/ # SQLAlchemy models
│ ├── user.py # User model
│ ├── strategy.py # Strategy model
│ └── broker.py # Broker credentials
├── services/ # Functional services
├── workers/ # Background tasks
│ ├── celery_app.py # Celery config
│ └── tasks.py # Async tasks
└── utils/ # Helper functions

```

---

## Key Workflows

### Strategy Creation Flow
1. User creates strategy in mobile app
2. Frontend validates required fields (symbol, times, stop_loss)
3. POST to `/strategies/` with strategy data
4. Backend validates and saves to DB
5. Return strategy ID

### Strategy Execution Flow
1. User starts strategy via mobile app
2. POST to `/strategies/{id}/start`
3. Backend loads strategy to Redis runtime
4. Scheduler monitors time + market data
5. Execution engine places orders at specified times
6. Stop-loss monitoring active during execution

### Broker Integration Flow
1. User adds broker credentials
2. POST to `/brokers/` with encrypted credentials
3. Backend validates credentials via test API call
4. Store encrypted credentials in DB
5. Use for order placement

---

## ID Prefixes

| Entity | Prefix | Example |
|--------|--------|---------|
| User | `usr_` | `usr_abc123` |
| Strategy | `str_` | `str_xyz789` |
| Broker | `brk_` | `brk_def456` |
| Order | `ord_` | `ord_ghi012` |

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/login` | POST | User authentication |
| `/auth/register` | POST | User registration |
| `/strategies/` | GET/POST | List/create strategies |
| `/strategies/{id}` | GET/PUT/DELETE | Strategy CRUD |
| `/strategies/{id}/start` | POST | Start strategy execution |
| `/strategies/{id}/stop` | POST | Stop strategy execution |
| `/brokers/` | GET/POST | List/add broker credentials |
| `/brokers/{id}/validate` | POST | Validate broker credentials |

---

## Reference Documentation

- `.github/instructions/algo-trading-system-rules.instructions.md` - Project rules & patterns
- `/docs/srs.md` - Software Requirements Specification
- `/docs/hld.md` - High-Level Design
- `/docs/lld.md` - Low-Level Design
- `/docs/API_Spec.md` - API Specification
- `/docs/BACKEND-SPEC.md` - Backend Specification
- `/docs/FRONTEND-SPEC.md` - Frontend Specification
- `/docs/WORKFLOW-SCHEMA.md` - JSON Schema documentation
```
