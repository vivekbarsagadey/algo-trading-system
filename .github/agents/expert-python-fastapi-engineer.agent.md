````chatagent
---
description: 'Algo Trading System Python/FastAPI/Redis engineering - focuses on project-specific patterns. Assumes you know Python, FastAPI, Redis fundamentals.'
model: Claude Opus 4.5 (Preview) (copilot)
tools: ['edit', 'runNotebooks', 'search', 'new', 'runCommands', 'runTasks', 'microsoft/playwright-mcp/*', 'microsoftdocs/mcp/*', 'context7/*', 'figma/*', 'github/github-mcp-server/*', 'usages', 'vscodeAPI', 'problems', 'changes', 'testFailure', 'openSimpleBrowser', 'fetch', 'githubRepo', 'github.vscode-pull-request-github/activePullRequest', 'github.vscode-pull-request-github/openPullRequest', 'extensions', 'todos']
handoffs:
  - label: Code Review
    agent: principal-software-engineer
    prompt: Review the implementation for Algo Trading System standards, strategy validation, and execution patterns.
    send: false
  - label: Debug Issues
    agent: debug
    prompt: Debug and fix any issues found in the application.
    send: false
  - label: Create Implementation Plan
    agent: implementation-plan
    prompt: Create a structured implementation plan before coding.
    send: false
---

# Algo Trading System Python/FastAPI/Redis Full-Stack Engineer

> **LLM Assumption**: You already know Python, FastAPI, Redis, Pydantic, and PostgreSQL fundamentals. This agent focuses ONLY on Algo Trading System-specific patterns and architecture.

## Critical Context

**Read First**: `.github/agents/algo-trading-system-agent-context.md` (Algo Trading System-specific patterns)
**Comprehensive Rules**: `.github/instructions/accubrief-rules.instructions.md`

**Stack**: FastAPI • Python 3.11+ • Redis • PostgreSQL • React Native/Expo • AWS

## Algo Trading System-Specific Implementation Patterns

### 1. Strategy Execution Pattern (CRITICAL)

**Every strategy execution must follow this pattern:**

```python
# Load strategy from Redis runtime
strategy = redis_client.get(f"strategy:{strategy_id}")

# Check execution conditions
if should_execute_buy(strategy, market_data):
    result = place_order_via_broker(strategy, "BUY")
    update_execution_state(strategy_id, result)
elif should_execute_sell(strategy, market_data):
    result = place_order_via_broker(strategy, "SELL")
    update_execution_state(strategy_id, result)
````

### 2. API Route Pattern

**Template for all Algo Trading System API routes:**

```python
# api/strategies.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.strategy import StrategyCreate, StrategyResponse
from app.services.strategy_service import create_strategy_service

router = APIRouter(prefix="/strategies", tags=["strategies"])

@router.post("/", response_model=StrategyResponse)
async def create_strategy(
    strategy_data: StrategyCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new trading strategy."""
    # 1. Get service
    service = create_strategy_service(db, redis_client)

    # 2. Validate strategy
    errors = service["validate_strategy"](strategy_data.dict())
    if errors:
        raise HTTPException(status_code=400, detail=errors)

    # 3. Create strategy with user isolation
    strategy = service["create_strategy"](current_user.id, strategy_data.dict())

    # 4. Return response
    return StrategyResponse.from_orm(strategy)
```

### 3. Functional Service Pattern (MANDATORY)

**Use factory functions, not classes:**

```python
# services/strategy_service.py
from sqlalchemy.orm import Session
from redis import Redis
from app.models.strategy import Strategy
from app.utils.id_utils import generate_strategy_id
from datetime import datetime

def create_strategy_service(db: Session, redis_client: Redis):
    """Factory function returning strategy operations."""

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
        if not strategy_data.get('quantity') or strategy_data['quantity'] <= 0:
            errors.append("Quantity must be positive")
        return errors

    def create_strategy(user_id: str, strategy_data: dict) -> Strategy:
        strategy = Strategy(
            id=generate_strategy_id(),
            user_id=user_id,
            symbol=strategy_data['symbol'],
            buy_time=strategy_data['buy_time'],
            sell_time=strategy_data['sell_time'],
            stop_loss=strategy_data['stop_loss'],
            quantity=strategy_data['quantity'],
            status="ACTIVE"
        )
        db.add(strategy)
        db.commit()
        db.refresh(strategy)
        return strategy

    def get_strategy(strategy_id: str, user_id: str) -> Strategy:
        return db.query(Strategy).filter(
            Strategy.id == strategy_id,
            Strategy.user_id == user_id,
            Strategy.status != "DELETED"
        ).first()

    def start_strategy(strategy_id: str, user_id: str) -> Strategy:
        strategy = get_strategy(strategy_id, user_id)
        if not strategy:
            raise ValueError("Strategy not found")

        strategy.status = "RUNNING"
        db.commit()

        # Load to Redis runtime
        execution_state = {
            "strategy_id": strategy.id,
            "symbol": strategy.symbol,
            "buy_time": strategy.buy_time,
            "sell_time": strategy.sell_time,
            "stop_loss": strategy.stop_loss,
            "quantity": strategy.quantity,
            "status": "WAITING"
        }
        redis_client.set(f"strategy:{strategy.id}:state", json.dumps(execution_state))

        return strategy

    return {
        "validate_strategy": validate_strategy,
        "create_strategy": create_strategy,
        "get_strategy": get_strategy,
        "start_strategy": start_strategy,
    }
```

### 4. Multi-Tenancy (MANDATORY)

**ALWAYS filter by user_id for security:**

```python
# ❌ FORBIDDEN - Data leakage vulnerability
strategies = db.query(Strategy).all()

# ✅ REQUIRED - User isolation
strategies = db.query(Strategy).filter(
    Strategy.user_id == current_user.id
).all()
```

### 5. Credential Encryption Pattern

**All broker credentials must be AES-256 encrypted:**

```python
# core/security.py
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

def create_encryption_service(master_key: str):
    """Factory function for encryption operations."""

    def encrypt_aes256(plain_text: str) -> str:
        """Encrypt sensitive data with AES-256."""
        key = hashlib.sha256(master_key.encode()).digest()
        iv = os.urandom(16)

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # PKCS7 padding
        block_size = 16
        padding_length = block_size - (len(plain_text) % block_size)
        padded_text = plain_text + chr(padding_length) * padding_length

        encrypted = encryptor.update(padded_text.encode()) + encryptor.finalize()
        return b64encode(iv + encrypted).decode()

    def decrypt_aes256(encrypted_text: str) -> str:
        """Decrypt AES-256 encrypted data."""
        key = hashlib.sha256(master_key.encode()).digest()
        encrypted_data = b64decode(encrypted_text)

        iv = encrypted_data[:16]
        encrypted = encrypted_data[16:]

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        decrypted_padded = decryptor.update(encrypted) + decryptor.finalize()

        # Remove PKCS7 padding
        padding_length = ord(decrypted_padded[-1:])
        return decrypted_padded[:-padding_length].decode()

    return {
        "encrypt": encrypt_aes256,
        "decrypt": decrypt_aes256,
    }
```

    def sign_summary(summary_data: dict, tenant_id: str) -> dict:
        # 1. Get active signing key
        key = kms_service.get_active_signing_key(tenant_id)

        # 2. Canonicalize JSON
        canonical = json.dumps(summary_data, sort_keys=True, separators=(",", ":"))

        # 3. Compute SHA-256 hash
        digest = hashlib.sha256(canonical.encode()).hexdigest()
        document_hash = f"SHA256:{digest}"

        # 4. Sign with RSA
        signature_bytes = key.private_key.sign(
            canonical.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        # 5. Return signature metadata
        return {
            "signature_id": generate_signature_id(),
            "public_key_id": key.public_key_id,
            "signature_value": b64encode(signature_bytes).decode(),
            "document_hash": document_hash,
            "algorithm": "RS256",
            "created_at": datetime.utcnow().isoformat()
        }

    return {
        "sign_summary": sign_summary,
    }

````

### 6. Pydantic Schema Pattern

```python
# schemas/strategy.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

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
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
````

### 7. Error Handling Pattern

```python
from fastapi import HTTPException

def handle_broker_error(broker_name: str, error: Exception) -> None:
    """Handle broker-specific errors with appropriate HTTP responses."""
    if "authentication" in str(error).lower():
        raise HTTPException(
            status_code=401,
            detail=f"Invalid {broker_name} credentials"
        )
    elif "rate limit" in str(error).lower():
        raise HTTPException(
            status_code=429,
            detail=f"{broker_name} rate limit exceeded"
        )
    else:
        raise HTTPException(
            status_code=500,
            detail=f"{broker_name} API error: {str(error)}"
        )
```

# Standard error responses

def raise_not_found(entity: str, id: str):
raise HTTPException(status_code=404, detail=f"{entity} {id} not found")

def raise_unauthorized():
raise HTTPException(status_code=401, detail="Invalid API key or token")

def raise_forbidden(reason: str = "Access denied"):
raise HTTPException(status_code=403, detail=reason)

def raise_validation_error(field: str, message: str):
raise HTTPException(status_code=422, detail={"field": field, "message": message})

````

### 8. Worker Job Pattern

```python
# workers/execution_worker.py
from app.services.execution_service import create_execution_service
from app.brokers.factory import get_broker

def handle_execution_job(strategy_id: str):
    """Execute trading strategy based on time and market conditions."""
    db = get_db_session()
    redis_client = get_redis_client()

    try:
        execution_service = create_execution_service(db, redis_client)

        # 1. Get current market data
        market_data = execution_service["get_market_data"](strategy_id)

        # 2. Check execution conditions
        if execution_service["should_execute_buy"](strategy_id, market_data):
            broker = get_broker(strategy_id)
            result = broker.place_order({
                "symbol": market_data["symbol"],
                "side": "BUY",
                "quantity": market_data["quantity"],
                "price": market_data["current_price"]
            })
            execution_service["update_execution_state"](strategy_id, result)

        elif execution_service["should_execute_sell"](strategy_id, market_data):
            broker = get_broker(strategy_id)
            result = broker.place_order({
                "symbol": market_data["symbol"],
                "side": "SELL",
                "quantity": market_data["quantity"],
                "price": market_data["current_price"]
            })
            execution_service["update_execution_state"](strategy_id, result)

    except Exception as e:
        # 3. Handle failure
        execution_service["mark_failed"](strategy_id, str(e))
        logger.error(f"Execution failed for strategy {strategy_id}: {e}")
    finally:
        db.close()
````

---

## React Native Patterns (TypeScript)

### Component Pattern

```typescript
// components/StrategyCard.tsx
import React from "react";
import { View, Text, TouchableOpacity } from "react-native";

interface StrategyCardProps {
  strategy: Strategy;
  onStart: (id: string) => void;
  onStop: (id: string) => void;
}

export const StrategyCard: React.FC<StrategyCardProps> = ({ strategy, onStart, onStop }) => {
  return (
    <View style={styles.card}>
      <Text style={styles.symbol}>{strategy.symbol}</Text>
      <Text>
        Buy: {strategy.buy_time} | Sell: {strategy.sell_time}
      </Text>
      <Text>Stop Loss: ₹{strategy.stop_loss}</Text>

      <View style={styles.actions}>
        {strategy.status === "ACTIVE" ? (
          <TouchableOpacity onPress={() => onStart(strategy.id)}>
            <Text style={styles.startButton}>Start</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity onPress={() => onStop(strategy.id)}>
            <Text style={styles.stopButton}>Stop</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
};
```

### Hook Pattern

```typescript
// hooks/useStrategies.ts
import { useState, useEffect } from "react";
import { Strategy } from "../types";

export function useStrategies() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchStrategies = async () => {
    try {
      const response = await fetch("/api/strategies");
      const data = await response.json();
      setStrategies(data);
    } catch (error) {
      console.error("Failed to fetch strategies:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStrategies();
  }, []);

  return {
    strategies,
    loading,
    refetch: fetchStrategies,
  };
}
```

---

## File Structure Reference

```
backend/app/
├── api/
│   ├── auth.py           # Authentication
│   ├── strategies.py     # Strategy CRUD
│   └── brokers.py        # Broker management
├── brokers/
│   ├── base.py           # Base broker class
│   ├── zerodha.py        # Zerodha integration
│   ├── dhan.py           # Dhan integration
│   └── fyers.py          # Fyers integration
├── core/
│   ├── config.py         # Configuration
│   ├── database.py       # DB connection
│   └── security.py       # Encryption, JWT
├── models/
│   ├── user.py           # User model
│   ├── strategy.py       # Strategy model
│   └── broker.py         # Broker credentials
├── services/
│   ├── auth_service.py
│   ├── strategy_service.py
│   └── broker_service.py
├── workers/
│   ├── execution_engine.py
│   └── scheduler.py
└── utils/
    └── validators.py
```

```

```
