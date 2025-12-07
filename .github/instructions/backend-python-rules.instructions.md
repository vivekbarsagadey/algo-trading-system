---
applyTo: "backend/**"
agent: expert-python
---

# Backend Python Rules - Algo Trading System

> **Expert Python Agent**: This guide contains backend-specific rules for FastAPI, SQLAlchemy, Redis, Celery, and trading execution engine.

**Last Updated**: December 7, 2025  
**Stack**: FastAPI • Python 3.11+ • PostgreSQL • Redis • Celery • AWS

---

## Table of Contents

1. [Critical Backend Policies](#critical-backend-policies)
2. [Project Structure](#project-structure)
3. [Code Standards](#code-standards)
4. [Database Patterns](#database-patterns)
5. [API Design](#api-design)
6. [Execution Engine](#execution-engine)
7. [Testing Standards](#testing-standards)

---

## 1. Critical Backend Policies

### ⚠️ Policy 1: Multi-Tenancy - Always Filter by user_id

**EVERY database query MUST filter by `user_id` for data isolation.**

```python
# ❌ FORBIDDEN - Security vulnerability (data leakage)
strategies = db.query(Strategy).all()

# ✅ REQUIRED - User isolation
strategies = db.query(Strategy).filter(
    Strategy.user_id == current_user.id
).all()
```

### ⚠️ Policy 2: Secure Broker Credentials

**ALL broker API keys MUST be encrypted with AES-256 before storage.**

```python
# ❌ FORBIDDEN - Plain text storage
broker.api_key = request.api_key

# ✅ REQUIRED - Encrypted storage
from app.core.security import encrypt_aes256, decrypt_aes256

encrypted_key = encrypt_aes256(request.api_key, master_key)
broker.encrypted_api_key = encrypted_key
db.commit()

# When using
api_key = decrypt_aes256(broker.encrypted_api_key, master_key)
```

### ⚠️ Policy 3: Mandatory Stop-Loss

**Every strategy MUST have stop-loss defined and enforced.**

```python
# ✅ REQUIRED - Validation in API layer
from pydantic import validator

class StrategyCreate(BaseModel):
    stop_loss: float = Field(..., gt=0, description="Mandatory stop-loss")
    
    @validator('stop_loss')
    def validate_stop_loss(cls, v):
        if v is None or v <= 0:
            raise ValueError("Stop-loss is mandatory and must be positive")
        return v
```

### ⚠️ Policy 4: Functional Services Over Classes

**Use functional composition for services.**

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

    def create_strategy(user_id: str, strategy_data: dict) -> Strategy:
        errors = validate_strategy(strategy_data)
        if errors:
            raise ValueError(f"Validation errors: {errors}")
        
        strategy = Strategy(user_id=user_id, **strategy_data)
        db.add(strategy)
        db.commit()
        return strategy

    return {
        "validate_strategy": validate_strategy,
        "create_strategy": create_strategy,
    }
```

### ⚠️ Policy 5: Schema Synchronization

**When modifying models, update ALL layers:**

1. **SQLAlchemy Model** (`models/*.py`)
2. **Pydantic Schema** (`schemas/*.py`) - if exists
3. **Alembic Migration** (`alembic/versions/`)
4. **Service Layer** (`services/*.py`)
5. **API Routes** (`api/*.py`)

```bash
# After model changes:
alembic revision --autogenerate -m "add_new_field"
alembic upgrade head
```

---

## 2. Project Structure

### Backend Directory Layout

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── broker.py            # Broker integration endpoints
│   │   └── strategies.py        # Strategy CRUD endpoints
│   ├── brokers/
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract base broker class
│   │   ├── zerodha.py           # Zerodha integration
│   │   ├── angel_one.py         # Angel One integration
│   │   ├── dhan.py              # Dhan integration
│   │   └── fyers.py             # Fyers integration
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Settings and configuration
│   │   ├── database.py          # Database connection
│   │   └── security.py          # JWT, encryption, hashing
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User SQLAlchemy model
│   │   ├── broker.py            # Broker credentials model
│   │   └── strategy.py          # Strategy model
│   ├── services/
│   │   └── __init__.py          # Business logic (functional)
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── celery_app.py        # Celery configuration
│   │   └── tasks.py             # Background tasks
│   └── utils/
│       └── __init__.py
├── tests/
│   ├── conftest.py              # Pytest configuration
│   ├── test_api/
│   ├── test_services/
│   └── test_integration_strategies.py
├── alembic/
│   ├── env.py
│   └── versions/
├── alembic.ini
├── requirements.txt
├── pyproject.toml
├── pytest.ini
└── Dockerfile
```

---

## 3. Code Standards

### Python Version & Type Hints

```python
# Python 3.11+ features
from typing import Optional, List, Dict, Any
from datetime import datetime, time

# Use modern type hints
def create_strategy(
    user_id: str,
    symbol: str,
    buy_time: time,
    stop_loss: float
) -> Strategy:
    """Create a new trading strategy."""
    pass

# Optional parameters
def get_strategies(
    db: Session,
    user_id: str,
    status: Optional[str] = None,
    limit: int = 100
) -> List[Strategy]:
    """Retrieve user strategies with optional filters."""
    query = db.query(Strategy).filter(Strategy.user_id == user_id)
    if status:
        query = query.filter(Strategy.status == status)
    return query.limit(limit).all()
```

### Naming Conventions

```python
# Files: snake_case
# app/api/auth.py
# app/models/user.py
# app/services/strategy_service.py

# Classes: PascalCase
class User(Base):
    pass

class StrategyService:
    pass

# Functions/Variables: snake_case
def validate_strategy(strategy_data: dict) -> list[str]:
    pass

current_user = get_current_user()
strategy_list = get_strategies()

# Constants: UPPER_SNAKE_CASE
MAX_STRATEGIES_PER_USER = 10
DEFAULT_TIMEOUT_SECONDS = 30
```

### Import Organization

```python
# 1. Standard library imports
import os
from datetime import datetime, timedelta
from typing import Optional, List

# 2. Third-party imports
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from redis import Redis

# 3. Local application imports
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.strategy import Strategy
```

---

## 4. Database Patterns

### SQLAlchemy Model Pattern

```python
# models/strategy.py
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Strategy(Base):
    __tablename__ = "strategies"

    # Primary key
    id = Column(String, primary_key=True, index=True)
    
    # Multi-tenancy (REQUIRED)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Business fields
    symbol = Column(String, nullable=False)
    buy_time = Column(String, nullable=False)  # HH:MM:SS format
    sell_time = Column(String, nullable=False)  # HH:MM:SS format
    stop_loss = Column(Float, nullable=False)  # Mandatory
    quantity = Column(Integer, nullable=False)
    status = Column(String, default="ACTIVE")  # ACTIVE, RUNNING, STOPPED
    
    # Audit fields (REQUIRED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String)
    updated_by = Column(String)
```

### Database Query Patterns

```python
# ✅ CORRECT - User isolation with pagination
def get_user_strategies(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[Strategy]:
    """Get strategies for specific user with pagination."""
    return db.query(Strategy)\
        .filter(Strategy.user_id == user_id)\
        .offset(skip)\
        .limit(limit)\
        .all()

# ✅ CORRECT - Filtered update
def update_strategy_status(
    db: Session,
    strategy_id: str,
    user_id: str,
    new_status: str
) -> Optional[Strategy]:
    """Update strategy status with user isolation."""
    strategy = db.query(Strategy)\
        .filter(
            Strategy.id == strategy_id,
            Strategy.user_id == user_id  # REQUIRED
        )\
        .first()
    
    if strategy:
        strategy.status = new_status
        strategy.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(strategy)
    
    return strategy
```

### Alembic Migration Pattern

```python
# alembic/versions/xxxx_add_broker_field.py
"""add broker field to strategies

Revision ID: xxxx
Create Date: 2025-12-07
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('strategies', 
        sa.Column('broker_name', sa.String(), nullable=True)
    )
    # Backfill existing data
    op.execute("UPDATE strategies SET broker_name = 'zerodha' WHERE broker_name IS NULL")
    # Make non-nullable after backfill
    op.alter_column('strategies', 'broker_name', nullable=False)

def downgrade():
    op.drop_column('strategies', 'broker_name')
```

---

## 5. API Design

### FastAPI Route Pattern

```python
# api/strategies.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.strategy import Strategy
from app.models.user import User

router = APIRouter(prefix="/strategies", tags=["strategies"])

@router.get("/", response_model=List[StrategyResponse])
async def list_strategies(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all strategies for current user."""
    strategies = db.query(Strategy)\
        .filter(Strategy.user_id == current_user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return strategies

@router.post("/", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    strategy_data: StrategyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new trading strategy."""
    # Validate mandatory fields
    if not strategy_data.stop_loss:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stop-loss is mandatory"
        )
    
    # Create strategy
    strategy = Strategy(
        user_id=current_user.id,
        symbol=strategy_data.symbol,
        buy_time=strategy_data.buy_time,
        sell_time=strategy_data.sell_time,
        stop_loss=strategy_data.stop_loss,
        quantity=strategy_data.quantity,
        created_by=current_user.id
    )
    
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    
    return strategy

@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a strategy (soft delete)."""
    strategy = db.query(Strategy)\
        .filter(
            Strategy.id == strategy_id,
            Strategy.user_id == current_user.id  # User isolation
        )\
        .first()
    
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    # Soft delete
    strategy.status = "DELETED"
    strategy.deleted_at = datetime.utcnow()
    strategy.deleted_by = current_user.id
    db.commit()
```

### Error Handling Pattern

```python
# core/exceptions.py
from fastapi import HTTPException, status

class StrategyNotFoundError(HTTPException):
    def __init__(self, strategy_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy {strategy_id} not found"
        )

class UnauthorizedAccessError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )

class StopLossRequiredError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stop-loss is mandatory for all strategies"
        )

# Usage in routes
@router.get("/{strategy_id}")
async def get_strategy(
    strategy_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    strategy = db.query(Strategy)\
        .filter(
            Strategy.id == strategy_id,
            Strategy.user_id == current_user.id
        )\
        .first()
    
    if not strategy:
        raise StrategyNotFoundError(strategy_id)
    
    return strategy
```

---

## 6. Execution Engine

### Broker Integration Pattern

```python
# brokers/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class OrderRequest:
    symbol: str
    quantity: int
    order_type: str  # MARKET, LIMIT
    side: str  # BUY, SELL
    price: Optional[float] = None

@dataclass
class OrderResponse:
    order_id: str
    status: str
    message: str
    executed_price: Optional[float] = None

class BaseBroker(ABC):
    """Abstract base class for broker integrations."""
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with broker API."""
        pass
    
    @abstractmethod
    def place_order(self, order: OrderRequest) -> OrderResponse:
        """Place a buy/sell order."""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions."""
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get status of an order."""
        pass
```

### Zerodha Broker Implementation

```python
# brokers/zerodha.py
from kiteconnect import KiteConnect
from app.brokers.base import BaseBroker, OrderRequest, OrderResponse

class ZerodhaBroker(BaseBroker):
    def __init__(self, api_key: str, access_token: str):
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)
    
    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Zerodha."""
        try:
            # Verify access token
            profile = self.kite.profile()
            return profile is not None
        except Exception as e:
            return False
    
    def place_order(self, order: OrderRequest) -> OrderResponse:
        """Place order via Zerodha Kite Connect."""
        try:
            order_id = self.kite.place_order(
                variety=self.kite.VARIETY_REGULAR,
                exchange=self.kite.EXCHANGE_NSE,
                tradingsymbol=order.symbol,
                transaction_type=self.kite.TRANSACTION_TYPE_BUY if order.side == "BUY" else self.kite.TRANSACTION_TYPE_SELL,
                quantity=order.quantity,
                product=self.kite.PRODUCT_MIS,  # Intraday
                order_type=self.kite.ORDER_TYPE_MARKET if order.order_type == "MARKET" else self.kite.ORDER_TYPE_LIMIT,
                price=order.price if order.order_type == "LIMIT" else None
            )
            
            return OrderResponse(
                order_id=str(order_id),
                status="SUCCESS",
                message="Order placed successfully"
            )
        except Exception as e:
            return OrderResponse(
                order_id="",
                status="FAILED",
                message=str(e)
            )
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions."""
        return self.kite.positions()
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get order status."""
        orders = self.kite.orders()
        for order in orders:
            if order['order_id'] == order_id:
                return order
        return {}
```

### Execution Engine Pattern

```python
# workers/tasks.py
from celery import Celery
from redis import Redis
from app.core.database import SessionLocal
from app.models.strategy import Strategy
from app.brokers.zerodha import ZerodhaBroker

celery_app = Celery('algo_trading', broker='redis://localhost:6379/0')

@celery_app.task
def execute_strategy(strategy_id: str):
    """Execute a trading strategy."""
    db = SessionLocal()
    redis_client = Redis.from_url('redis://localhost:6379')
    
    try:
        # Load strategy from database
        strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            return {"status": "error", "message": "Strategy not found"}
        
        # Get broker credentials (decrypt)
        broker_creds = get_broker_credentials(db, strategy.user_id)
        
        # Initialize broker
        broker = ZerodhaBroker(
            api_key=broker_creds.api_key,
            access_token=broker_creds.access_token
        )
        
        # Check if stop-loss triggered
        current_price = get_current_price(strategy.symbol)
        if current_price <= strategy.stop_loss:
            # Place sell order
            order = OrderRequest(
                symbol=strategy.symbol,
                quantity=strategy.quantity,
                order_type="MARKET",
                side="SELL"
            )
            response = broker.place_order(order)
            
            # Update strategy status
            strategy.status = "STOPPED"
            db.commit()
            
            return {
                "status": "stop_loss_triggered",
                "order_id": response.order_id
            }
        
        # Normal execution logic
        # ...
        
    except Exception as e:
        # Log error
        redis_client.lpush(f"errors:{strategy_id}", str(e))
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
```

---

## 7. Testing Standards

### Pytest Configuration

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.main import app

@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def test_client():
    """Create a test client."""
    from fastapi.testclient import TestClient
    return TestClient(app)

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    from app.models.user import User
    user = User(
        id="test_user_123",
        email="test@example.com",
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    return user
```

### Unit Test Pattern

```python
# tests/test_services/test_strategy_service.py
import pytest
from app.services.strategy_service import create_strategy_service

def test_validate_strategy_missing_symbol(db_session):
    """Test strategy validation with missing symbol."""
    service = create_strategy_service(db_session, None)
    
    strategy_data = {
        "buy_time": "09:15:00",
        "sell_time": "15:30:00",
        "stop_loss": 100.0,
        "quantity": 10
    }
    
    errors = service["validate_strategy"](strategy_data)
    assert "Symbol is required" in errors

def test_validate_strategy_missing_stop_loss(db_session):
    """Test strategy validation with missing stop-loss."""
    service = create_strategy_service(db_session, None)
    
    strategy_data = {
        "symbol": "RELIANCE",
        "buy_time": "09:15:00",
        "sell_time": "15:30:00",
        "quantity": 10
    }
    
    errors = service["validate_strategy"](strategy_data)
    assert "Stop-loss is mandatory" in errors
```

### Integration Test Pattern

```python
# tests/test_integration_strategies.py
def test_create_strategy_success(test_client, test_user):
    """Test successful strategy creation."""
    # Get auth token
    login_response = test_client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    # Create strategy
    response = test_client.post(
        "/strategies/",
        json={
            "symbol": "RELIANCE",
            "buy_time": "09:15:00",
            "sell_time": "15:30:00",
            "stop_loss": 2500.0,
            "quantity": 10
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["symbol"] == "RELIANCE"
    assert data["stop_loss"] == 2500.0

def test_create_strategy_without_stop_loss_fails(test_client, test_user):
    """Test strategy creation fails without stop-loss."""
    token = get_auth_token(test_client)
    
    response = test_client.post(
        "/strategies/",
        json={
            "symbol": "RELIANCE",
            "buy_time": "09:15:00",
            "sell_time": "15:30:00",
            "quantity": 10
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400
    assert "stop-loss" in response.json()["detail"].lower()
```

---

## Quick Reference

### Common Backend Operations

| Task | Code |
|------|------|
| **Create session** | `db = SessionLocal()` |
| **Query with filter** | `db.query(Model).filter(Model.user_id == user_id).all()` |
| **Encrypt credential** | `encrypt_aes256(value, master_key)` |
| **Hash password** | `pwd_context.hash(password)` |
| **Create JWT token** | `create_access_token(data={"sub": user_id})` |
| **Redis set** | `redis_client.set(key, value)` |
| **Celery task** | `@celery_app.task` |

### Environment Variables

```bash
DATABASE_URL="postgresql://user:pass@localhost:5432/algo_trading"
REDIS_URL="redis://localhost:6379/0"
JWT_SECRET_KEY="your-secret-key-here"
AES_MASTER_KEY="your-encryption-key-here"
CELERY_BROKER_URL="redis://localhost:6379/0"
```

### Docker Commands

```bash
# Start backend
docker-compose up -d backend

# View logs
docker-compose logs -f backend

# Run tests
docker-compose exec backend pytest

# Apply migrations
docker-compose exec backend alembic upgrade head
```

---

**Last Updated**: December 7, 2025  
**Maintained by**: Backend Engineering Team  
**Agent**: expert-python
