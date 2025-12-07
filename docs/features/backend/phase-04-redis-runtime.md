---
goal: Phase 4 - Redis Runtime & In-Memory Execution
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Backend Engineering Team
status: Planned
tags: [backend, redis, runtime, caching, pub-sub]
---

# Phase 4: Redis Runtime & In-Memory Execution

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

## Goal

**GOAL-004**: Implement Redis-based in-memory runtime store for active strategy execution

## Overview

This phase implements the Redis layer for storing active strategies during execution. Redis provides sub-millisecond access for the execution engine, stop-loss monitoring, and real-time event broadcasting via pub/sub.

---

## Prerequisites

- Phase 1-3 completed
- Redis 7+ installed and running
- Understanding of Redis data structures

## Dependencies

```txt
redis>=5.0.0
```

---

## Implementation Tasks

### TASK-043: Create Redis Service

**File**: `backend/app/services/redis_service.py`

**Description**: Create RedisClient wrapper with connection pooling, retry logic, and health check.

**Acceptance Criteria**:
- [ ] Async Redis client using redis-py
- [ ] Connection pooling for efficiency
- [ ] Retry logic with exponential backoff
- [ ] Health check method
- [ ] Graceful connection handling
- [ ] Configurable from environment variables

**Code Reference**:
```python
import redis.asyncio as redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class RedisService:
    """Redis client wrapper with connection pooling and retry logic"""
    
    def __init__(self):
        self.pool = None
        self.client = None
    
    async def connect(self):
        """Initialize Redis connection pool"""
        retry = Retry(ExponentialBackoff(), 3)
        self.pool = redis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=20,
            retry=retry,
            retry_on_timeout=True,
            decode_responses=True
        )
        self.client = redis.Redis(connection_pool=self.pool)
        logger.info("Redis connection pool initialized")
    
    async def disconnect(self):
        """Close Redis connections"""
        if self.pool:
            await self.pool.disconnect()
            logger.info("Redis connection pool closed")
    
    async def health_check(self) -> bool:
        """Check Redis connectivity"""
        try:
            await self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
    
    async def get(self, key: str) -> str | None:
        """Get value by key"""
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, ex: int = None) -> bool:
        """Set value with optional expiry in seconds"""
        return await self.client.set(key, value, ex=ex)
    
    async def delete(self, key: str) -> int:
        """Delete key"""
        return await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return await self.client.exists(key) > 0
    
    async def hset(self, name: str, mapping: dict) -> int:
        """Set hash fields"""
        return await self.client.hset(name, mapping=mapping)
    
    async def hget(self, name: str, key: str) -> str | None:
        """Get hash field"""
        return await self.client.hget(name, key)
    
    async def hgetall(self, name: str) -> dict:
        """Get all hash fields"""
        return await self.client.hgetall(name)
    
    async def hdel(self, name: str, *keys) -> int:
        """Delete hash fields"""
        return await self.client.hdel(name, *keys)
    
    async def publish(self, channel: str, message: str) -> int:
        """Publish message to channel"""
        return await self.client.publish(channel, message)
    
    async def subscribe(self, *channels):
        """Subscribe to channels"""
        pubsub = self.client.pubsub()
        await pubsub.subscribe(*channels)
        return pubsub
    
    async def setex(self, key: str, seconds: int, value: str) -> bool:
        """Set key with expiry"""
        return await self.client.setex(key, seconds, value)
    
    async def setnx(self, key: str, value: str) -> bool:
        """Set key if not exists (for locking)"""
        return await self.client.setnx(key, value)

# Singleton instance
_redis_service: RedisService = None

async def get_redis() -> RedisService:
    """Get Redis service instance"""
    global _redis_service
    if _redis_service is None:
        _redis_service = RedisService()
        await _redis_service.connect()
    return _redis_service
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-044: Implement set_active_strategy

**File**: `backend/app/services/redis_service.py`

**Description**: Implement `set_active_strategy(strategy_id, data)` to store active strategy in Redis with user namespace.

**Acceptance Criteria**:
- [ ] Stores strategy data as Redis hash
- [ ] Uses namespace pattern for isolation
- [ ] Includes all fields needed for execution
- [ ] JSON serialization for complex fields
- [ ] Returns success/failure

**Code Reference**:
```python
import json
from typing import Dict, Any

# Key patterns
STRATEGY_KEY = "user:{user_id}:strategy:{strategy_id}"
ACTIVE_STRATEGIES_SET = "active_strategies"

async def set_active_strategy(strategy_id: str, data: Dict[str, Any]) -> bool:
    """Store active strategy in Redis"""
    redis = await get_redis()
    
    user_id = data.get("user_id")
    if not user_id:
        raise ValueError("user_id is required in strategy data")
    
    key = STRATEGY_KEY.format(user_id=user_id, strategy_id=strategy_id)
    
    # Prepare data for Redis (convert to strings)
    redis_data = {}
    for k, v in data.items():
        if isinstance(v, (dict, list)):
            redis_data[k] = json.dumps(v)
        else:
            redis_data[k] = str(v)
    
    # Store as hash
    await redis.hset(key, redis_data)
    
    # Add to active strategies set for quick lookup
    await redis.client.sadd(ACTIVE_STRATEGIES_SET, f"{user_id}:{strategy_id}")
    
    logger.info(f"Strategy {strategy_id} stored in Redis")
    return True
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-045: Implement get_active_strategy

**File**: `backend/app/services/redis_service.py`

**Description**: Implement `get_active_strategy(strategy_id)` to retrieve active strategy state.

**Acceptance Criteria**:
- [ ] Retrieves strategy data from Redis hash
- [ ] Deserializes JSON fields
- [ ] Returns None if not found
- [ ] Handles missing user_id lookup

**Code Reference**:
```python
async def get_active_strategy(strategy_id: str, user_id: str = None) -> Dict[str, Any] | None:
    """Get active strategy from Redis"""
    redis = await get_redis()
    
    if user_id:
        key = STRATEGY_KEY.format(user_id=user_id, strategy_id=strategy_id)
        data = await redis.hgetall(key)
        if data:
            return _deserialize_strategy_data(data)
    else:
        # Search in active strategies (less efficient)
        members = await redis.client.smembers(ACTIVE_STRATEGIES_SET)
        for member in members:
            if member.endswith(f":{strategy_id}"):
                uid, _ = member.rsplit(":", 1)
                key = STRATEGY_KEY.format(user_id=uid, strategy_id=strategy_id)
                data = await redis.hgetall(key)
                if data:
                    return _deserialize_strategy_data(data)
    
    return None

def _deserialize_strategy_data(data: dict) -> dict:
    """Deserialize Redis hash to Python dict"""
    result = {}
    for k, v in data.items():
        # Try to parse as JSON for complex fields
        try:
            if v.startswith("{") or v.startswith("["):
                result[k] = json.loads(v)
            else:
                result[k] = v
        except (json.JSONDecodeError, AttributeError):
            result[k] = v
    return result
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-046: Implement update_strategy_state

**File**: `backend/app/services/redis_service.py`

**Description**: Implement `update_strategy_state(strategy_id, updates)` for partial state updates.

**Acceptance Criteria**:
- [ ] Updates only specified fields
- [ ] Preserves other fields
- [ ] Atomic operation
- [ ] Returns success/failure
- [ ] Publishes update event

**Code Reference**:
```python
async def update_strategy_state(
    strategy_id: str,
    user_id: str,
    updates: Dict[str, Any]
) -> bool:
    """Update strategy state in Redis"""
    redis = await get_redis()
    
    key = STRATEGY_KEY.format(user_id=user_id, strategy_id=strategy_id)
    
    # Check if strategy exists
    if not await redis.exists(key):
        logger.warning(f"Strategy {strategy_id} not found in Redis")
        return False
    
    # Prepare updates
    redis_updates = {}
    for k, v in updates.items():
        if isinstance(v, (dict, list)):
            redis_updates[k] = json.dumps(v)
        else:
            redis_updates[k] = str(v)
    
    # Update hash fields
    await redis.hset(key, redis_updates)
    
    # Publish update event
    event = {
        "type": "STRATEGY_UPDATED",
        "strategy_id": strategy_id,
        "updates": updates
    }
    await redis.publish(f"events:{user_id}", json.dumps(event))
    
    logger.info(f"Strategy {strategy_id} state updated: {list(updates.keys())}")
    return True
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-047: Implement remove_active_strategy

**File**: `backend/app/services/redis_service.py`

**Description**: Implement `remove_active_strategy(strategy_id)` to clean up stopped strategies.

**Acceptance Criteria**:
- [ ] Removes strategy hash from Redis
- [ ] Removes from active strategies set
- [ ] Cleans up related locks
- [ ] Publishes removal event
- [ ] Returns success/failure

**Code Reference**:
```python
async def remove_active_strategy(strategy_id: str, user_id: str) -> bool:
    """Remove strategy from Redis"""
    redis = await get_redis()
    
    key = STRATEGY_KEY.format(user_id=user_id, strategy_id=strategy_id)
    
    # Delete hash
    deleted = await redis.delete(key)
    
    # Remove from active set
    await redis.client.srem(ACTIVE_STRATEGIES_SET, f"{user_id}:{strategy_id}")
    
    # Clean up any locks
    lock_pattern = f"lock:order:{strategy_id}:*"
    async for lock_key in redis.client.scan_iter(match=lock_pattern):
        await redis.delete(lock_key)
    
    # Publish removal event
    event = {
        "type": "STRATEGY_REMOVED",
        "strategy_id": strategy_id
    }
    await redis.publish(f"events:{user_id}", json.dumps(event))
    
    logger.info(f"Strategy {strategy_id} removed from Redis")
    return deleted > 0
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-048: Implement get_all_active_strategies

**File**: `backend/app/services/redis_service.py`

**Description**: Implement `get_all_active_strategies()` for market listener to fetch all running strategies.

**Acceptance Criteria**:
- [ ] Returns all active strategies
- [ ] Efficient for market listener polling
- [ ] Groups by symbol for price subscription
- [ ] Handles large number of strategies

**Code Reference**:
```python
from typing import List

async def get_all_active_strategies() -> List[Dict[str, Any]]:
    """Get all active strategies from Redis"""
    redis = await get_redis()
    
    strategies = []
    
    # Get all active strategy keys
    members = await redis.client.smembers(ACTIVE_STRATEGIES_SET)
    
    for member in members:
        user_id, strategy_id = member.rsplit(":", 1)
        key = STRATEGY_KEY.format(user_id=user_id, strategy_id=strategy_id)
        data = await redis.hgetall(key)
        if data:
            strategies.append(_deserialize_strategy_data(data))
    
    return strategies

async def get_active_strategies_by_symbol(symbol: str) -> List[Dict[str, Any]]:
    """Get active strategies for a specific symbol"""
    all_strategies = await get_all_active_strategies()
    return [s for s in all_strategies if s.get("symbol") == symbol]

async def get_active_symbols() -> set:
    """Get set of symbols with active strategies"""
    all_strategies = await get_all_active_strategies()
    return {s.get("symbol") for s in all_strategies if s.get("symbol")}
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-049: Create Per-User Namespace Pattern

**File**: `backend/app/services/redis_service.py`

**Description**: Create per-user namespace pattern: `user:{user_id}:strategy:{strategy_id}` for multi-tenant isolation.

**Acceptance Criteria**:
- [ ] All user data scoped by user_id
- [ ] Key patterns documented
- [ ] Helper functions for key generation
- [ ] No cross-user data access possible

**Code Reference**:
```python
# Key Patterns Documentation
"""
Redis Key Namespace Patterns:

User-Scoped Keys:
- user:{user_id}:strategy:{strategy_id}  - Active strategy hash
- user:{user_id}:broker                   - Broker connection cache
- events:{user_id}                        - User event pub/sub channel

Global Keys:
- active_strategies                       - Set of active strategy references
- ltp:{symbol}                            - Last traded price cache
- lock:order:{strategy_id}:{action}       - Order execution lock

Token Management:
- token_blacklist:{token_hash}            - Blacklisted tokens
- reset:{reset_token}                     - Password reset tokens

Cache Keys:
- cache:broker_status:{user_id}           - Broker status cache
- cache:analytics:{user_id}:{metric}      - Analytics cache
"""

class RedisKeys:
    """Redis key pattern generators"""
    
    @staticmethod
    def strategy(user_id: str, strategy_id: str) -> str:
        return f"user:{user_id}:strategy:{strategy_id}"
    
    @staticmethod
    def user_events(user_id: str) -> str:
        return f"events:{user_id}"
    
    @staticmethod
    def ltp(symbol: str) -> str:
        return f"ltp:{symbol}"
    
    @staticmethod
    def order_lock(strategy_id: str, action: str) -> str:
        return f"lock:order:{strategy_id}:{action}"
    
    @staticmethod
    def token_blacklist(token_hash: str) -> str:
        return f"token_blacklist:{token_hash}"
    
    @staticmethod
    def broker_status_cache(user_id: str) -> str:
        return f"cache:broker_status:{user_id}"
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-050: Implement Redis Distributed Locking

**File**: `backend/app/services/redis_service.py`

**Description**: Implement Redis locking for duplicate order prevention: `lock:order:{strategy_id}:{action}`.

**Acceptance Criteria**:
- [ ] Acquire lock with TTL
- [ ] Release lock safely
- [ ] Check lock before order
- [ ] Auto-expire to prevent deadlocks
- [ ] Context manager pattern

**Code Reference**:
```python
import asyncio
from contextlib import asynccontextmanager

LOCK_TTL_SECONDS = 30  # Lock expires after 30 seconds

class DistributedLock:
    """Redis-based distributed lock"""
    
    def __init__(self, redis_service: RedisService, key: str, ttl: int = LOCK_TTL_SECONDS):
        self.redis = redis_service
        self.key = key
        self.ttl = ttl
        self.acquired = False
    
    async def acquire(self) -> bool:
        """Try to acquire the lock"""
        # SET NX with expiry
        result = await self.redis.client.set(
            self.key,
            "locked",
            nx=True,
            ex=self.ttl
        )
        self.acquired = result is not None
        return self.acquired
    
    async def release(self) -> bool:
        """Release the lock"""
        if self.acquired:
            await self.redis.delete(self.key)
            self.acquired = False
            return True
        return False
    
    async def is_locked(self) -> bool:
        """Check if lock is currently held"""
        return await self.redis.exists(self.key)

@asynccontextmanager
async def acquire_order_lock(strategy_id: str, action: str):
    """Context manager for order execution lock"""
    redis = await get_redis()
    lock_key = RedisKeys.order_lock(strategy_id, action)
    lock = DistributedLock(redis, lock_key)
    
    acquired = await lock.acquire()
    if not acquired:
        raise LockAcquisitionError(f"Could not acquire lock for {strategy_id}:{action}")
    
    try:
        yield lock
    finally:
        await lock.release()

class LockAcquisitionError(Exception):
    """Raised when lock cannot be acquired"""
    pass

async def is_order_locked(strategy_id: str, action: str) -> bool:
    """Check if order is currently locked"""
    redis = await get_redis()
    lock_key = RedisKeys.order_lock(strategy_id, action)
    return await redis.exists(lock_key)
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-051: Add Redis Pub/Sub for Event Broadcasting

**File**: `backend/app/services/redis_service.py`

**Description**: Add Redis pub/sub for real-time event broadcasting: `events:{user_id}` channel.

**Acceptance Criteria**:
- [ ] Publish events to user channel
- [ ] Subscribe to user channel
- [ ] Event types defined
- [ ] JSON serialization for events
- [ ] Async message handling

**Code Reference**:
```python
from enum import Enum
from typing import Callable, Awaitable
from datetime import datetime

class EventType(str, Enum):
    ORDER_EXECUTED = "ORDER_EXECUTED"
    SL_TRIGGERED = "SL_TRIGGERED"
    STRATEGY_STARTED = "STRATEGY_STARTED"
    STRATEGY_STOPPED = "STRATEGY_STOPPED"
    STRATEGY_UPDATED = "STRATEGY_UPDATED"
    STRATEGY_ERROR = "STRATEGY_ERROR"
    STRATEGY_COMPLETED = "STRATEGY_COMPLETED"

async def publish_event(
    user_id: str,
    event_type: EventType,
    data: dict
) -> int:
    """Publish event to user's event channel"""
    redis = await get_redis()
    
    event = {
        "type": event_type.value,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data
    }
    
    channel = RedisKeys.user_events(user_id)
    subscribers = await redis.publish(channel, json.dumps(event))
    
    logger.debug(f"Published {event_type} to {channel}, {subscribers} subscribers")
    return subscribers

async def subscribe_to_events(
    user_id: str,
    callback: Callable[[dict], Awaitable[None]]
):
    """Subscribe to user's event channel"""
    redis = await get_redis()
    channel = RedisKeys.user_events(user_id)
    
    pubsub = await redis.subscribe(channel)
    
    async for message in pubsub.listen():
        if message["type"] == "message":
            try:
                event = json.loads(message["data"])
                await callback(event)
            except json.JSONDecodeError:
                logger.error(f"Invalid event JSON: {message['data']}")
            except Exception as e:
                logger.error(f"Event callback error: {e}")

# Helper for publishing specific events
async def publish_order_executed(user_id: str, strategy_id: str, order_type: str, price: float):
    await publish_event(user_id, EventType.ORDER_EXECUTED, {
        "strategy_id": strategy_id,
        "order_type": order_type,
        "price": price
    })

async def publish_sl_triggered(user_id: str, strategy_id: str, trigger_price: float):
    await publish_event(user_id, EventType.SL_TRIGGERED, {
        "strategy_id": strategy_id,
        "trigger_price": trigger_price
    })

async def publish_strategy_error(user_id: str, strategy_id: str, error: str):
    await publish_event(user_id, EventType.STRATEGY_ERROR, {
        "strategy_id": strategy_id,
        "error": error
    })
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-052: Implement State Synchronization

**File**: `backend/app/services/redis_service.py`

**Description**: Implement strategy state synchronization between PostgreSQL and Redis on strategy start/stop.

**Acceptance Criteria**:
- [ ] Sync from DB to Redis on start
- [ ] Sync from Redis to DB on stop
- [ ] Handle sync failures gracefully
- [ ] Log sync operations
- [ ] Periodic reconciliation option

**Code Reference**:
```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.strategy import Strategy, StrategyStatus, PositionStatus

async def sync_strategy_to_redis(db: AsyncSession, strategy_id: str) -> bool:
    """Sync strategy from PostgreSQL to Redis"""
    from sqlalchemy import select
    
    result = await db.execute(
        select(Strategy).where(Strategy.id == strategy_id)
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        logger.error(f"Strategy {strategy_id} not found in database")
        return False
    
    data = {
        "id": strategy.id,
        "user_id": strategy.user_id,
        "symbol": strategy.symbol,
        "buy_time": str(strategy.buy_time),
        "sell_time": str(strategy.sell_time),
        "stop_loss": str(strategy.stop_loss),
        "quantity": strategy.quantity,
        "status": strategy.status.value,
        "position": strategy.position.value,
        "entry_price": str(strategy.entry_price) if strategy.entry_price else None,
        "exit_price": str(strategy.exit_price) if strategy.exit_price else None,
    }
    
    await set_active_strategy(strategy_id, data)
    logger.info(f"Synced strategy {strategy_id} to Redis")
    return True

async def sync_strategy_to_db(db: AsyncSession, strategy_id: str) -> bool:
    """Sync strategy state from Redis to PostgreSQL"""
    from sqlalchemy import select
    from decimal import Decimal
    
    # Get from Redis
    redis_data = await get_active_strategy(strategy_id)
    if not redis_data:
        logger.warning(f"Strategy {strategy_id} not found in Redis")
        return False
    
    # Get from DB
    result = await db.execute(
        select(Strategy).where(Strategy.id == strategy_id)
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        logger.error(f"Strategy {strategy_id} not found in database")
        return False
    
    # Update database with Redis state
    strategy.status = StrategyStatus(redis_data.get("status", strategy.status.value))
    strategy.position = PositionStatus(redis_data.get("position", strategy.position.value))
    strategy.last_action = redis_data.get("last_action")
    
    if redis_data.get("entry_price"):
        strategy.entry_price = Decimal(redis_data["entry_price"])
    if redis_data.get("exit_price"):
        strategy.exit_price = Decimal(redis_data["exit_price"])
    
    await db.commit()
    logger.info(f"Synced strategy {strategy_id} to database")
    return True

async def reconcile_strategies(db: AsyncSession):
    """Reconcile Redis and PostgreSQL states for all active strategies"""
    from sqlalchemy import select
    
    # Get active strategies from database
    result = await db.execute(
        select(Strategy).where(Strategy.status == StrategyStatus.RUNNING)
    )
    db_strategies = {s.id: s for s in result.scalars().all()}
    
    # Get active strategies from Redis
    redis_strategies = await get_all_active_strategies()
    redis_ids = {s["id"] for s in redis_strategies}
    
    # Find discrepancies
    db_only = set(db_strategies.keys()) - redis_ids
    redis_only = redis_ids - set(db_strategies.keys())
    
    # Sync DB-only strategies to Redis
    for strategy_id in db_only:
        logger.warning(f"Strategy {strategy_id} in DB but not Redis, syncing...")
        await sync_strategy_to_redis(db, strategy_id)
    
    # Remove Redis-only strategies (orphaned)
    for strategy_id in redis_only:
        logger.warning(f"Strategy {strategy_id} in Redis but not DB, removing...")
        # Find user_id from Redis data
        for s in redis_strategies:
            if s["id"] == strategy_id:
                await remove_active_strategy(strategy_id, s["user_id"])
                break
    
    logger.info(f"Reconciliation complete. DB-only: {len(db_only)}, Redis-only: {len(redis_only)}")
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-053: Add Redis Health Monitoring Endpoint

**File**: `backend/app/api/health.py`

**Description**: Add Redis health monitoring endpoint `/health/redis`.

**Acceptance Criteria**:
- [ ] Check Redis connectivity
- [ ] Measure response latency
- [ ] Check memory usage
- [ ] Return health status
- [ ] Include connected clients count

**Code Reference**:
```python
from fastapi import APIRouter
from app.services.redis_service import get_redis
import time

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/redis")
async def redis_health():
    """Check Redis health status"""
    redis = await get_redis()
    
    start = time.time()
    
    try:
        # Ping test
        await redis.client.ping()
        latency_ms = (time.time() - start) * 1000
        
        # Get server info
        info = await redis.client.info()
        
        return {
            "status": "healthy",
            "latency_ms": round(latency_ms, 2),
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "unknown"),
            "uptime_in_seconds": info.get("uptime_in_seconds", 0),
            "redis_version": info.get("redis_version", "unknown")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-054: Write Redis Integration Tests

**File**: `backend/tests/test_redis.py`

**Description**: Write integration tests for Redis operations with test Redis instance.

**Acceptance Criteria**:
- [ ] Test connection and health check
- [ ] Test set/get active strategy
- [ ] Test update strategy state
- [ ] Test remove strategy
- [ ] Test distributed locking
- [ ] Test pub/sub events
- [ ] Test state synchronization
- [ ] Use test Redis instance (separate DB)

**Code Reference**:
```python
import pytest
import json
from app.services.redis_service import (
    get_redis,
    set_active_strategy,
    get_active_strategy,
    update_strategy_state,
    remove_active_strategy,
    get_all_active_strategies,
    acquire_order_lock,
    LockAcquisitionError,
    publish_event,
    EventType
)

@pytest.fixture
async def redis_service():
    """Get Redis service for tests"""
    redis = await get_redis()
    yield redis
    # Cleanup test keys
    async for key in redis.client.scan_iter(match="user:test_*"):
        await redis.delete(key)

@pytest.fixture
def test_strategy_data():
    return {
        "id": "str_test123",
        "user_id": "usr_test456",
        "symbol": "RELIANCE",
        "buy_time": "09:30:00",
        "sell_time": "15:00:00",
        "stop_loss": "2500.00",
        "quantity": 10,
        "status": "RUNNING",
        "position": "NONE"
    }

@pytest.mark.asyncio
async def test_redis_health(redis_service):
    """Test Redis health check"""
    is_healthy = await redis_service.health_check()
    assert is_healthy is True

@pytest.mark.asyncio
async def test_set_and_get_strategy(redis_service, test_strategy_data):
    """Test storing and retrieving strategy"""
    # Set
    success = await set_active_strategy(
        test_strategy_data["id"],
        test_strategy_data
    )
    assert success is True
    
    # Get
    data = await get_active_strategy(
        test_strategy_data["id"],
        test_strategy_data["user_id"]
    )
    assert data is not None
    assert data["id"] == test_strategy_data["id"]
    assert data["symbol"] == test_strategy_data["symbol"]

@pytest.mark.asyncio
async def test_update_strategy_state(redis_service, test_strategy_data):
    """Test updating strategy state"""
    # Set initial
    await set_active_strategy(test_strategy_data["id"], test_strategy_data)
    
    # Update
    success = await update_strategy_state(
        test_strategy_data["id"],
        test_strategy_data["user_id"],
        {"position": "BOUGHT", "entry_price": "2600.00"}
    )
    assert success is True
    
    # Verify
    data = await get_active_strategy(
        test_strategy_data["id"],
        test_strategy_data["user_id"]
    )
    assert data["position"] == "BOUGHT"
    assert data["entry_price"] == "2600.00"

@pytest.mark.asyncio
async def test_remove_strategy(redis_service, test_strategy_data):
    """Test removing strategy"""
    # Set
    await set_active_strategy(test_strategy_data["id"], test_strategy_data)
    
    # Remove
    success = await remove_active_strategy(
        test_strategy_data["id"],
        test_strategy_data["user_id"]
    )
    assert success is True
    
    # Verify removed
    data = await get_active_strategy(
        test_strategy_data["id"],
        test_strategy_data["user_id"]
    )
    assert data is None

@pytest.mark.asyncio
async def test_distributed_lock():
    """Test distributed locking"""
    strategy_id = "str_lock_test"
    action = "BUY"
    
    # Acquire lock
    async with acquire_order_lock(strategy_id, action) as lock:
        assert lock.acquired is True
        
        # Try to acquire again - should fail
        with pytest.raises(LockAcquisitionError):
            async with acquire_order_lock(strategy_id, action):
                pass
    
    # Lock released, can acquire again
    async with acquire_order_lock(strategy_id, action) as lock:
        assert lock.acquired is True

@pytest.mark.asyncio
async def test_get_all_active_strategies(redis_service):
    """Test getting all active strategies"""
    # Set multiple strategies
    for i in range(3):
        await set_active_strategy(f"str_test_{i}", {
            "id": f"str_test_{i}",
            "user_id": f"usr_test_{i}",
            "symbol": "INFY",
            "status": "RUNNING"
        })
    
    # Get all
    strategies = await get_all_active_strategies()
    test_strategies = [s for s in strategies if s["id"].startswith("str_test_")]
    assert len(test_strategies) >= 3
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/app/services/redis_service.py` | Create | Redis service with all operations |
| `backend/app/api/health.py` | Modify | Add Redis health endpoint |
| `backend/tests/test_redis.py` | Create | Redis integration tests |

---

## Environment Variables Required

```bash
# Redis Configuration
REDIS_URL="redis://localhost:6379/0"
```

---

## Definition of Done

- [ ] All 12 tasks completed
- [ ] All integration tests passing
- [ ] Redis operations are performant (< 1ms)
- [ ] Pub/sub events working
- [ ] Distributed locking working
- [ ] Health check endpoint working
- [ ] Code reviewed and approved

---

## Next Phase

After completing Phase 4, proceed to [Phase 5: Scheduler Service](./phase-05-scheduler-service.md)
