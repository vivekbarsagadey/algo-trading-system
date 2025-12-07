---
goal: Phase 3 - Strategy Management Module
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Backend Engineering Team
status: Planned
tags: [backend, strategy, crud, validation, stop-loss]
---

# Phase 3: Strategy Management Module

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

## Goal

**GOAL-003**: Implement strategy CRUD operations with mandatory stop-loss validation

## Overview

This phase implements the core strategy management functionality. Users can create, read, update, and delete trading strategies. Every strategy requires a mandatory stop-loss for safety. Strategies can be started/stopped and their status monitored in real-time.

---

## Prerequisites

- Phase 1 (Authentication) completed
- Phase 2 (Broker Integration) completed
- User can authenticate and has broker connected

## Dependencies

```txt
pydantic>=2.0.0
sqlalchemy>=2.0.0
```

---

## Implementation Tasks

### TASK-028: Create Strategy SQLAlchemy Model

**File**: `backend/app/models/strategy.py`

**Description**: Create Strategy SQLAlchemy model with all required fields for time-based trading strategies.

**Acceptance Criteria**:
- [ ] `id` - String primary key with `str_` prefix
- [ ] `user_id` - Foreign key to users table, indexed
- [ ] `symbol` - String, trading symbol (e.g., "RELIANCE", "INFY")
- [ ] `buy_time` - Time, when to execute BUY order
- [ ] `sell_time` - Time, when to execute SELL order
- [ ] `stop_loss` - Decimal, mandatory stop-loss price
- [ ] `quantity` - Integer, number of shares
- [ ] `status` - Enum (CREATED, RUNNING, STOPPED, COMPLETED, ERROR)
- [ ] `position` - Enum (NONE, BOUGHT, SOLD, SL_HIT)
- [ ] `last_action` - String, last executed action
- [ ] `entry_price` - Decimal, nullable, actual buy price
- [ ] `exit_price` - Decimal, nullable, actual sell price
- [ ] `created_at` - DateTime
- [ ] `updated_at` - DateTime
- [ ] Index on (user_id, status) for efficient queries

**Code Reference**:
```python
from sqlalchemy import Column, String, Integer, Numeric, Time, DateTime, ForeignKey, Enum, Index
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import enum

def generate_strategy_id() -> str:
    return f"str_{uuid.uuid4().hex[:12]}"

class StrategyStatus(str, enum.Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"

class PositionStatus(str, enum.Enum):
    NONE = "NONE"
    BOUGHT = "BOUGHT"
    SOLD = "SOLD"
    SL_HIT = "SL_HIT"

class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(String(50), primary_key=True, default=generate_strategy_id)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    symbol = Column(String(50), nullable=False)
    buy_time = Column(Time, nullable=False)
    sell_time = Column(Time, nullable=False)
    stop_loss = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(
        Enum(StrategyStatus),
        default=StrategyStatus.CREATED,
        nullable=False
    )
    position = Column(
        Enum(PositionStatus),
        default=PositionStatus.NONE,
        nullable=False
    )
    last_action = Column(String(100), nullable=True)
    entry_price = Column(Numeric(10, 2), nullable=True)
    exit_price = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_strategies_user_status', 'user_id', 'status'),
        Index('idx_strategies_status', 'status'),
    )
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-029: Create Strategy POST Endpoint

**File**: `backend/app/api/strategies.py`

**Description**: Create `/strategies` POST endpoint with validation for mandatory stop_loss, buy_time < sell_time, quantity > 0, and valid symbol format.

**Acceptance Criteria**:
- [ ] Accepts symbol, buy_time, sell_time, stop_loss, quantity
- [ ] Validates stop_loss is provided (mandatory)
- [ ] Validates buy_time < sell_time
- [ ] Validates quantity > 0
- [ ] Validates symbol format (alphanumeric, max 20 chars)
- [ ] Creates strategy with CREATED status
- [ ] Returns created strategy with ID
- [ ] Associates strategy with current user

**Code Reference**:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from datetime import time
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.models.strategy import Strategy, StrategyStatus, PositionStatus
from app.services.strategy_service import create_strategy

router = APIRouter(prefix="/strategies", tags=["Strategies"])

class StrategyCreateRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20, pattern=r'^[A-Za-z0-9]+$')
    buy_time: time
    sell_time: time
    stop_loss: Decimal = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    
    @field_validator('sell_time')
    @classmethod
    def validate_sell_time(cls, v, info):
        buy_time = info.data.get('buy_time')
        if buy_time and v <= buy_time:
            raise ValueError('sell_time must be after buy_time')
        return v

class StrategyResponse(BaseModel):
    id: str
    user_id: str
    symbol: str
    buy_time: time
    sell_time: time
    stop_loss: Decimal
    quantity: int
    status: str
    position: str
    last_action: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy_endpoint(
    request: StrategyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new trading strategy"""
    
    # Additional validation for market hours
    market_open = time(9, 15)
    market_close = time(15, 30)
    
    if request.buy_time < market_open or request.buy_time > market_close:
        raise HTTPException(
            status_code=400,
            detail="buy_time must be within market hours (9:15 AM - 3:30 PM)"
        )
    
    if request.sell_time < market_open or request.sell_time > market_close:
        raise HTTPException(
            status_code=400,
            detail="sell_time must be within market hours (9:15 AM - 3:30 PM)"
        )
    
    strategy = await create_strategy(
        db=db,
        user_id=current_user.id,
        symbol=request.symbol.upper(),
        buy_time=request.buy_time,
        sell_time=request.sell_time,
        stop_loss=request.stop_loss,
        quantity=request.quantity
    )
    
    return strategy
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-030: Create Strategy List GET Endpoint

**File**: `backend/app/api/strategies.py`

**Description**: Add `/strategies` GET endpoint with pagination, filtering by status, and sorting options.

**Acceptance Criteria**:
- [ ] Returns paginated list of user's strategies
- [ ] Query params: page, limit, status, sort_by, order
- [ ] Default pagination: page=1, limit=20
- [ ] Filter by status (optional)
- [ ] Sort by created_at (default), symbol, status
- [ ] Order ascending or descending
- [ ] Returns total count for pagination
- [ ] Only returns current user's strategies (multi-tenant)

**Code Reference**:
```python
from typing import Optional, List
from enum import Enum

class SortBy(str, Enum):
    created_at = "created_at"
    symbol = "symbol"
    status = "status"

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

class StrategyListResponse(BaseModel):
    items: List[StrategyResponse]
    total: int
    page: int
    limit: int
    pages: int

@router.get("", response_model=StrategyListResponse)
async def list_strategies(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[StrategyStatus] = None,
    sort_by: SortBy = SortBy.created_at,
    order: SortOrder = SortOrder.desc,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all strategies for current user"""
    
    # Build query
    query = select(Strategy).where(Strategy.user_id == current_user.id)
    
    # Filter by status
    if status:
        query = query.where(Strategy.status == status)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Sort
    sort_column = getattr(Strategy, sort_by.value)
    if order == SortOrder.desc:
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Paginate
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    strategies = result.scalars().all()
    
    return StrategyListResponse(
        items=strategies,
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit
    )
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-031: Create Strategy Detail GET Endpoint

**File**: `backend/app/api/strategies.py`

**Description**: Add `/strategies/{strategy_id}` GET endpoint to fetch single strategy details.

**Acceptance Criteria**:
- [ ] Returns full strategy details
- [ ] Validates user owns the strategy
- [ ] Returns 404 if not found
- [ ] Returns 403 if user doesn't own strategy
- [ ] Includes all fields including entry/exit prices

**Code Reference**:
```python
class StrategyDetailResponse(StrategyResponse):
    entry_price: Optional[Decimal]
    exit_price: Optional[Decimal]
    updated_at: Optional[datetime]

@router.get("/{strategy_id}", response_model=StrategyDetailResponse)
async def get_strategy(
    strategy_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get strategy details by ID"""
    
    result = await db.execute(
        select(Strategy).where(Strategy.id == strategy_id)
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Check ownership
    if strategy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return strategy
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-032: Create Strategy Update PUT Endpoint

**File**: `backend/app/api/strategies.py`

**Description**: Add `/strategies/{strategy_id}` PUT endpoint for strategy updates with ownership validation and conditional field updates.

**Acceptance Criteria**:
- [ ] Validates user owns the strategy
- [ ] Allows updating: stop_loss, sell_time, quantity when STOPPED
- [ ] When RUNNING: only allows stop_loss and sell_time updates
- [ ] Cannot update symbol or buy_time when RUNNING
- [ ] Validates new values (stop_loss > 0, sell_time > current time if running)
- [ ] Returns updated strategy
- [ ] Returns 400 for invalid updates

**Code Reference**:
```python
class StrategyUpdateRequest(BaseModel):
    symbol: Optional[str] = Field(None, min_length=1, max_length=20)
    buy_time: Optional[time] = None
    sell_time: Optional[time] = None
    stop_loss: Optional[Decimal] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, gt=0)

@router.put("/{strategy_id}", response_model=StrategyDetailResponse)
async def update_strategy(
    strategy_id: str,
    request: StrategyUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update strategy parameters"""
    
    result = await db.execute(
        select(Strategy).where(Strategy.id == strategy_id)
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if strategy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check what can be updated based on status
    if strategy.status == StrategyStatus.RUNNING:
        # Only stop_loss and sell_time can be updated when running
        if request.symbol is not None or request.buy_time is not None or request.quantity is not None:
            raise HTTPException(
                status_code=400,
                detail="Cannot update symbol, buy_time, or quantity while strategy is running"
            )
        
        if request.stop_loss is not None:
            strategy.stop_loss = request.stop_loss
        
        if request.sell_time is not None:
            # Validate sell_time is in future
            now = datetime.now().time()
            if request.sell_time <= now:
                raise HTTPException(
                    status_code=400,
                    detail="sell_time must be in the future for running strategy"
                )
            strategy.sell_time = request.sell_time
    
    elif strategy.status == StrategyStatus.CREATED or strategy.status == StrategyStatus.STOPPED:
        # All fields can be updated when stopped
        if request.symbol is not None:
            strategy.symbol = request.symbol.upper()
        if request.buy_time is not None:
            strategy.buy_time = request.buy_time
        if request.sell_time is not None:
            strategy.sell_time = request.sell_time
        if request.stop_loss is not None:
            strategy.stop_loss = request.stop_loss
        if request.quantity is not None:
            strategy.quantity = request.quantity
        
        # Validate buy_time < sell_time
        if strategy.buy_time >= strategy.sell_time:
            raise HTTPException(
                status_code=400,
                detail="sell_time must be after buy_time"
            )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot update strategy with status {strategy.status}"
        )
    
    await db.commit()
    await db.refresh(strategy)
    
    return strategy
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-033: Create Strategy Delete Endpoint

**File**: `backend/app/api/strategies.py`

**Description**: Add `/strategies/{strategy_id}` DELETE endpoint that only allows deletion when strategy is stopped.

**Acceptance Criteria**:
- [ ] Validates user owns the strategy
- [ ] Only allows deletion when status is CREATED, STOPPED, or COMPLETED
- [ ] Returns 400 if trying to delete RUNNING strategy
- [ ] Returns 204 No Content on success
- [ ] Cleans up any related data (order logs kept for audit)

**Code Reference**:
```python
@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a strategy"""
    
    result = await db.execute(
        select(Strategy).where(Strategy.id == strategy_id)
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if strategy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Cannot delete running strategy
    if strategy.status == StrategyStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a running strategy. Stop it first."
        )
    
    await db.delete(strategy)
    await db.commit()
    
    return None
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-034: Create Strategy Start Endpoint

**File**: `backend/app/api/strategies.py`

**Description**: Add `/strategies/{strategy_id}/start` POST endpoint to activate strategy for execution.

**Acceptance Criteria**:
- [ ] Validates user owns the strategy
- [ ] Validates broker is connected
- [ ] Validates strategy is in CREATED or STOPPED status
- [ ] Updates status to RUNNING
- [ ] Stores strategy in Redis for execution engine
- [ ] Schedules buy/sell orders with scheduler
- [ ] Returns updated strategy

**Code Reference**:
```python
from app.services.strategy_service import start_strategy

@router.post("/{strategy_id}/start", response_model=StrategyDetailResponse)
async def start_strategy_endpoint(
    strategy_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a strategy for execution"""
    
    result = await db.execute(
        select(Strategy).where(Strategy.id == strategy_id)
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if strategy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if broker is connected
    broker_result = await db.execute(
        select(BrokerCredential).where(
            BrokerCredential.user_id == current_user.id,
            BrokerCredential.is_valid == True
        )
    )
    broker_cred = broker_result.scalar_one_or_none()
    
    if not broker_cred:
        raise HTTPException(
            status_code=400,
            detail="No valid broker connection. Please connect your broker first."
        )
    
    # Check strategy status
    if strategy.status not in [StrategyStatus.CREATED, StrategyStatus.STOPPED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start strategy with status {strategy.status}"
        )
    
    # Check market hours
    now = datetime.now().time()
    market_open = time(9, 15)
    market_close = time(15, 30)
    
    if now < market_open or now > market_close:
        raise HTTPException(
            status_code=400,
            detail="Strategies can only be started during market hours (9:15 AM - 3:30 PM)"
        )
    
    # Start the strategy
    strategy = await start_strategy(db, strategy_id)
    
    return strategy
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-035: Create Strategy Stop Endpoint

**File**: `backend/app/api/strategies.py`

**Description**: Add `/strategies/{strategy_id}/stop` POST endpoint to immediately deactivate strategy.

**Acceptance Criteria**:
- [ ] Validates user owns the strategy
- [ ] Validates strategy is RUNNING
- [ ] Updates status to STOPPED
- [ ] Removes from Redis
- [ ] Cancels scheduled orders
- [ ] If position is BOUGHT, optionally trigger exit
- [ ] Returns updated strategy

**Code Reference**:
```python
from app.services.strategy_service import stop_strategy

class StopStrategyRequest(BaseModel):
    exit_position: bool = False  # Whether to sell if currently BOUGHT

@router.post("/{strategy_id}/stop", response_model=StrategyDetailResponse)
async def stop_strategy_endpoint(
    strategy_id: str,
    request: StopStrategyRequest = StopStrategyRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stop a running strategy"""
    
    result = await db.execute(
        select(Strategy).where(Strategy.id == strategy_id)
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if strategy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if strategy.status != StrategyStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail=f"Strategy is not running. Current status: {strategy.status}"
        )
    
    # Stop the strategy
    strategy = await stop_strategy(
        db=db,
        strategy_id=strategy_id,
        exit_position=request.exit_position
    )
    
    return strategy
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-036: Create Strategy Status Endpoint

**File**: `backend/app/api/strategies.py`

**Description**: Add `/strategies/{strategy_id}/status` GET endpoint for real-time status polling.

**Acceptance Criteria**:
- [ ] Returns current strategy status
- [ ] Includes position, last_action, entry/exit prices
- [ ] Optimized for frequent polling
- [ ] Reads from Redis if strategy is active
- [ ] Falls back to database
- [ ] Returns last updated timestamp

**Code Reference**:
```python
class StrategyStatusResponse(BaseModel):
    id: str
    status: str
    position: str
    last_action: Optional[str]
    entry_price: Optional[Decimal]
    exit_price: Optional[Decimal]
    current_price: Optional[Decimal]  # From market data
    unrealized_pnl: Optional[Decimal]
    updated_at: datetime

@router.get("/{strategy_id}/status", response_model=StrategyStatusResponse)
async def get_strategy_status(
    strategy_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get real-time strategy status"""
    
    result = await db.execute(
        select(Strategy).where(Strategy.id == strategy_id)
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    if strategy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Try to get from Redis for active strategies
    redis_data = None
    if strategy.status == StrategyStatus.RUNNING:
        redis_data = await get_active_strategy_from_redis(strategy_id)
    
    # Get current price if position is BOUGHT
    current_price = None
    unrealized_pnl = None
    if strategy.position == PositionStatus.BOUGHT and strategy.entry_price:
        try:
            current_price = await get_ltp_from_cache(strategy.symbol)
            if current_price:
                unrealized_pnl = (current_price - strategy.entry_price) * strategy.quantity
        except Exception:
            pass
    
    return StrategyStatusResponse(
        id=strategy.id,
        status=redis_data.get("status", strategy.status) if redis_data else strategy.status,
        position=redis_data.get("position", strategy.position) if redis_data else strategy.position,
        last_action=redis_data.get("last_action", strategy.last_action) if redis_data else strategy.last_action,
        entry_price=strategy.entry_price,
        exit_price=strategy.exit_price,
        current_price=current_price,
        unrealized_pnl=unrealized_pnl,
        updated_at=strategy.updated_at or strategy.created_at
    )
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-037: Create Strategy Service

**File**: `backend/app/services/strategy_service.py`

**Description**: Create strategy service with `create_strategy()`, `update_strategy()`, `start_strategy()`, `stop_strategy()` functions.

**Acceptance Criteria**:
- [ ] `create_strategy(db, user_id, ...)` - creates new strategy
- [ ] `start_strategy(db, strategy_id)` - starts strategy execution
- [ ] `stop_strategy(db, strategy_id, exit_position)` - stops strategy
- [ ] Integrates with Redis service
- [ ] Integrates with Scheduler service
- [ ] All functions are async
- [ ] Proper error handling

**Code Reference**:
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import time
from decimal import Decimal
from app.models.strategy import Strategy, StrategyStatus, PositionStatus
from app.services.redis_service import (
    set_active_strategy,
    remove_active_strategy,
    get_active_strategy
)
from app.services.scheduler_service import (
    schedule_buy_order,
    schedule_sell_order,
    cancel_scheduled_orders
)

async def create_strategy(
    db: AsyncSession,
    user_id: str,
    symbol: str,
    buy_time: time,
    sell_time: time,
    stop_loss: Decimal,
    quantity: int
) -> Strategy:
    """Create a new trading strategy"""
    
    strategy = Strategy(
        user_id=user_id,
        symbol=symbol.upper(),
        buy_time=buy_time,
        sell_time=sell_time,
        stop_loss=stop_loss,
        quantity=quantity,
        status=StrategyStatus.CREATED,
        position=PositionStatus.NONE
    )
    
    db.add(strategy)
    await db.commit()
    await db.refresh(strategy)
    
    return strategy

async def start_strategy(db: AsyncSession, strategy_id: str) -> Strategy:
    """Start a strategy for execution"""
    
    result = await db.execute(
        select(Strategy).where(Strategy.id == strategy_id)
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise ValueError("Strategy not found")
    
    # Update status
    strategy.status = StrategyStatus.RUNNING
    strategy.last_action = "Strategy started"
    
    await db.commit()
    await db.refresh(strategy)
    
    # Store in Redis for execution engine
    await set_active_strategy(strategy_id, {
        "id": strategy.id,
        "user_id": strategy.user_id,
        "symbol": strategy.symbol,
        "buy_time": str(strategy.buy_time),
        "sell_time": str(strategy.sell_time),
        "stop_loss": str(strategy.stop_loss),
        "quantity": strategy.quantity,
        "status": strategy.status.value,
        "position": strategy.position.value,
    })
    
    # Schedule orders
    await schedule_buy_order(strategy_id, strategy.buy_time)
    await schedule_sell_order(strategy_id, strategy.sell_time)
    
    return strategy

async def stop_strategy(
    db: AsyncSession,
    strategy_id: str,
    exit_position: bool = False
) -> Strategy:
    """Stop a running strategy"""
    
    result = await db.execute(
        select(Strategy).where(Strategy.id == strategy_id)
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise ValueError("Strategy not found")
    
    # Cancel scheduled orders
    await cancel_scheduled_orders(strategy_id)
    
    # Remove from Redis
    await remove_active_strategy(strategy_id)
    
    # Update status
    strategy.status = StrategyStatus.STOPPED
    strategy.last_action = "Strategy stopped by user"
    
    # If exit_position requested and we're BOUGHT, queue sell order
    if exit_position and strategy.position == PositionStatus.BOUGHT:
        # Queue immediate sell
        from app.workers.tasks import execute_sell_order
        execute_sell_order.delay(strategy_id)
        strategy.last_action = "Strategy stopped - exit order queued"
    
    await db.commit()
    await db.refresh(strategy)
    
    return strategy
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-038: Create Strategy Validation Service

**File**: `backend/app/services/strategy_validator.py`

**Description**: Implement strategy validation service for symbol validation, time validation, and stop-loss percentage checks.

**Acceptance Criteria**:
- [ ] `validate_symbol(symbol: str) -> bool` - validates symbol format
- [ ] `validate_times(buy_time, sell_time) -> bool` - validates time order
- [ ] `validate_market_hours(time) -> bool` - checks market hours
- [ ] `validate_stop_loss(stop_loss, symbol) -> bool` - validates SL percentage
- [ ] `validate_strategy(request) -> List[str]` - returns list of errors
- [ ] Stop-loss should be within reasonable percentage (e.g., 1-20%)

**Code Reference**:
```python
from datetime import time
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel

MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)
MIN_STOP_LOSS_PERCENT = Decimal("0.5")  # 0.5%
MAX_STOP_LOSS_PERCENT = Decimal("20.0")  # 20%

class ValidationError(BaseModel):
    field: str
    message: str

def validate_symbol(symbol: str) -> Optional[str]:
    """Validate trading symbol format"""
    if not symbol:
        return "Symbol is required"
    if len(symbol) > 20:
        return "Symbol must be 20 characters or less"
    if not symbol.isalnum():
        return "Symbol must contain only letters and numbers"
    return None

def validate_market_hours(t: time) -> Optional[str]:
    """Validate time is within market hours"""
    if t < MARKET_OPEN:
        return f"Time must be after market open ({MARKET_OPEN})"
    if t > MARKET_CLOSE:
        return f"Time must be before market close ({MARKET_CLOSE})"
    return None

def validate_times(buy_time: time, sell_time: time) -> Optional[str]:
    """Validate buy_time is before sell_time"""
    if buy_time >= sell_time:
        return "sell_time must be after buy_time"
    return None

def validate_stop_loss_percentage(
    stop_loss: Decimal,
    expected_price: Decimal
) -> Optional[str]:
    """Validate stop-loss is within reasonable percentage"""
    if expected_price <= 0:
        return None  # Can't validate without price
    
    sl_percent = ((expected_price - stop_loss) / expected_price) * 100
    
    if sl_percent < MIN_STOP_LOSS_PERCENT:
        return f"Stop-loss too tight. Minimum {MIN_STOP_LOSS_PERCENT}% from entry"
    if sl_percent > MAX_STOP_LOSS_PERCENT:
        return f"Stop-loss too wide. Maximum {MAX_STOP_LOSS_PERCENT}% from entry"
    
    return None

def validate_quantity(quantity: int) -> Optional[str]:
    """Validate quantity"""
    if quantity <= 0:
        return "Quantity must be greater than 0"
    if quantity > 10000:
        return "Quantity exceeds maximum allowed (10000)"
    return None

def validate_strategy_request(
    symbol: str,
    buy_time: time,
    sell_time: time,
    stop_loss: Decimal,
    quantity: int
) -> List[ValidationError]:
    """Validate complete strategy request"""
    errors = []
    
    # Symbol validation
    symbol_error = validate_symbol(symbol)
    if symbol_error:
        errors.append(ValidationError(field="symbol", message=symbol_error))
    
    # Buy time validation
    buy_time_error = validate_market_hours(buy_time)
    if buy_time_error:
        errors.append(ValidationError(field="buy_time", message=buy_time_error))
    
    # Sell time validation
    sell_time_error = validate_market_hours(sell_time)
    if sell_time_error:
        errors.append(ValidationError(field="sell_time", message=sell_time_error))
    
    # Time order validation
    time_order_error = validate_times(buy_time, sell_time)
    if time_order_error:
        errors.append(ValidationError(field="sell_time", message=time_order_error))
    
    # Quantity validation
    quantity_error = validate_quantity(quantity)
    if quantity_error:
        errors.append(ValidationError(field="quantity", message=quantity_error))
    
    # Stop-loss mandatory
    if stop_loss is None or stop_loss <= 0:
        errors.append(ValidationError(
            field="stop_loss",
            message="Stop-loss is mandatory and must be greater than 0"
        ))
    
    return errors
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-039: Add Strategy Status Enum

**File**: `backend/app/models/strategy.py`

**Description**: Add strategy status enum: CREATED, RUNNING, STOPPED, COMPLETED, ERROR.

**Acceptance Criteria**:
- [ ] Enum is importable from models
- [ ] Used consistently across API and services
- [ ] Documented state transitions

**Code Reference**:
```python
# Already included in TASK-028, but document state transitions here

"""
Strategy Status State Machine:

CREATED → RUNNING (on start)
RUNNING → STOPPED (on stop or error)
RUNNING → COMPLETED (when sell executed)
RUNNING → ERROR (on unrecoverable failure)
STOPPED → RUNNING (on restart)
ERROR → STOPPED (on acknowledge/reset)

Valid transitions:
- CREATED: [RUNNING]
- RUNNING: [STOPPED, COMPLETED, ERROR]
- STOPPED: [RUNNING] (can restart)
- COMPLETED: [] (terminal state)
- ERROR: [STOPPED] (can reset and try again)
"""
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-040: Add Position Tracking Enum

**File**: `backend/app/models/strategy.py`

**Description**: Add position tracking enum: NONE, BOUGHT, SOLD, SL_HIT.

**Acceptance Criteria**:
- [ ] Enum is importable from models
- [ ] Used consistently across API and services
- [ ] Documented position transitions

**Code Reference**:
```python
# Already included in TASK-028, but document position transitions here

"""
Position Status State Machine:

NONE → BOUGHT (on buy execution)
BOUGHT → SOLD (on sell execution)
BOUGHT → SL_HIT (on stop-loss trigger)
SOLD → NONE (terminal for this strategy)
SL_HIT → NONE (terminal for this strategy)

Valid transitions:
- NONE: [BOUGHT]
- BOUGHT: [SOLD, SL_HIT]
- SOLD: [] (terminal)
- SL_HIT: [] (terminal)
"""
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-041: Ensure Multi-Tenant Isolation

**File**: `backend/app/api/strategies.py`

**Description**: Ensure all strategy queries filter by `user_id` for multi-tenant isolation.

**Acceptance Criteria**:
- [ ] All SELECT queries include user_id filter
- [ ] All UPDATE/DELETE operations verify ownership
- [ ] No way to access another user's strategies
- [ ] Audit log for unauthorized access attempts
- [ ] Test cases for isolation

**Code Reference**:
```python
# Pattern to follow in ALL strategy operations:

async def get_user_strategy(
    db: AsyncSession,
    strategy_id: str,
    user_id: str
) -> Strategy | None:
    """Get strategy only if owned by user"""
    result = await db.execute(
        select(Strategy).where(
            Strategy.id == strategy_id,
            Strategy.user_id == user_id  # CRITICAL: Always filter by user_id
        )
    )
    return result.scalar_one_or_none()

async def list_user_strategies(
    db: AsyncSession,
    user_id: str,
    **filters
) -> List[Strategy]:
    """List strategies only for specific user"""
    query = select(Strategy).where(
        Strategy.user_id == user_id  # CRITICAL: Always filter by user_id
    )
    # Apply additional filters
    result = await db.execute(query)
    return result.scalars().all()

# NEVER do this:
# select(Strategy).where(Strategy.id == strategy_id)  # Missing user_id!
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-042: Write Strategy Unit Tests

**File**: `backend/tests/test_strategies.py`

**Description**: Write comprehensive unit tests for all strategy endpoints.

**Acceptance Criteria**:
- [ ] Test create strategy with valid data
- [ ] Test create strategy without stop_loss (should fail)
- [ ] Test create strategy with invalid times
- [ ] Test list strategies with pagination
- [ ] Test list strategies with filters
- [ ] Test get strategy detail
- [ ] Test get strategy owned by different user (403)
- [ ] Test update strategy when stopped
- [ ] Test update strategy when running (limited fields)
- [ ] Test delete strategy when stopped
- [ ] Test delete strategy when running (should fail)
- [ ] Test start strategy
- [ ] Test start strategy without broker (should fail)
- [ ] Test stop strategy
- [ ] Test status endpoint

**Code Reference**:
```python
import pytest
from httpx import AsyncClient
from datetime import time
from app.main import app

@pytest.fixture
async def auth_headers(test_user):
    """Get auth headers for test user"""
    return {"Authorization": f"Bearer {test_user['token']}"}

@pytest.fixture
async def connected_broker(auth_headers, db):
    """Ensure broker is connected for test user"""
    # Create mock broker connection
    pass

@pytest.mark.asyncio
async def test_create_strategy_success(auth_headers, connected_broker):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/strategies",
            headers=auth_headers,
            json={
                "symbol": "RELIANCE",
                "buy_time": "09:30:00",
                "sell_time": "15:00:00",
                "stop_loss": "2500.00",
                "quantity": 10
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["id"].startswith("str_")
        assert data["symbol"] == "RELIANCE"
        assert data["status"] == "CREATED"
        assert data["position"] == "NONE"

@pytest.mark.asyncio
async def test_create_strategy_without_stop_loss(auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/strategies",
            headers=auth_headers,
            json={
                "symbol": "RELIANCE",
                "buy_time": "09:30:00",
                "sell_time": "15:00:00",
                # stop_loss is missing - should fail
                "quantity": 10
            }
        )
        assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_create_strategy_invalid_times(auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/strategies",
            headers=auth_headers,
            json={
                "symbol": "RELIANCE",
                "buy_time": "15:00:00",  # After sell_time
                "sell_time": "09:30:00",
                "stop_loss": "2500.00",
                "quantity": 10
            }
        )
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_strategy_other_user(auth_headers, other_user_strategy):
    """Test that user cannot access another user's strategy"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/strategies/{other_user_strategy['id']}",
            headers=auth_headers
        )
        assert response.status_code == 403

@pytest.mark.asyncio
async def test_delete_running_strategy(auth_headers, running_strategy):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(
            f"/strategies/{running_strategy['id']}",
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "running" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_start_strategy_without_broker(auth_headers, created_strategy):
    # No broker connected
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/strategies/{created_strategy['id']}/start",
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "broker" in response.json()["detail"].lower()
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/app/models/strategy.py` | Modify | Strategy model with enums |
| `backend/app/api/strategies.py` | Modify | Strategy CRUD endpoints |
| `backend/app/services/strategy_service.py` | Create | Strategy business logic |
| `backend/app/services/strategy_validator.py` | Create | Validation service |
| `backend/tests/test_strategies.py` | Create | Strategy tests |
| `backend/alembic/versions/xxxx_create_strategies.py` | Create | Database migration |

---

## Definition of Done

- [ ] All 15 tasks completed
- [ ] All unit tests passing
- [ ] Code reviewed and approved
- [ ] Database migration tested
- [ ] API documentation updated
- [ ] Multi-tenant isolation verified
- [ ] Stop-loss is mandatory on all strategies

---

## Next Phase

After completing Phase 3, proceed to [Phase 4: Redis Runtime & In-Memory Execution](./phase-04-redis-runtime.md)
