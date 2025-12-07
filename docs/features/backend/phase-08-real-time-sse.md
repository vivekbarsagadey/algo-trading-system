---
goal: Phase 8 - Real-Time Status Updates via Server-Sent Events (SSE)
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Backend Engineering Team
status: Planned
tags: [backend, sse, real-time, events, streaming]
---

# Phase 8: Real-Time Status & SSE

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

## Goal

**GOAL-008**: Implement Server-Sent Events (SSE) for real-time strategy status updates

## Overview

This phase implements SSE endpoints for streaming real-time updates to frontend clients. SSE provides a persistent, one-way connection from server to client, enabling instant updates for strategy status changes, order executions, stop-loss triggers, and price updates.

---

## Prerequisites

- Phase 1-7 completed
- Redis Pub/Sub configured
- Event types defined

## Dependencies

```txt
sse-starlette>=1.0.0
```

---

## Implementation Tasks

### TASK-085: Create SSE Manager

**File**: `backend/app/services/sse_manager.py`

**Description**: Create SSEManager to handle SSE connections and broadcast events.

**Acceptance Criteria**:
- [ ] Manage client connections
- [ ] Subscribe to Redis Pub/Sub
- [ ] Broadcast events to clients
- [ ] Handle connection lifecycle
- [ ] Support user-specific channels

**Code Reference**:
```python
from typing import Dict, Set
import asyncio
import json
import logging
from asyncio import Queue

logger = logging.getLogger(__name__)

class SSEManager:
    """Manages SSE connections and event broadcasting"""
    
    def __init__(self):
        # user_id -> set of client queues
        self.clients: Dict[str, Set[Queue]] = {}
        self._redis_listener_task = None
    
    async def connect(self, user_id: str) -> Queue:
        """Connect a new SSE client"""
        queue = Queue()
        
        if user_id not in self.clients:
            self.clients[user_id] = set()
        
        self.clients[user_id].add(queue)
        
        logger.info(f"SSE client connected for user {user_id}, total: {len(self.clients[user_id])}")
        
        # Start Redis listener if not running
        if self._redis_listener_task is None:
            self._redis_listener_task = asyncio.create_task(self._redis_listener())
        
        return queue
    
    async def disconnect(self, user_id: str, queue: Queue):
        """Disconnect an SSE client"""
        if user_id in self.clients:
            self.clients[user_id].discard(queue)
            
            if not self.clients[user_id]:
                del self.clients[user_id]
        
        logger.info(f"SSE client disconnected for user {user_id}")
    
    async def broadcast_to_user(self, user_id: str, event: dict):
        """Broadcast event to all clients of a user"""
        if user_id not in self.clients:
            return
        
        for queue in self.clients[user_id]:
            try:
                await queue.put(event)
            except Exception as e:
                logger.error(f"Failed to broadcast to client: {e}")
    
    async def broadcast_to_all(self, event: dict):
        """Broadcast event to all connected clients"""
        for user_id in self.clients:
            await self.broadcast_to_user(user_id, event)
    
    async def _redis_listener(self):
        """Listen to Redis Pub/Sub for events"""
        from app.services.redis_service import get_redis
        
        redis = await get_redis()
        
        # Subscribe to all user event channels
        pubsub = redis.client.pubsub()
        await pubsub.psubscribe("events:*")
        
        logger.info("SSE Redis listener started")
        
        try:
            async for message in pubsub.listen():
                if message["type"] == "pmessage":
                    channel = message["channel"]
                    data = message["data"]
                    
                    # Extract user_id from channel (events:{user_id})
                    user_id = channel.split(":")[1]
                    
                    try:
                        event = json.loads(data)
                        await self.broadcast_to_user(user_id, event)
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON in event: {data}")
        
        except Exception as e:
            logger.error(f"Redis listener error: {e}")
        
        finally:
            await pubsub.punsubscribe("events:*")
    
    def get_connection_count(self, user_id: str = None) -> int:
        """Get number of active connections"""
        if user_id:
            return len(self.clients.get(user_id, set()))
        return sum(len(clients) for clients in self.clients.values())
    
    async def shutdown(self):
        """Shutdown SSE manager"""
        if self._redis_listener_task:
            self._redis_listener_task.cancel()
            self._redis_listener_task = None
        
        # Close all client connections
        for user_id, queues in self.clients.items():
            for queue in queues:
                await queue.put(None)  # Signal to close
        
        self.clients.clear()
        logger.info("SSE manager shutdown complete")

# Singleton
_sse_manager: SSEManager = None

def get_sse_manager() -> SSEManager:
    global _sse_manager
    if _sse_manager is None:
        _sse_manager = SSEManager()
    return _sse_manager
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-086: Create SSE Endpoint for Strategy Updates

**File**: `backend/app/api/sse.py`

**Description**: Create SSE endpoint `/sse/strategies` for streaming strategy updates.

**Acceptance Criteria**:
- [ ] Persistent SSE connection
- [ ] Authenticate user
- [ ] Stream strategy events
- [ ] Handle disconnection gracefully
- [ ] Support reconnection

**Code Reference**:
```python
from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse
from typing import AsyncGenerator
import asyncio
import json

from app.api.auth import get_current_user
from app.models.user import User
from app.services.sse_manager import get_sse_manager

router = APIRouter(prefix="/sse", tags=["SSE"])

async def event_generator(
    request: Request,
    user_id: str
) -> AsyncGenerator[dict, None]:
    """Generate SSE events for a user"""
    sse_manager = get_sse_manager()
    queue = await sse_manager.connect(user_id)
    
    try:
        # Send initial connection event
        yield {
            "event": "connected",
            "data": json.dumps({
                "message": "SSE connection established",
                "user_id": user_id
            })
        }
        
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                break
            
            try:
                # Wait for event with timeout (for keep-alive)
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                
                if event is None:  # Shutdown signal
                    break
                
                yield {
                    "event": event.get("type", "update"),
                    "data": json.dumps(event)
                }
                
            except asyncio.TimeoutError:
                # Send keep-alive ping
                yield {
                    "event": "ping",
                    "data": json.dumps({"timestamp": datetime.utcnow().isoformat()})
                }
    
    finally:
        await sse_manager.disconnect(user_id, queue)

@router.get("/strategies")
async def strategy_updates(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """SSE endpoint for strategy updates"""
    return EventSourceResponse(
        event_generator(request, current_user.id),
        media_type="text/event-stream"
    )
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-087: Create SSE Endpoint for Specific Strategy

**File**: `backend/app/api/sse.py`

**Description**: Create SSE endpoint `/sse/strategy/{strategy_id}` for single strategy updates.

**Acceptance Criteria**:
- [ ] Filter events for specific strategy
- [ ] Validate strategy ownership
- [ ] Include price updates for strategy symbol
- [ ] Stream order events

**Code Reference**:
```python
async def strategy_event_generator(
    request: Request,
    user_id: str,
    strategy_id: str
) -> AsyncGenerator[dict, None]:
    """Generate SSE events for a specific strategy"""
    from app.services.redis_service import get_active_strategy
    
    # Verify strategy ownership
    strategy = await get_active_strategy(strategy_id, user_id)
    if not strategy:
        yield {
            "event": "error",
            "data": json.dumps({"error": "Strategy not found"})
        }
        return
    
    sse_manager = get_sse_manager()
    queue = await sse_manager.connect(user_id)
    
    try:
        # Send initial strategy state
        yield {
            "event": "initial_state",
            "data": json.dumps(strategy)
        }
        
        while True:
            if await request.is_disconnected():
                break
            
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                
                if event is None:
                    break
                
                # Filter: only events for this strategy
                if event.get("data", {}).get("strategy_id") == strategy_id:
                    yield {
                        "event": event.get("type", "update"),
                        "data": json.dumps(event)
                    }
                
            except asyncio.TimeoutError:
                # Send keep-alive with current strategy state
                strategy = await get_active_strategy(strategy_id, user_id)
                yield {
                    "event": "state_update",
                    "data": json.dumps(strategy) if strategy else "{}"
                }
    
    finally:
        await sse_manager.disconnect(user_id, queue)

@router.get("/strategy/{strategy_id}")
async def single_strategy_updates(
    strategy_id: str,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """SSE endpoint for single strategy updates"""
    return EventSourceResponse(
        strategy_event_generator(request, current_user.id, strategy_id),
        media_type="text/event-stream"
    )
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-088: Create SSE Endpoint for Price Updates

**File**: `backend/app/api/sse.py`

**Description**: Create SSE endpoint `/sse/prices` for streaming real-time price updates.

**Acceptance Criteria**:
- [ ] Stream LTP updates
- [ ] Support symbol filtering
- [ ] Throttle updates (max 10/sec)
- [ ] Batch updates for efficiency

**Code Reference**:
```python
from collections import defaultdict
from datetime import datetime
import time

class PriceThrottler:
    """Throttles price updates to avoid overwhelming clients"""
    
    def __init__(self, max_updates_per_second: int = 10):
        self.max_updates = max_updates_per_second
        self.last_update: Dict[str, float] = {}
        self.min_interval = 1.0 / max_updates_per_second
    
    def should_update(self, symbol: str) -> bool:
        """Check if update should be sent"""
        now = time.time()
        last = self.last_update.get(symbol, 0)
        
        if now - last >= self.min_interval:
            self.last_update[symbol] = now
            return True
        return False

async def price_event_generator(
    request: Request,
    user_id: str,
    symbols: List[str]
) -> AsyncGenerator[dict, None]:
    """Generate price update events"""
    from app.services.redis_service import get_redis
    
    redis = await get_redis()
    throttler = PriceThrottler(max_updates_per_second=10)
    
    # Subscribe to price channels
    pubsub = redis.client.pubsub()
    for symbol in symbols:
        await pubsub.subscribe(f"prices:{symbol}")
    
    try:
        yield {
            "event": "subscribed",
            "data": json.dumps({"symbols": symbols})
        }
        
        while True:
            if await request.is_disconnected():
                break
            
            try:
                message = await asyncio.wait_for(
                    pubsub.get_message(ignore_subscribe_messages=True),
                    timeout=5.0
                )
                
                if message:
                    channel = message["channel"]
                    symbol = channel.split(":")[1]
                    
                    if throttler.should_update(symbol):
                        yield {
                            "event": "price",
                            "data": message["data"]
                        }
                else:
                    # Keep-alive
                    yield {
                        "event": "ping",
                        "data": json.dumps({"timestamp": datetime.utcnow().isoformat()})
                    }
                    
            except asyncio.TimeoutError:
                # Send keep-alive
                yield {
                    "event": "ping",
                    "data": json.dumps({"timestamp": datetime.utcnow().isoformat()})
                }
    
    finally:
        for symbol in symbols:
            await pubsub.unsubscribe(f"prices:{symbol}")

@router.get("/prices")
async def price_updates(
    request: Request,
    symbols: str,  # Comma-separated list
    current_user: User = Depends(get_current_user)
):
    """SSE endpoint for price updates"""
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    
    return EventSourceResponse(
        price_event_generator(request, current_user.id, symbol_list),
        media_type="text/event-stream"
    )
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-089: Define Event Types and Schemas

**File**: `backend/app/schemas/events.py`

**Description**: Define standard event types and their schemas for SSE.

**Acceptance Criteria**:
- [ ] All event types documented
- [ ] Pydantic schemas for each
- [ ] Consistent structure
- [ ] Timestamp in all events
- [ ] Event type enum

**Code Reference**:
```python
from pydantic import BaseModel
from typing import Optional, Any
from enum import Enum
from datetime import datetime

class EventType(str, Enum):
    # Strategy Events
    STRATEGY_STARTED = "STRATEGY_STARTED"
    STRATEGY_STOPPED = "STRATEGY_STOPPED"
    STRATEGY_UPDATED = "STRATEGY_UPDATED"
    STRATEGY_ERROR = "STRATEGY_ERROR"
    STRATEGY_COMPLETED = "STRATEGY_COMPLETED"
    
    # Order Events
    ORDER_PLACED = "ORDER_PLACED"
    ORDER_EXECUTED = "ORDER_EXECUTED"
    ORDER_REJECTED = "ORDER_REJECTED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    ORDER_FAILED = "ORDER_FAILED"
    
    # Stop-Loss Events
    SL_TRIGGERED = "SL_TRIGGERED"
    SL_EXECUTED = "SL_EXECUTED"
    
    # Price Events
    PRICE_UPDATE = "PRICE_UPDATE"
    
    # System Events
    CONNECTED = "CONNECTED"
    PING = "PING"
    ERROR = "ERROR"

class BaseEvent(BaseModel):
    type: EventType
    timestamp: datetime = None
    
    def __init__(self, **data):
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow()
        super().__init__(**data)

class StrategyEvent(BaseEvent):
    strategy_id: str
    user_id: str
    status: Optional[str] = None
    position: Optional[str] = None
    message: Optional[str] = None

class OrderEvent(BaseEvent):
    strategy_id: str
    order_id: str
    order_type: str  # BUY, SELL, SL_SELL
    symbol: str
    quantity: int
    price: Optional[float] = None
    status: str

class StopLossEvent(BaseEvent):
    strategy_id: str
    trigger_price: float
    current_price: float
    order_id: Optional[str] = None

class PriceEvent(BaseEvent):
    symbol: str
    ltp: float
    change: Optional[float] = None
    change_percent: Optional[float] = None

class ErrorEvent(BaseEvent):
    strategy_id: Optional[str] = None
    error_code: str
    error_message: str
    details: Optional[dict] = None

# Event factory
def create_event(event_type: EventType, **kwargs) -> BaseEvent:
    """Create typed event based on event type"""
    event_classes = {
        EventType.STRATEGY_STARTED: StrategyEvent,
        EventType.STRATEGY_STOPPED: StrategyEvent,
        EventType.STRATEGY_UPDATED: StrategyEvent,
        EventType.ORDER_PLACED: OrderEvent,
        EventType.ORDER_EXECUTED: OrderEvent,
        EventType.SL_TRIGGERED: StopLossEvent,
        EventType.PRICE_UPDATE: PriceEvent,
        EventType.ERROR: ErrorEvent,
    }
    
    event_class = event_classes.get(event_type, BaseEvent)
    return event_class(type=event_type, **kwargs)
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-090: Implement Event Publishing Helpers

**File**: `backend/app/services/event_publisher.py`

**Description**: Create helper functions for publishing events from various parts of the system.

**Acceptance Criteria**:
- [ ] Easy-to-use event publishing
- [ ] Consistent event formatting
- [ ] Async publishing
- [ ] Error handling
- [ ] Logging

**Code Reference**:
```python
from app.services.redis_service import get_redis, RedisKeys
from app.schemas.events import EventType, create_event
import json
import logging

logger = logging.getLogger(__name__)

class EventPublisher:
    """Publishes events to Redis Pub/Sub for SSE distribution"""
    
    async def publish(self, user_id: str, event_type: EventType, **kwargs):
        """Publish event to user's channel"""
        redis = await get_redis()
        
        event = create_event(event_type, **kwargs)
        channel = RedisKeys.user_events(user_id)
        
        await redis.publish(channel, event.json())
        logger.debug(f"Published {event_type} to {channel}")
    
    async def publish_strategy_started(
        self,
        user_id: str,
        strategy_id: str,
        status: str = "RUNNING"
    ):
        """Publish strategy started event"""
        await self.publish(
            user_id,
            EventType.STRATEGY_STARTED,
            strategy_id=strategy_id,
            user_id=user_id,
            status=status,
            message="Strategy started successfully"
        )
    
    async def publish_strategy_stopped(
        self,
        user_id: str,
        strategy_id: str,
        reason: str = None
    ):
        """Publish strategy stopped event"""
        await self.publish(
            user_id,
            EventType.STRATEGY_STOPPED,
            strategy_id=strategy_id,
            user_id=user_id,
            status="STOPPED",
            message=reason or "Strategy stopped"
        )
    
    async def publish_order_executed(
        self,
        user_id: str,
        strategy_id: str,
        order_id: str,
        order_type: str,
        symbol: str,
        quantity: int,
        price: float
    ):
        """Publish order executed event"""
        await self.publish(
            user_id,
            EventType.ORDER_EXECUTED,
            strategy_id=strategy_id,
            order_id=order_id,
            order_type=order_type,
            symbol=symbol,
            quantity=quantity,
            price=price,
            status="EXECUTED"
        )
    
    async def publish_sl_triggered(
        self,
        user_id: str,
        strategy_id: str,
        trigger_price: float,
        current_price: float
    ):
        """Publish stop-loss triggered event"""
        await self.publish(
            user_id,
            EventType.SL_TRIGGERED,
            strategy_id=strategy_id,
            trigger_price=trigger_price,
            current_price=current_price
        )
    
    async def publish_error(
        self,
        user_id: str,
        error_code: str,
        error_message: str,
        strategy_id: str = None,
        details: dict = None
    ):
        """Publish error event"""
        await self.publish(
            user_id,
            EventType.ERROR,
            error_code=error_code,
            error_message=error_message,
            strategy_id=strategy_id,
            details=details
        )
    
    async def publish_price_update(
        self,
        symbol: str,
        ltp: float,
        change: float = None,
        change_percent: float = None
    ):
        """Publish price update to symbol channel"""
        redis = await get_redis()
        
        event = create_event(
            EventType.PRICE_UPDATE,
            symbol=symbol,
            ltp=ltp,
            change=change,
            change_percent=change_percent
        )
        
        channel = f"prices:{symbol}"
        await redis.publish(channel, event.json())

# Singleton
_event_publisher: EventPublisher = None

def get_event_publisher() -> EventPublisher:
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-091: Add SSE Connection Health Monitoring

**File**: `backend/app/api/health.py`

**Description**: Add health monitoring endpoint for SSE connections.

**Acceptance Criteria**:
- [ ] Show active connection count
- [ ] Show connections per user
- [ ] Show Redis listener status
- [ ] Include in overall health check

**Code Reference**:
```python
@router.get("/sse")
async def sse_health():
    """Check SSE connection health"""
    from app.services.sse_manager import get_sse_manager
    
    sse_manager = get_sse_manager()
    
    total_connections = sse_manager.get_connection_count()
    per_user = {
        user_id: len(queues)
        for user_id, queues in sse_manager.clients.items()
    }
    
    return {
        "status": "healthy",
        "total_connections": total_connections,
        "connections_per_user": per_user,
        "redis_listener_active": sse_manager._redis_listener_task is not None
    }
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-092: Implement SSE Reconnection Support

**File**: `backend/app/api/sse.py`

**Description**: Implement Last-Event-ID support for SSE reconnection.

**Acceptance Criteria**:
- [ ] Accept Last-Event-ID header
- [ ] Store recent events in Redis
- [ ] Replay missed events on reconnect
- [ ] Event ID format
- [ ] TTL for event history

**Code Reference**:
```python
from typing import Optional
import uuid

EVENT_HISTORY_TTL = 300  # 5 minutes
EVENT_HISTORY_KEY = "sse:history:{user_id}"

class EventHistory:
    """Stores recent events for reconnection support"""
    
    async def store_event(self, user_id: str, event: dict) -> str:
        """Store event and return event ID"""
        redis = await get_redis()
        
        event_id = f"{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"
        event["id"] = event_id
        
        key = EVENT_HISTORY_KEY.format(user_id=user_id)
        
        # Add to sorted set with timestamp as score
        await redis.client.zadd(
            key,
            {json.dumps(event): time.time()}
        )
        
        # Trim old events
        await redis.client.zremrangebyscore(
            key,
            "-inf",
            time.time() - EVENT_HISTORY_TTL
        )
        
        return event_id
    
    async def get_events_after(
        self,
        user_id: str,
        last_event_id: str
    ) -> List[dict]:
        """Get events after the given event ID"""
        redis = await get_redis()
        key = EVENT_HISTORY_KEY.format(user_id=user_id)
        
        # Parse timestamp from event ID
        try:
            timestamp = int(last_event_id.split("-")[0]) / 1000
        except (ValueError, IndexError):
            return []
        
        # Get events after timestamp
        events = await redis.client.zrangebyscore(
            key,
            timestamp,
            "+inf"
        )
        
        return [json.loads(e) for e in events]

# Modified event generator with reconnection support
async def event_generator_with_reconnect(
    request: Request,
    user_id: str,
    last_event_id: Optional[str] = None
) -> AsyncGenerator[dict, None]:
    """Generate SSE events with reconnection support"""
    sse_manager = get_sse_manager()
    event_history = EventHistory()
    queue = await sse_manager.connect(user_id)
    
    try:
        # Replay missed events on reconnect
        if last_event_id:
            missed_events = await event_history.get_events_after(
                user_id,
                last_event_id
            )
            for event in missed_events:
                yield {
                    "id": event.get("id"),
                    "event": event.get("type", "update"),
                    "data": json.dumps(event)
                }
        
        # Continue with normal event streaming
        yield {
            "event": "connected",
            "data": json.dumps({"message": "Connected"})
        }
        
        while True:
            if await request.is_disconnected():
                break
            
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                
                if event is None:
                    break
                
                # Store event for reconnection
                event_id = await event_history.store_event(user_id, event)
                
                yield {
                    "id": event_id,
                    "event": event.get("type", "update"),
                    "data": json.dumps(event)
                }
                
            except asyncio.TimeoutError:
                yield {"event": "ping", "data": "{}"}
    
    finally:
        await sse_manager.disconnect(user_id, queue)

@router.get("/strategies/reconnect")
async def strategy_updates_with_reconnect(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """SSE endpoint with reconnection support"""
    last_event_id = request.headers.get("Last-Event-ID")
    
    return EventSourceResponse(
        event_generator_with_reconnect(
            request,
            current_user.id,
            last_event_id
        ),
        media_type="text/event-stream"
    )
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-093: Write SSE Integration Tests

**File**: `backend/tests/test_sse.py`

**Description**: Write integration tests for SSE endpoints.

**Acceptance Criteria**:
- [ ] Test SSE connection
- [ ] Test event broadcasting
- [ ] Test reconnection
- [ ] Test event filtering
- [ ] Test price updates
- [ ] Mock Redis Pub/Sub

**Code Reference**:
```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from httpx import AsyncClient
from app.main import app
from app.services.sse_manager import SSEManager, get_sse_manager
from app.services.event_publisher import get_event_publisher

class TestSSEManager:
    
    @pytest.fixture
    def sse_manager(self):
        return SSEManager()
    
    @pytest.mark.asyncio
    async def test_connect_creates_queue(self, sse_manager):
        """Test connecting creates a queue for user"""
        queue = await sse_manager.connect("usr_123")
        
        assert queue is not None
        assert "usr_123" in sse_manager.clients
        assert queue in sse_manager.clients["usr_123"]
    
    @pytest.mark.asyncio
    async def test_disconnect_removes_queue(self, sse_manager):
        """Test disconnecting removes the queue"""
        queue = await sse_manager.connect("usr_123")
        await sse_manager.disconnect("usr_123", queue)
        
        assert "usr_123" not in sse_manager.clients
    
    @pytest.mark.asyncio
    async def test_broadcast_to_user(self, sse_manager):
        """Test broadcasting sends to all user clients"""
        queue1 = await sse_manager.connect("usr_123")
        queue2 = await sse_manager.connect("usr_123")
        
        event = {"type": "TEST", "data": "hello"}
        await sse_manager.broadcast_to_user("usr_123", event)
        
        # Both queues should have the event
        assert await queue1.get() == event
        assert await queue2.get() == event

class TestSSEEndpoints:
    
    @pytest.fixture
    async def client(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture
    def auth_headers(self, test_user_token):
        return {"Authorization": f"Bearer {test_user_token}"}
    
    @pytest.mark.asyncio
    async def test_strategies_endpoint(self, client, auth_headers):
        """Test SSE strategies endpoint connects"""
        async with client.stream(
            "GET",
            "/sse/strategies",
            headers=auth_headers
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream"
            
            # Read first event (connected)
            async for line in response.aiter_lines():
                if line.startswith("event:"):
                    assert "connected" in line
                    break

class TestEventPublisher:
    
    @pytest.mark.asyncio
    async def test_publish_strategy_started(self):
        """Test publishing strategy started event"""
        publisher = get_event_publisher()
        
        with patch("app.services.event_publisher.get_redis") as mock_redis:
            mock_redis.return_value = AsyncMock()
            
            await publisher.publish_strategy_started(
                "usr_123",
                "str_456",
                "RUNNING"
            )
            
            mock_redis.return_value.publish.assert_called_once()
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/app/services/sse_manager.py` | Create | SSE connection manager |
| `backend/app/api/sse.py` | Create | SSE endpoints |
| `backend/app/schemas/events.py` | Create | Event schemas |
| `backend/app/services/event_publisher.py` | Create | Event publishing helpers |
| `backend/app/api/health.py` | Modify | Add SSE health check |
| `backend/app/main.py` | Modify | Add SSE router |
| `backend/tests/test_sse.py` | Create | Integration tests |

---

## Environment Variables Required

```bash
# SSE Configuration
SSE_KEEPALIVE_INTERVAL=30
SSE_EVENT_HISTORY_TTL=300
```

---

## Definition of Done

- [ ] All 9 tasks completed
- [ ] SSE endpoints functional
- [ ] Events broadcast correctly
- [ ] Reconnection working
- [ ] Price updates streaming
- [ ] Health monitoring working
- [ ] Integration tests passing
- [ ] Code reviewed and approved

---

## Next Phase

After completing Phase 8, proceed to [Phase 9: Admin APIs](./phase-09-admin-apis.md)
