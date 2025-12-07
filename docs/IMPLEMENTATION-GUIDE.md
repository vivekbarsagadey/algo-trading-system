# 📘 Implementation Guide

## Algo Trading System

**Version:** 1.0  
**Last Updated:** December 2024  
**Status:** Active  
**Audience:** Development Team

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Development Environment Setup](#2-development-environment-setup)
3. [Backend Implementation](#3-backend-implementation)
4. [Database Implementation](#4-database-implementation)
5. [Redis Implementation](#5-redis-implementation)
6. [Broker Integration](#6-broker-integration)
7. [Execution Engine](#7-execution-engine)
8. [Mobile App Implementation](#8-mobile-app-implementation)
9. [Testing Strategy](#9-testing-strategy)
10. [Deployment Guide](#10-deployment-guide)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Introduction

### 1.1 Purpose

This guide provides step-by-step instructions for implementing the Algo Trading System. It covers development environment setup, code organization, key implementation patterns, and deployment procedures.

### 1.2 Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.11+ | Backend development |
| Node.js | 20+ | Mobile app development (LTS) |
| Docker | 24+ | Containerization |
| PostgreSQL | 15+ | Database |
| Redis | 7+ | In-memory runtime |
| Git | 2.40+ | Version control |

### 1.3 Technology Stack Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                      TECHNOLOGY STACK                            │
├─────────────────────────────────────────────────────────────────┤
│  Frontend:  React Native + Expo                                  │
│  Backend:   FastAPI (Python 3.11+)                               │
│  Database:  PostgreSQL 15                                        │
│  Cache:     Redis 7                                              │
│  Queue:     Celery + Redis                                       │
│  Auth:      JWT (PyJWT)                                          │
│  Crypto:    AES-256 (cryptography)                               │
│  Cloud:     AWS (ECS, RDS, ElastiCache)                          │
│  CI/CD:     GitHub Actions                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Development Environment Setup

### 2.1 Clone Repository

```bash
git clone https://github.com/vivekbarsagadey/algo-trading-system.git
cd algo-trading-system
```

### 2.2 Backend Setup

#### 2.2.1 Create Python Virtual Environment

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
.\venv\Scripts\activate   # Windows
```

#### 2.2.2 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -r dev-requirements.txt  # For development
```

#### 2.2.3 Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/algo_trading

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Encryption (AES-256)
AES_MASTER_KEY=your-32-byte-aes-key-for-broker-credentials

# Environment
ENVIRONMENT=development
DEBUG=true
```

#### 2.2.4 Start Development Services

Using Docker Compose:

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Or use the dev script
./scripts/dev_up.sh
```

#### 2.2.5 Run Database Migrations

```bash
cd backend
alembic upgrade head
```

#### 2.2.6 Start Backend Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use make command
make run-dev
```

### 2.3 Verify Setup

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "timestamp": "2024-12-07T10:00:00Z"}
```

---

## 3. Backend Implementation

### 3.1 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── broker.py           # Broker integration endpoints
│   │   └── strategies.py       # Strategy management endpoints
│   ├── brokers/                # Broker API integrations
│   │   ├── __init__.py
│   │   ├── base.py             # Abstract base class
│   │   ├── zerodha.py          # Zerodha Kite implementation
│   │   ├── dhan.py             # Dhan implementation
│   │   ├── angel_one.py        # Angel One implementation
│   │   └── fyers.py            # Fyers implementation
│   ├── core/                   # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration management
│   │   ├── database.py         # Database connection
│   │   └── security.py         # JWT & encryption utilities
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── broker.py
│   │   └── strategy.py
│   ├── services/               # Business logic services
│   │   └── __init__.py
│   └── workers/                # Background workers
│       ├── __init__.py
│       ├── celery_app.py
│       └── tasks.py
├── alembic/                    # Database migrations
├── tests/                      # Test suite
└── scripts/                    # Utility scripts
```

### 3.2 FastAPI Application Setup

#### `app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, broker, strategies

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Algo Trading System",
    description="High-Speed Automated Trading Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(broker.router, prefix="/broker", tags=["Broker"])
app.include_router(strategies.router, prefix="/strategy", tags=["Strategy"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
```

### 3.3 Configuration Management

#### `app/core/config.py`

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # Encryption
    aes_master_key: str
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

### 3.4 Authentication Implementation

#### `app/api/auth.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.models.user import User

router = APIRouter()

# Request/Response Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Endpoints
@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate token
    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token)

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token)
```

### 3.5 Security Utilities

#### `app/core/security.py`

```python
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT Token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

# AES-256 Encryption for Broker Credentials
def get_fernet_key() -> bytes:
    """Derive a Fernet key from the master key."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"algo_trading_salt",  # Use proper salt in production
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(settings.aes_master_key.encode()))
    return key

def encrypt_credential(plaintext: str) -> str:
    """Encrypt broker credentials using AES-256."""
    f = Fernet(get_fernet_key())
    return f.encrypt(plaintext.encode()).decode()

def decrypt_credential(ciphertext: str) -> str:
    """Decrypt broker credentials."""
    f = Fernet(get_fernet_key())
    return f.decrypt(ciphertext.encode()).decode()
```

### 3.6 Strategy Management

#### `app/api/strategies.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
import redis

from app.core.database import get_db
from app.core.config import settings
from app.models.strategy import Strategy
from app.api.auth import get_current_user

router = APIRouter()

# Redis client
redis_client = redis.from_url(settings.redis_url)

# Request/Response Models
class StrategyCreate(BaseModel):
    symbol: str = Field(..., description="Stock symbol (e.g., RELIANCE)")
    buy_time: str = Field(..., description="Buy time in HH:MM:SS format")
    sell_time: str = Field(..., description="Sell time in HH:MM:SS format")
    stop_loss: float = Field(..., gt=0, description="Stop-loss price (mandatory)")
    quantity: int = Field(..., gt=0, description="Quantity to trade")

class StrategyResponse(BaseModel):
    id: str
    symbol: str
    buy_time: str
    sell_time: str
    stop_loss: float
    quantity: int
    status: str

class StrategyStatus(BaseModel):
    status: str
    position: str
    last_action: Optional[str]
    last_price: Optional[float]

# Endpoints
@router.post("/create", response_model=StrategyResponse)
async def create_strategy(
    strategy_data: StrategyCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate stop-loss (mandatory)
    if not strategy_data.stop_loss:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stop-loss is mandatory for all strategies"
        )
    
    # Create strategy
    strategy = Strategy(
        user_id=current_user.id,
        symbol=strategy_data.symbol.upper(),
        buy_time=strategy_data.buy_time,
        sell_time=strategy_data.sell_time,
        stop_loss=strategy_data.stop_loss,
        quantity=strategy_data.quantity,
        status="created"
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    
    return StrategyResponse(
        id=str(strategy.id),
        symbol=strategy.symbol,
        buy_time=strategy.buy_time,
        sell_time=strategy.sell_time,
        stop_loss=strategy.stop_loss,
        quantity=strategy.quantity,
        status=strategy.status
    )

@router.post("/start/{strategy_id}")
async def start_strategy(
    strategy_id: UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch strategy with user validation
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id  # Multi-tenant isolation
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if strategy.status == "running":
        raise HTTPException(status_code=400, detail="Strategy already running")
    
    # Load into Redis
    strategy_key = f"strategy:{strategy_id}"
    runtime_key = f"runtime:{strategy_id}"
    
    redis_client.hset(strategy_key, mapping={
        "symbol": strategy.symbol,
        "buy_time": strategy.buy_time,
        "sell_time": strategy.sell_time,
        "stop_loss": str(strategy.stop_loss),
        "quantity": str(strategy.quantity),
        "user_id": str(strategy.user_id)
    })
    
    redis_client.hset(runtime_key, mapping={
        "position": "NONE",
        "last_action": "",
        "last_price": "0"
    })
    
    # Update database status
    strategy.status = "running"
    db.commit()
    
    # Register with scheduler (trigger Celery task)
    # schedule_strategy_jobs.delay(str(strategy_id))
    
    return {"message": "Strategy started", "strategy_id": str(strategy_id)}

@router.post("/stop/{strategy_id}")
async def stop_strategy(
    strategy_id: UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Remove from Redis
    redis_client.delete(f"strategy:{strategy_id}")
    redis_client.delete(f"runtime:{strategy_id}")
    redis_client.delete(f"lock:{strategy_id}")
    
    # Update database
    strategy.status = "stopped"
    db.commit()
    
    return {"message": "Strategy stopped", "strategy_id": str(strategy_id)}

@router.get("/status/{strategy_id}", response_model=StrategyStatus)
async def get_strategy_status(
    strategy_id: UUID,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify ownership
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Get runtime state from Redis
    runtime_key = f"runtime:{strategy_id}"
    runtime_data = redis_client.hgetall(runtime_key)
    
    if not runtime_data:
        return StrategyStatus(
            status=strategy.status,
            position="NONE",
            last_action=None,
            last_price=None
        )
    
    return StrategyStatus(
        status=strategy.status,
        position=runtime_data.get(b"position", b"NONE").decode(),
        last_action=runtime_data.get(b"last_action", b"").decode() or None,
        last_price=float(runtime_data.get(b"last_price", b"0").decode()) or None
    )
```

---

## 4. Database Implementation

### 4.1 SQLAlchemy Models

#### `app/models/user.py`

```python
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### `app/models/strategy.py`

```python
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String(25), nullable=False)
    buy_time = Column(String(8), nullable=False)  # HH:MM:SS
    sell_time = Column(String(8), nullable=False)
    stop_loss = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String(20), default="created")  # created, running, stopped, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### `app/models/broker.py`

```python
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class BrokerCredentials(Base):
    __tablename__ = "broker_credentials"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    broker_name = Column(String(50), nullable=False)  # zerodha, dhan, angel_one, fyers
    encrypted_api_key = Column(Text, nullable=False)
    encrypted_secret_key = Column(Text, nullable=False)
    encrypted_access_token = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 4.2 Database Migrations

#### Create Migration

```bash
cd backend
alembic revision --autogenerate -m "create_initial_tables"
```

#### Apply Migration

```bash
alembic upgrade head
```

#### Rollback Migration

```bash
alembic downgrade -1
```

---

## 5. Redis Implementation

### 5.1 Redis Key Schema

| Key Pattern | Type | Description | TTL |
|-------------|------|-------------|-----|
| `strategy:{id}` | Hash | Strategy configuration | None |
| `runtime:{id}` | Hash | Runtime execution state | None |
| `lock:{id}` | String | Order execution lock | 30s |
| `price:{symbol}` | String | Latest price | 5s |
| `queue:orders` | List | Order execution queue | None |

### 5.2 Redis Data Structures

#### Strategy Configuration (`strategy:{id}`)

```json
{
  "symbol": "RELIANCE",
  "buy_time": "09:30:00",
  "sell_time": "15:15:00",
  "stop_loss": "2450.00",
  "quantity": "10",
  "user_id": "uuid-string"
}
```

#### Runtime State (`runtime:{id}`)

```json
{
  "position": "NONE|BOUGHT|SOLD|EXITED_BY_SL",
  "last_action": "BUY|SELL|SL_HIT",
  "last_price": "2500.50",
  "buy_order_id": "order-123",
  "sell_order_id": "order-456"
}
```

### 5.3 Redis Service

#### `app/services/redis_service.py`

```python
import redis
from typing import Optional, Dict, Any
from app.core.config import settings

class RedisService:
    def __init__(self):
        self.client = redis.from_url(settings.redis_url, decode_responses=True)
    
    # Strategy Operations
    def load_strategy(self, strategy_id: str, data: Dict[str, Any]) -> None:
        key = f"strategy:{strategy_id}"
        self.client.hset(key, mapping=data)
    
    def get_strategy(self, strategy_id: str) -> Optional[Dict]:
        key = f"strategy:{strategy_id}"
        return self.client.hgetall(key) or None
    
    def delete_strategy(self, strategy_id: str) -> None:
        self.client.delete(f"strategy:{strategy_id}")
        self.client.delete(f"runtime:{strategy_id}")
        self.client.delete(f"lock:{strategy_id}")
    
    # Runtime Operations
    def update_runtime(self, strategy_id: str, data: Dict[str, Any]) -> None:
        key = f"runtime:{strategy_id}"
        self.client.hset(key, mapping=data)
    
    def get_runtime(self, strategy_id: str) -> Optional[Dict]:
        key = f"runtime:{strategy_id}"
        return self.client.hgetall(key) or None
    
    # Locking (Duplicate Prevention)
    def acquire_lock(self, strategy_id: str, ttl: int = 30) -> bool:
        key = f"lock:{strategy_id}"
        return self.client.set(key, "1", nx=True, ex=ttl)
    
    def release_lock(self, strategy_id: str) -> None:
        key = f"lock:{strategy_id}"
        self.client.delete(key)
    
    # Price Feed
    def update_price(self, symbol: str, price: float) -> None:
        key = f"price:{symbol}"
        self.client.set(key, str(price), ex=5)
    
    def get_price(self, symbol: str) -> Optional[float]:
        key = f"price:{symbol}"
        price = self.client.get(key)
        return float(price) if price else None
    
    # Order Queue
    def push_order(self, order_data: Dict) -> None:
        import json
        self.client.lpush("queue:orders", json.dumps(order_data))
    
    def pop_order(self) -> Optional[Dict]:
        import json
        data = self.client.rpop("queue:orders")
        return json.loads(data) if data else None

# Singleton instance
redis_service = RedisService()
```

---

## 6. Broker Integration

### 6.1 Broker Base Class

#### `app/brokers/base.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class OrderResult:
    success: bool
    order_id: Optional[str]
    message: str
    raw_response: Dict[str, Any]

class BaseBroker(ABC):
    """Abstract base class for all broker integrations."""
    
    def __init__(self, api_key: str, secret_key: str, access_token: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = access_token
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """Validate API credentials with broker."""
        pass
    
    @abstractmethod
    def place_buy_order(
        self,
        symbol: str,
        quantity: int,
        order_type: str = "MARKET"
    ) -> OrderResult:
        """Place a BUY order."""
        pass
    
    @abstractmethod
    def place_sell_order(
        self,
        symbol: str,
        quantity: int,
        order_type: str = "MARKET"
    ) -> OrderResult:
        """Place a SELL order."""
        pass
    
    @abstractmethod
    def get_ltp(self, symbol: str) -> Optional[float]:
        """Get Last Traded Price for a symbol."""
        pass
    
    @abstractmethod
    def get_positions(self) -> Dict[str, Any]:
        """Get current positions."""
        pass
```

### 6.2 Zerodha Implementation

#### `app/brokers/zerodha.py`

```python
from kiteconnect import KiteConnect
from typing import Dict, Any, Optional
import logging

from app.brokers.base import BaseBroker, OrderResult

logger = logging.getLogger(__name__)

class ZerodhaBroker(BaseBroker):
    """Zerodha Kite API integration."""
    
    def __init__(self, api_key: str, secret_key: str, access_token: str):
        super().__init__(api_key, secret_key, access_token)
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)
    
    def validate_credentials(self) -> bool:
        try:
            profile = self.kite.profile()
            return bool(profile.get("user_id"))
        except Exception as e:
            logger.error(f"Zerodha credential validation failed: {e}")
            return False
    
    def place_buy_order(
        self,
        symbol: str,
        quantity: int,
        order_type: str = "MARKET"
    ) -> OrderResult:
        try:
            order_id = self.kite.place_order(
                tradingsymbol=symbol,
                exchange="NSE",
                transaction_type="BUY",
                quantity=quantity,
                order_type=order_type,
                product="MIS",  # Intraday
                variety="regular"
            )
            return OrderResult(
                success=True,
                order_id=str(order_id),
                message="Order placed successfully",
                raw_response={"order_id": order_id}
            )
        except Exception as e:
            logger.error(f"Zerodha BUY order failed: {e}")
            return OrderResult(
                success=False,
                order_id=None,
                message=str(e),
                raw_response={"error": str(e)}
            )
    
    def place_sell_order(
        self,
        symbol: str,
        quantity: int,
        order_type: str = "MARKET"
    ) -> OrderResult:
        try:
            order_id = self.kite.place_order(
                tradingsymbol=symbol,
                exchange="NSE",
                transaction_type="SELL",
                quantity=quantity,
                order_type=order_type,
                product="MIS",
                variety="regular"
            )
            return OrderResult(
                success=True,
                order_id=str(order_id),
                message="Order placed successfully",
                raw_response={"order_id": order_id}
            )
        except Exception as e:
            logger.error(f"Zerodha SELL order failed: {e}")
            return OrderResult(
                success=False,
                order_id=None,
                message=str(e),
                raw_response={"error": str(e)}
            )
    
    def get_ltp(self, symbol: str) -> Optional[float]:
        try:
            quote = self.kite.ltp(f"NSE:{symbol}")
            return quote.get(f"NSE:{symbol}", {}).get("last_price")
        except Exception as e:
            logger.error(f"Failed to get LTP for {symbol}: {e}")
            return None
    
    def get_positions(self) -> Dict[str, Any]:
        try:
            return self.kite.positions()
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return {}
```

### 6.3 Broker Factory

#### `app/brokers/__init__.py`

```python
from typing import Optional
from app.brokers.base import BaseBroker
from app.brokers.zerodha import ZerodhaBroker
from app.brokers.dhan import DhanBroker
from app.brokers.angel_one import AngelOneBroker
from app.brokers.fyers import FyersBroker

def get_broker(
    broker_name: str,
    api_key: str,
    secret_key: str,
    access_token: str
) -> Optional[BaseBroker]:
    """Factory function to get broker instance."""
    
    brokers = {
        "zerodha": ZerodhaBroker,
        "dhan": DhanBroker,
        "angel_one": AngelOneBroker,
        "fyers": FyersBroker,
    }
    
    broker_class = brokers.get(broker_name.lower())
    if broker_class:
        return broker_class(api_key, secret_key, access_token)
    return None
```

---

## 7. Execution Engine

### 7.1 Celery Configuration

#### `app/workers/celery_app.py`

```python
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "algo_trading",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30,
    worker_prefetch_multiplier=1,
)
```

### 7.2 Execution Tasks

#### `app/workers/tasks.py`

```python
from celery import shared_task
import logging
from typing import Optional

from app.workers.celery_app import celery_app
from app.services.redis_service import redis_service
from app.brokers import get_broker
from app.core.security import decrypt_credential

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def execute_buy_order(self, strategy_id: str):
    """Execute BUY order at scheduled time."""
    try:
        # Acquire lock to prevent duplicates
        if not redis_service.acquire_lock(strategy_id):
            logger.warning(f"Lock already held for strategy {strategy_id}")
            return {"status": "skipped", "reason": "lock_held"}
        
        # Get strategy config
        strategy = redis_service.get_strategy(strategy_id)
        if not strategy:
            redis_service.release_lock(strategy_id)
            return {"status": "error", "reason": "strategy_not_found"}
        
        # Get runtime state
        runtime = redis_service.get_runtime(strategy_id)
        if runtime.get("position") != "NONE":
            redis_service.release_lock(strategy_id)
            return {"status": "skipped", "reason": "already_bought"}
        
        # Get broker credentials and place order
        # (Simplified - in production, fetch from DB)
        broker = get_broker_for_user(strategy["user_id"])
        result = broker.place_buy_order(
            symbol=strategy["symbol"],
            quantity=int(strategy["quantity"])
        )
        
        if result.success:
            # Update runtime state
            redis_service.update_runtime(strategy_id, {
                "position": "BOUGHT",
                "last_action": "BUY",
                "buy_order_id": result.order_id
            })
            logger.info(f"BUY executed for {strategy_id}: {result.order_id}")
        else:
            # Retry on failure
            raise Exception(result.message)
        
        redis_service.release_lock(strategy_id)
        return {"status": "success", "order_id": result.order_id}
        
    except Exception as e:
        redis_service.release_lock(strategy_id)
        logger.error(f"BUY execution failed for {strategy_id}: {e}")
        raise self.retry(exc=e, countdown=2)

@celery_app.task(bind=True, max_retries=3)
def execute_sell_order(self, strategy_id: str):
    """Execute SELL order at scheduled time or stop-loss."""
    try:
        if not redis_service.acquire_lock(strategy_id):
            return {"status": "skipped", "reason": "lock_held"}
        
        strategy = redis_service.get_strategy(strategy_id)
        runtime = redis_service.get_runtime(strategy_id)
        
        if runtime.get("position") != "BOUGHT":
            redis_service.release_lock(strategy_id)
            return {"status": "skipped", "reason": "no_position"}
        
        broker = get_broker_for_user(strategy["user_id"])
        result = broker.place_sell_order(
            symbol=strategy["symbol"],
            quantity=int(strategy["quantity"])
        )
        
        if result.success:
            redis_service.update_runtime(strategy_id, {
                "position": "SOLD",
                "last_action": "SELL",
                "sell_order_id": result.order_id
            })
            logger.info(f"SELL executed for {strategy_id}: {result.order_id}")
        else:
            raise Exception(result.message)
        
        redis_service.release_lock(strategy_id)
        return {"status": "success", "order_id": result.order_id}
        
    except Exception as e:
        redis_service.release_lock(strategy_id)
        logger.error(f"SELL execution failed for {strategy_id}: {e}")
        raise self.retry(exc=e, countdown=2)

@celery_app.task
def check_stop_loss(strategy_id: str, current_price: float):
    """Check and execute stop-loss if triggered."""
    strategy = redis_service.get_strategy(strategy_id)
    runtime = redis_service.get_runtime(strategy_id)
    
    if runtime.get("position") != "BOUGHT":
        return {"status": "skipped", "reason": "no_position"}
    
    stop_loss = float(strategy.get("stop_loss", 0))
    
    if current_price <= stop_loss:
        logger.warning(f"STOP-LOSS triggered for {strategy_id} at {current_price}")
        
        # Execute immediate sell
        result = execute_sell_order.apply_async(
            args=[strategy_id],
            priority=10  # High priority
        )
        
        # Update last action
        redis_service.update_runtime(strategy_id, {
            "last_action": "SL_HIT",
            "position": "EXITED_BY_SL"
        })
        
        return {"status": "sl_triggered", "price": current_price}
    
    return {"status": "ok", "price": current_price, "stop_loss": stop_loss}
```

### 7.3 Running Workers

```bash
# Start Celery worker
celery -A app.workers.celery_app worker --loglevel=info

# Start Celery beat (scheduler)
celery -A app.workers.celery_app beat --loglevel=info

# Or use the Makefile
make run-worker
make run-beat
```

---

## 8. Mobile App Implementation

### 8.1 Project Setup

```bash
# Create Expo project
npx create-expo-app algo-trading-mobile --template blank-typescript
cd algo-trading-mobile

# Install dependencies
npm install axios @react-native-async-storage/async-storage
npm install @react-navigation/native @react-navigation/native-stack
npm install react-native-screens react-native-safe-area-context
```

### 8.2 Project Structure

```
mobile/
├── App.tsx
├── src/
│   ├── api/
│   │   └── client.ts           # Axios API client
│   ├── screens/
│   │   ├── LoginScreen.tsx
│   │   ├── RegisterScreen.tsx
│   │   ├── BrokerConnectScreen.tsx
│   │   ├── StrategyCreateScreen.tsx
│   │   └── StrategyControlScreen.tsx
│   ├── components/
│   │   ├── StatusIndicator.tsx
│   │   └── TimePickerInput.tsx
│   ├── context/
│   │   └── AuthContext.tsx
│   ├── hooks/
│   │   └── usePolling.ts
│   └── types/
│       └── index.ts
└── package.json
```

### 8.3 API Client

#### `src/api/client.ts`

```typescript
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authApi = {
  register: (email: string, password: string) =>
    apiClient.post('/auth/register', { email, password }),
  
  login: (email: string, password: string) =>
    apiClient.post('/auth/login', { email, password }),
};

// Strategy API
export const strategyApi = {
  create: (data: {
    symbol: string;
    buy_time: string;
    sell_time: string;
    stop_loss: number;
    quantity: number;
  }) => apiClient.post('/strategy/create', data),
  
  start: (strategyId: string) =>
    apiClient.post(`/strategy/start/${strategyId}`),
  
  stop: (strategyId: string) =>
    apiClient.post(`/strategy/stop/${strategyId}`),
  
  getStatus: (strategyId: string) =>
    apiClient.get(`/strategy/status/${strategyId}`),
};

// Broker API
export const brokerApi = {
  connect: (data: {
    broker_name: string;
    api_key: string;
    secret_key: string;
    access_token: string;
  }) => apiClient.post('/broker/connect', data),
};

export default apiClient;
```

### 8.4 Status Polling Hook

#### `src/hooks/usePolling.ts`

```typescript
import { useEffect, useRef, useCallback } from 'react';

export function usePolling(
  callback: () => void,
  intervalMs: number = 5000,
  enabled: boolean = true
) {
  const savedCallback = useRef(callback);
  
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);
  
  useEffect(() => {
    if (!enabled) return;
    
    const tick = () => savedCallback.current();
    tick(); // Initial call
    
    const id = setInterval(tick, intervalMs);
    return () => clearInterval(id);
  }, [intervalMs, enabled]);
}
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

#### `tests/test_auth.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_success():
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_register_duplicate_email():
    # First registration
    client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "password123"
    })
    
    # Second registration with same email
    response = client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "password123"
    })
    assert response.status_code == 400

def test_login_success():
    # Register first
    client.post("/auth/register", json={
        "email": "login@example.com",
        "password": "password123"
    })
    
    # Login
    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_password():
    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
```

### 9.2 Integration Tests

#### `tests/test_integration_strategies.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_token():
    """Create user and return token."""
    response = client.post("/auth/register", json={
        "email": "strategy_test@example.com",
        "password": "password123"
    })
    return response.json()["access_token"]

def test_create_strategy_requires_stop_loss(auth_token):
    response = client.post(
        "/strategy/create",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "symbol": "RELIANCE",
            "buy_time": "09:30:00",
            "sell_time": "15:15:00",
            "quantity": 10
            # Missing stop_loss
        }
    )
    assert response.status_code == 422  # Validation error

def test_create_strategy_success(auth_token):
    response = client.post(
        "/strategy/create",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "symbol": "RELIANCE",
            "buy_time": "09:30:00",
            "sell_time": "15:15:00",
            "stop_loss": 2450.00,
            "quantity": 10
        }
    )
    assert response.status_code == 200
    assert response.json()["symbol"] == "RELIANCE"
```

### 9.3 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run tests matching pattern
pytest -k "test_login" -v
```

---

## 10. Deployment Guide

### 10.1 Docker Build

#### `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### `docker-compose.yml`

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/algo_trading
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - AES_MASTER_KEY=${AES_MASTER_KEY}
    depends_on:
      - postgres
      - redis

  worker:
    build: ./backend
    command: celery -A app.workers.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/algo_trading
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=algo_trading
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 10.2 AWS Deployment

#### Infrastructure Components

| Service | AWS Resource | Configuration |
|---------|--------------|---------------|
| Backend API | ECS Fargate | 2 vCPU, 4GB RAM |
| Celery Workers | ECS Fargate | 1 vCPU, 2GB RAM |
| Database | RDS PostgreSQL | db.t3.micro |
| Cache | ElastiCache Redis | cache.t3.micro |
| Load Balancer | ALB | Public-facing |
| Container Registry | ECR | Private |

#### Deployment Steps

```bash
# 1. Build and push Docker image
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.ap-south-1.amazonaws.com

docker build -t algo-trading-backend ./backend
docker tag algo-trading-backend:latest <account>.dkr.ecr.ap-south-1.amazonaws.com/algo-trading-backend:latest
docker push <account>.dkr.ecr.ap-south-1.amazonaws.com/algo-trading-backend:latest

# 2. Update ECS service
aws ecs update-service --cluster algo-trading --service backend --force-new-deployment

# 3. Run database migrations
aws ecs run-task --cluster algo-trading --task-definition migrate --launch-type FARGATE
```

---

## 11. Troubleshooting

### 11.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Database connection failed | Wrong DATABASE_URL | Verify `.env` configuration |
| Redis connection refused | Redis not running | Start Redis: `docker-compose up redis` |
| JWT decode error | Invalid/expired token | Re-login to get new token |
| Broker validation failed | Invalid API credentials | Verify credentials with broker |
| Order execution timeout | Broker API slow | Increase task timeout |
| Duplicate orders | Lock not acquired | Check Redis lock mechanism |

### 11.2 Debug Commands

```bash
# Check backend logs
docker-compose logs -f backend

# Check worker logs
docker-compose logs -f worker

# Redis CLI
docker-compose exec redis redis-cli
> KEYS strategy:*
> HGETALL strategy:<id>

# PostgreSQL
docker-compose exec postgres psql -U postgres -d algo_trading
\dt                    # List tables
SELECT * FROM users;   # Query users

# Test API endpoint
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### 11.3 Performance Monitoring

```bash
# Check Redis latency
redis-cli --latency

# Monitor Celery tasks
celery -A app.workers.celery_app inspect active

# Check database connections
SELECT count(*) FROM pg_stat_activity;
```

---

## Appendix A: API Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | Login user |
| `/broker/connect` | POST | Connect broker credentials |
| `/strategy/create` | POST | Create strategy |
| `/strategy/start/{id}` | POST | Start strategy |
| `/strategy/stop/{id}` | POST | Stop strategy |
| `/strategy/status/{id}` | GET | Get strategy status |
| `/health` | GET | Health check |

---

## Appendix B: Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `JWT_SECRET_KEY` | Yes | JWT signing key |
| `AES_MASTER_KEY` | Yes | 32-byte key for AES encryption |
| `ENVIRONMENT` | No | development/staging/production |
| `DEBUG` | No | Enable debug mode |

---

## Appendix C: Related Documents

| Document | Purpose |
|----------|---------|
| [PRD.md](PRD.md) | Product Requirements |
| [SRS.MD](SRS.MD) | Software Requirements |
| [HLD.MD](HLD.MD) | High-Level Design |
| [LLD.MD](LLD.MD) | Low-Level Design |
| [API-SCHEMA.md](API-SCHEMA.md) | API Specifications |
| [SCOPE.md](SCOPE.md) | Project Scope |

---

**Document Owner:** Engineering Team  
**Last Updated:** December 2024  
**Next Review:** After each milestone
