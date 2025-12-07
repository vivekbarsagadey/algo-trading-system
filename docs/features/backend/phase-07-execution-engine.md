---
goal: Phase 7 - Execution Engine for Order Placement
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Backend Engineering Team
status: Planned
tags: [backend, execution, orders, trading, safety]
---

# Phase 7: Execution Engine

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

## Goal

**GOAL-007**: Implement the core execution engine for placing buy/sell orders through broker APIs

## Overview

This phase implements the execution engine - the heart of the trading system. It handles order placement, status tracking, and failsafe mechanisms. The engine ensures orders are placed correctly with proper validation, locking, and error handling.

---

## Prerequisites

- Phase 1-6 completed
- Broker adapters implemented
- Redis service running
- Market data listener active

## Dependencies

```txt
# Uses broker SDKs from Phase 2
```

---

## Implementation Tasks

### TASK-075: Create ExecutionEngine Class

**File**: `backend/app/services/execution_engine.py`

**Description**: Create ExecutionEngine class to orchestrate order execution flow.

**Acceptance Criteria**:
- [ ] Central point for all order execution
- [ ] Broker-agnostic interface
- [ ] State management integration
- [ ] Logging and audit trail
- [ ] Error handling framework

**Code Reference**:
```python
from typing import Dict, Any, Optional
from decimal import Decimal
from enum import Enum
import logging
from datetime import datetime

from app.services.redis_service import (
    get_active_strategy,
    update_strategy_state,
    acquire_order_lock,
    LockAcquisitionError,
    publish_order_executed
)
from app.services.broker_service import get_broker_adapter

logger = logging.getLogger(__name__)

class OrderType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    SL_SELL = "SL_SELL"

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PLACED = "PLACED"
    EXECUTED = "EXECUTED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"

class ExecutionEngine:
    """Core execution engine for order placement"""
    
    def __init__(self):
        self.retry_attempts = 3
        self.retry_delay_seconds = 1
    
    async def execute_order(
        self,
        strategy: dict,
        order_type: OrderType,
        price: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Execute an order for a strategy"""
        strategy_id = strategy["id"]
        user_id = strategy["user_id"]
        
        logger.info(f"Executing {order_type.value} order for strategy {strategy_id}")
        
        try:
            # Acquire lock to prevent duplicate orders
            async with acquire_order_lock(strategy_id, order_type.value):
                
                # Validate pre-conditions
                await self._validate_order(strategy, order_type)
                
                # Prepare order data
                order_data = await self._prepare_order(strategy, order_type, price)
                
                # Place order via broker
                result = await self._place_order(strategy, order_data)
                
                # Update strategy state
                await self._update_state_after_order(strategy, order_type, result)
                
                # Publish event
                await publish_order_executed(
                    user_id,
                    strategy_id,
                    order_type.value,
                    result.get("execution_price", price)
                )
                
                logger.info(f"Order executed successfully: {result}")
                return result
                
        except LockAcquisitionError:
            logger.warning(f"Could not acquire lock for {strategy_id}:{order_type}")
            raise DuplicateOrderError(f"Order already in progress for {strategy_id}")
        
        except OrderValidationError as e:
            logger.error(f"Order validation failed: {e}")
            raise
        
        except BrokerError as e:
            logger.error(f"Broker error: {e}")
            await self._handle_broker_error(strategy, order_type, e)
            raise

class DuplicateOrderError(Exception):
    """Raised when duplicate order is detected"""
    pass

class OrderValidationError(Exception):
    """Raised when order validation fails"""
    pass

class BrokerError(Exception):
    """Raised when broker rejects/fails order"""
    pass

# Singleton
_execution_engine: ExecutionEngine = None

def get_execution_engine() -> ExecutionEngine:
    global _execution_engine
    if _execution_engine is None:
        _execution_engine = ExecutionEngine()
    return _execution_engine
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-076: Implement place_buy_order

**File**: `backend/app/services/execution_engine.py`

**Description**: Implement `place_buy_order(strategy)` to execute market buy orders.

**Acceptance Criteria**:
- [ ] Market order execution
- [ ] Quantity from strategy
- [ ] Use broker adapter
- [ ] Update position to BOUGHT
- [ ] Store entry_price
- [ ] Handle partial fills

**Code Reference**:
```python
async def place_buy_order(strategy: dict) -> Dict[str, Any]:
    """Place buy order for a strategy"""
    engine = get_execution_engine()
    return await engine.execute_order(strategy, OrderType.BUY)

class ExecutionEngine:
    # ... continued
    
    async def _prepare_order(
        self,
        strategy: dict,
        order_type: OrderType,
        price: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Prepare order data for broker"""
        
        order_data = {
            "symbol": strategy["symbol"],
            "quantity": int(strategy["quantity"]),
            "exchange": "NSE",
            "order_type": "MARKET",  # Always market orders
            "product": "CNC",  # Delivery
            "transaction_type": "BUY" if order_type == OrderType.BUY else "SELL"
        }
        
        if price:
            order_data["price"] = float(price)
        
        return order_data
    
    async def _place_order(
        self,
        strategy: dict,
        order_data: dict
    ) -> Dict[str, Any]:
        """Place order through broker adapter"""
        user_id = strategy["user_id"]
        broker_name = strategy.get("broker", "zerodha")
        
        # Get broker adapter
        adapter = await get_broker_adapter(user_id, broker_name)
        
        # Place order with retry
        for attempt in range(self.retry_attempts):
            try:
                result = await adapter.place_order(order_data)
                return result
            except Exception as e:
                if attempt < self.retry_attempts - 1:
                    logger.warning(f"Order attempt {attempt + 1} failed: {e}, retrying...")
                    await asyncio.sleep(self.retry_delay_seconds)
                else:
                    raise BrokerError(f"Order failed after {self.retry_attempts} attempts: {e}")
    
    async def _update_state_after_order(
        self,
        strategy: dict,
        order_type: OrderType,
        result: dict
    ):
        """Update strategy state after order execution"""
        strategy_id = strategy["id"]
        user_id = strategy["user_id"]
        
        updates = {
            "last_action": order_type.value,
            "last_action_time": datetime.utcnow().isoformat(),
            "last_order_id": result.get("order_id")
        }
        
        if order_type == OrderType.BUY:
            updates["position"] = "BOUGHT"
            updates["entry_price"] = str(result.get("execution_price", "0"))
            updates["entry_time"] = datetime.utcnow().isoformat()
        
        elif order_type in (OrderType.SELL, OrderType.SL_SELL):
            updates["position"] = "SOLD"
            updates["exit_price"] = str(result.get("execution_price", "0"))
            updates["exit_time"] = datetime.utcnow().isoformat()
            
            # Calculate P&L
            if strategy.get("entry_price"):
                entry = Decimal(strategy["entry_price"])
                exit_price = Decimal(str(result.get("execution_price", "0")))
                quantity = int(strategy["quantity"])
                pnl = (exit_price - entry) * quantity
                updates["pnl"] = str(pnl)
        
        await update_strategy_state(strategy_id, user_id, updates)
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-077: Implement place_sell_order

**File**: `backend/app/services/execution_engine.py`

**Description**: Implement `place_sell_order(strategy)` for scheduled sell orders.

**Acceptance Criteria**:
- [ ] Market sell order
- [ ] Only if position is BOUGHT
- [ ] Update position to SOLD
- [ ] Store exit_price
- [ ] Calculate P&L
- [ ] Handle partial fills

**Code Reference**:
```python
async def place_sell_order(strategy: dict) -> Dict[str, Any]:
    """Place sell order for a strategy"""
    engine = get_execution_engine()
    return await engine.execute_order(strategy, OrderType.SELL)

class ExecutionEngine:
    # ... continued
    
    async def _validate_order(
        self,
        strategy: dict,
        order_type: OrderType
    ):
        """Validate order pre-conditions"""
        strategy_id = strategy["id"]
        position = strategy.get("position", "NONE")
        
        # Validate based on order type
        if order_type == OrderType.BUY:
            if position != "NONE":
                raise OrderValidationError(
                    f"Cannot buy - strategy {strategy_id} already has position {position}"
                )
        
        elif order_type in (OrderType.SELL, OrderType.SL_SELL):
            if position != "BOUGHT":
                raise OrderValidationError(
                    f"Cannot sell - strategy {strategy_id} has no position (current: {position})"
                )
        
        # Validate strategy is still running
        if strategy.get("status") != "RUNNING":
            raise OrderValidationError(
                f"Cannot execute - strategy {strategy_id} is not running"
            )
        
        # Validate quantity
        quantity = strategy.get("quantity", 0)
        if quantity <= 0:
            raise OrderValidationError(
                f"Invalid quantity: {quantity}"
            )
        
        # Validate symbol
        if not strategy.get("symbol"):
            raise OrderValidationError("Missing symbol")
        
        logger.debug(f"Order validation passed for {strategy_id}:{order_type}")
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-078: Implement place_sl_sell_order

**File**: `backend/app/services/execution_engine.py`

**Description**: Implement `place_sl_sell_order(strategy, trigger_price)` for stop-loss triggered orders.

**Acceptance Criteria**:
- [ ] Immediate market sell
- [ ] Log stop-loss trigger
- [ ] Record trigger price
- [ ] Update position to SOLD
- [ ] Mark strategy as SL_TRIGGERED

**Code Reference**:
```python
async def place_sl_sell_order(
    strategy: dict,
    trigger_price: Decimal
) -> Dict[str, Any]:
    """Place stop-loss sell order"""
    engine = get_execution_engine()
    
    logger.warning(
        f"STOP-LOSS SELL: Strategy {strategy['id']}, "
        f"Trigger price: {trigger_price}"
    )
    
    # Execute the order
    result = await engine.execute_order(
        strategy,
        OrderType.SL_SELL,
        price=trigger_price
    )
    
    # Additional state update for SL
    await update_strategy_state(
        strategy["id"],
        strategy["user_id"],
        {
            "sl_triggered": "true",
            "sl_trigger_price": str(trigger_price),
            "exit_reason": "STOP_LOSS"
        }
    )
    
    return result
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-079: Implement Order Queue with Celery

**File**: `backend/app/workers/tasks.py`

**Description**: Implement Celery task for background order processing.

**Acceptance Criteria**:
- [ ] Async order processing
- [ ] Retry on failure
- [ ] Task result storage
- [ ] Priority queue support
- [ ] Dead letter queue for failures

**Code Reference**:
```python
from celery import shared_task
from app.workers.celery_app import celery_app

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    autoretry_for=(BrokerError,),
    acks_late=True
)
async def process_order_task(
    self,
    strategy_id: str,
    user_id: str,
    order_type: str,
    price: Optional[str] = None
):
    """Celery task for background order processing"""
    from app.services.redis_service import get_active_strategy
    from app.services.execution_engine import (
        get_execution_engine,
        OrderType
    )
    
    logger.info(f"Processing order task: {strategy_id}, {order_type}")
    
    try:
        # Get strategy from Redis
        strategy = await get_active_strategy(strategy_id, user_id)
        if not strategy:
            logger.error(f"Strategy {strategy_id} not found")
            return {"status": "error", "message": "Strategy not found"}
        
        # Execute order
        engine = get_execution_engine()
        result = await engine.execute_order(
            strategy,
            OrderType(order_type),
            price=Decimal(price) if price else None
        )
        
        return {"status": "success", "result": result}
        
    except Exception as e:
        logger.error(f"Order task failed: {e}")
        raise self.retry(exc=e)

@celery_app.task(
    bind=True,
    max_retries=0,  # No retry for SL - must execute immediately
    acks_late=True
)
async def process_sl_order_task(
    self,
    strategy_id: str,
    user_id: str,
    trigger_price: str
):
    """Celery task for stop-loss order - high priority, no retry"""
    from app.services.redis_service import get_active_strategy
    from app.services.execution_engine import place_sl_sell_order
    
    logger.warning(f"Processing SL order task: {strategy_id}")
    
    strategy = await get_active_strategy(strategy_id, user_id)
    if not strategy:
        logger.error(f"Strategy {strategy_id} not found for SL")
        return {"status": "error", "message": "Strategy not found"}
    
    result = await place_sl_sell_order(strategy, Decimal(trigger_price))
    return {"status": "success", "result": result}
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-080: Implement Order Status Tracking

**File**: `backend/app/services/execution_engine.py`

**Description**: Implement order status tracking and polling for completion.

**Acceptance Criteria**:
- [ ] Track order status
- [ ] Poll for execution
- [ ] Handle pending orders
- [ ] Timeout handling
- [ ] Callback on completion

**Code Reference**:
```python
import asyncio

class OrderTracker:
    """Tracks order status and waits for completion"""
    
    def __init__(self, timeout_seconds: int = 30):
        self.timeout = timeout_seconds
        self.poll_interval = 1  # seconds
    
    async def wait_for_completion(
        self,
        user_id: str,
        broker_name: str,
        order_id: str
    ) -> Dict[str, Any]:
        """Wait for order to complete or timeout"""
        adapter = await get_broker_adapter(user_id, broker_name)
        
        start_time = datetime.utcnow()
        
        while True:
            # Check timeout
            elapsed = (datetime.utcnow() - start_time).seconds
            if elapsed > self.timeout:
                raise OrderTimeoutError(f"Order {order_id} timed out after {self.timeout}s")
            
            # Get order status
            status = await adapter.get_order_status(order_id)
            
            if status["status"] == "COMPLETE":
                return {
                    "order_id": order_id,
                    "status": "EXECUTED",
                    "execution_price": status.get("average_price"),
                    "filled_quantity": status.get("filled_quantity"),
                    "timestamp": status.get("exchange_timestamp")
                }
            
            elif status["status"] == "REJECTED":
                raise OrderRejectedError(
                    f"Order {order_id} rejected: {status.get('status_message')}"
                )
            
            elif status["status"] == "CANCELLED":
                raise OrderCancelledError(f"Order {order_id} was cancelled")
            
            # Still pending, wait and poll again
            await asyncio.sleep(self.poll_interval)
    
    async def get_order_history(
        self,
        user_id: str,
        broker_name: str,
        strategy_id: str
    ) -> List[Dict[str, Any]]:
        """Get order history for a strategy"""
        adapter = await get_broker_adapter(user_id, broker_name)
        
        # Get today's orders
        orders = await adapter.get_orders()
        
        # Filter by strategy (using tag or order metadata)
        strategy_orders = [
            o for o in orders
            if o.get("tag") == strategy_id or o.get("strategy_id") == strategy_id
        ]
        
        return strategy_orders

class OrderTimeoutError(Exception):
    """Raised when order times out"""
    pass

class OrderRejectedError(Exception):
    """Raised when order is rejected by broker"""
    pass

class OrderCancelledError(Exception):
    """Raised when order is cancelled"""
    pass
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-081: Implement Failsafe Mechanisms

**File**: `backend/app/services/execution_engine.py`

**Description**: Implement failsafe mechanisms for order failures.

**Acceptance Criteria**:
- [ ] Retry failed orders
- [ ] Exponential backoff
- [ ] Max retry limit
- [ ] Alert on failure
- [ ] Manual intervention flag
- [ ] Emergency stop

**Code Reference**:
```python
from typing import Callable

class FailsafeManager:
    """Manages failsafe mechanisms for order execution"""
    
    def __init__(self):
        self.max_retries = 3
        self.base_delay = 1  # seconds
        self.alert_handlers: List[Callable] = []
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with retry logic"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except (BrokerError, ConnectionError) as e:
                last_error = e
                delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                
                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries} failed: {e}, "
                    f"retrying in {delay}s"
                )
                
                await asyncio.sleep(delay)
            except OrderValidationError:
                # Don't retry validation errors
                raise
        
        # All retries failed
        await self._handle_failure(last_error, args, kwargs)
        raise ExecutionFailureError(f"Failed after {self.max_retries} retries: {last_error}")
    
    async def _handle_failure(self, error: Exception, args: tuple, kwargs: dict):
        """Handle complete failure after all retries"""
        logger.error(f"Execution failed completely: {error}")
        
        # Mark strategy for manual intervention
        if "strategy" in kwargs:
            strategy = kwargs["strategy"]
            await update_strategy_state(
                strategy["id"],
                strategy["user_id"],
                {
                    "needs_intervention": "true",
                    "last_error": str(error),
                    "error_time": datetime.utcnow().isoformat()
                }
            )
        
        # Send alerts
        await self._send_alerts(error, args, kwargs)
    
    async def _send_alerts(self, error: Exception, args: tuple, kwargs: dict):
        """Send failure alerts"""
        for handler in self.alert_handlers:
            try:
                await handler(error, args, kwargs)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
    
    def register_alert_handler(self, handler: Callable):
        """Register alert handler for failures"""
        self.alert_handlers.append(handler)
    
    async def emergency_stop(self, user_id: str, reason: str):
        """Emergency stop all strategies for a user"""
        from app.services.redis_service import get_all_active_strategies
        from app.services.scheduler_service import get_scheduler
        
        logger.critical(f"EMERGENCY STOP for user {user_id}: {reason}")
        
        strategies = await get_all_active_strategies()
        user_strategies = [s for s in strategies if s["user_id"] == user_id]
        
        scheduler = await get_scheduler()
        
        for strategy in user_strategies:
            # Cancel scheduled jobs
            await scheduler.cancel_strategy_jobs(strategy["id"])
            
            # Update status
            await update_strategy_state(
                strategy["id"],
                user_id,
                {
                    "status": "STOPPED",
                    "stop_reason": f"EMERGENCY: {reason}",
                    "stopped_at": datetime.utcnow().isoformat()
                }
            )
        
        logger.critical(f"Emergency stopped {len(user_strategies)} strategies")

class ExecutionFailureError(Exception):
    """Raised when execution fails after all retries"""
    pass

# Singleton
_failsafe_manager: FailsafeManager = None

def get_failsafe_manager() -> FailsafeManager:
    global _failsafe_manager
    if _failsafe_manager is None:
        _failsafe_manager = FailsafeManager()
    return _failsafe_manager
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-082: Implement Order Logging and Audit

**File**: `backend/app/services/execution_engine.py`

**Description**: Implement comprehensive order logging for audit trail.

**Acceptance Criteria**:
- [ ] Log all order attempts
- [ ] Log order results
- [ ] Include timestamps
- [ ] Persist to database
- [ ] Support audit queries

**Code Reference**:
```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order_log import OrderLog

class OrderAuditLogger:
    """Logs all order activity for audit trail"""
    
    async def log_order_attempt(
        self,
        db: AsyncSession,
        strategy_id: str,
        user_id: str,
        order_type: str,
        order_data: dict
    ) -> str:
        """Log order attempt, returns log_id"""
        log = OrderLog(
            strategy_id=strategy_id,
            user_id=user_id,
            order_type=order_type,
            order_data=order_data,
            status="ATTEMPTING",
            attempted_at=datetime.utcnow()
        )
        
        db.add(log)
        await db.commit()
        await db.refresh(log)
        
        logger.info(f"Order attempt logged: {log.id}")
        return log.id
    
    async def log_order_result(
        self,
        db: AsyncSession,
        log_id: str,
        result: dict,
        success: bool
    ):
        """Log order result"""
        from sqlalchemy import select
        
        stmt = select(OrderLog).where(OrderLog.id == log_id)
        result_obj = await db.execute(stmt)
        log = result_obj.scalar_one_or_none()
        
        if log:
            log.status = "SUCCESS" if success else "FAILED"
            log.result = result
            log.completed_at = datetime.utcnow()
            log.execution_time_ms = (
                (log.completed_at - log.attempted_at).total_seconds() * 1000
            )
            
            await db.commit()
            logger.info(f"Order result logged: {log_id}, success={success}")
    
    async def log_order_error(
        self,
        db: AsyncSession,
        log_id: str,
        error: Exception
    ):
        """Log order error"""
        from sqlalchemy import select
        
        stmt = select(OrderLog).where(OrderLog.id == log_id)
        result = await db.execute(stmt)
        log = result.scalar_one_or_none()
        
        if log:
            log.status = "ERROR"
            log.error_message = str(error)
            log.completed_at = datetime.utcnow()
            
            await db.commit()
            logger.error(f"Order error logged: {log_id}, error={error}")
    
    async def get_order_history(
        self,
        db: AsyncSession,
        user_id: str,
        strategy_id: Optional[str] = None,
        limit: int = 100
    ) -> List[OrderLog]:
        """Get order history for audit"""
        from sqlalchemy import select
        
        stmt = select(OrderLog).where(OrderLog.user_id == user_id)
        
        if strategy_id:
            stmt = stmt.where(OrderLog.strategy_id == strategy_id)
        
        stmt = stmt.order_by(OrderLog.attempted_at.desc()).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()

# Model for order logs
class OrderLog(Base):
    __tablename__ = "order_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: f"ord_{uuid4().hex[:12]}")
    strategy_id = Column(String(36), ForeignKey("strategies.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    order_type = Column(String(20), nullable=False)  # BUY, SELL, SL_SELL
    order_data = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False)  # ATTEMPTING, SUCCESS, FAILED, ERROR
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    attempted_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    
    # Relationships
    strategy = relationship("Strategy", back_populates="order_logs")
    user = relationship("User", back_populates="order_logs")
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-083: Create Execution API Endpoints

**File**: `backend/app/api/execution.py`

**Description**: Create API endpoints for order management.

**Acceptance Criteria**:
- [ ] Manual order trigger endpoint
- [ ] Order status endpoint
- [ ] Order history endpoint
- [ ] Cancel order endpoint
- [ ] Emergency stop endpoint

**Code Reference**:
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

from app.api.auth import get_current_user
from app.models.user import User
from app.services.execution_engine import (
    get_execution_engine,
    OrderType,
    place_buy_order,
    place_sell_order,
    OrderTracker,
    get_failsafe_manager
)
from app.services.redis_service import get_active_strategy

router = APIRouter(prefix="/execution", tags=["Execution"])

class ManualOrderRequest(BaseModel):
    strategy_id: str
    order_type: str  # BUY or SELL
    price: Optional[float] = None

@router.post("/order")
async def trigger_manual_order(
    request: ManualOrderRequest,
    current_user: User = Depends(get_current_user)
):
    """Manually trigger an order for a strategy"""
    strategy = await get_active_strategy(request.strategy_id, current_user.id)
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    try:
        if request.order_type == "BUY":
            result = await place_buy_order(strategy)
        elif request.order_type == "SELL":
            result = await place_sell_order(strategy)
        else:
            raise HTTPException(status_code=400, detail="Invalid order type")
        
        return {"status": "success", "result": result}
    
    except DuplicateOrderError:
        raise HTTPException(status_code=409, detail="Order already in progress")
    except OrderValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except BrokerError as e:
        raise HTTPException(status_code=500, detail=f"Broker error: {e}")

@router.get("/order/{order_id}/status")
async def get_order_status(
    order_id: str,
    broker: str = "zerodha",
    current_user: User = Depends(get_current_user)
):
    """Get status of an order"""
    tracker = OrderTracker()
    
    try:
        status = await tracker.wait_for_completion(
            current_user.id,
            broker,
            order_id
        )
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_order_history(
    strategy_id: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get order history"""
    audit_logger = OrderAuditLogger()
    orders = await audit_logger.get_order_history(
        db,
        current_user.id,
        strategy_id,
        limit
    )
    
    return {"orders": [o.to_dict() for o in orders]}

@router.post("/emergency-stop")
async def emergency_stop(
    reason: str,
    current_user: User = Depends(get_current_user)
):
    """Emergency stop all strategies"""
    failsafe = get_failsafe_manager()
    await failsafe.emergency_stop(current_user.id, reason)
    
    return {"status": "stopped", "message": f"All strategies stopped: {reason}"}
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-084: Write Execution Engine Tests

**File**: `backend/tests/test_execution_engine.py`

**Description**: Write comprehensive tests for execution engine.

**Acceptance Criteria**:
- [ ] Test order validation
- [ ] Test buy order execution
- [ ] Test sell order execution
- [ ] Test stop-loss execution
- [ ] Test retry logic
- [ ] Test failsafe mechanisms
- [ ] Test order logging
- [ ] Mock broker adapter

**Code Reference**:
```python
import pytest
from unittest.mock import Mock, AsyncMock, patch
from decimal import Decimal
from app.services.execution_engine import (
    ExecutionEngine,
    OrderType,
    OrderValidationError,
    DuplicateOrderError,
    BrokerError,
    place_buy_order,
    place_sell_order
)

class TestOrderValidation:
    
    @pytest.fixture
    def engine(self):
        return ExecutionEngine()
    
    @pytest.mark.asyncio
    async def test_buy_requires_no_position(self, engine):
        """Test buy fails if already has position"""
        strategy = {
            "id": "str_123",
            "status": "RUNNING",
            "position": "BOUGHT",
            "quantity": 10,
            "symbol": "RELIANCE"
        }
        
        with pytest.raises(OrderValidationError) as exc:
            await engine._validate_order(strategy, OrderType.BUY)
        
        assert "already has position" in str(exc.value)
    
    @pytest.mark.asyncio
    async def test_sell_requires_position(self, engine):
        """Test sell fails without position"""
        strategy = {
            "id": "str_123",
            "status": "RUNNING",
            "position": "NONE",
            "quantity": 10,
            "symbol": "RELIANCE"
        }
        
        with pytest.raises(OrderValidationError) as exc:
            await engine._validate_order(strategy, OrderType.SELL)
        
        assert "has no position" in str(exc.value)
    
    @pytest.mark.asyncio
    async def test_order_requires_running_status(self, engine):
        """Test order fails if strategy not running"""
        strategy = {
            "id": "str_123",
            "status": "STOPPED",
            "position": "NONE",
            "quantity": 10,
            "symbol": "RELIANCE"
        }
        
        with pytest.raises(OrderValidationError) as exc:
            await engine._validate_order(strategy, OrderType.BUY)
        
        assert "not running" in str(exc.value)

class TestOrderExecution:
    
    @pytest.fixture
    def mock_adapter(self):
        adapter = AsyncMock()
        adapter.place_order.return_value = {
            "order_id": "ord_123",
            "status": "COMPLETE",
            "execution_price": 2650.50
        }
        return adapter
    
    @pytest.mark.asyncio
    async def test_buy_order_success(self, mock_adapter):
        """Test successful buy order"""
        strategy = {
            "id": "str_123",
            "user_id": "usr_456",
            "status": "RUNNING",
            "position": "NONE",
            "quantity": 10,
            "symbol": "RELIANCE",
            "broker": "zerodha"
        }
        
        with patch("app.services.execution_engine.get_broker_adapter") as mock_get:
            mock_get.return_value = mock_adapter
            
            with patch("app.services.execution_engine.acquire_order_lock"):
                with patch("app.services.execution_engine.update_strategy_state"):
                    with patch("app.services.execution_engine.publish_order_executed"):
                        result = await place_buy_order(strategy)
        
        assert result["order_id"] == "ord_123"
        mock_adapter.place_order.assert_called_once()

class TestFailsafe:
    
    @pytest.mark.asyncio
    async def test_retry_on_broker_error(self):
        """Test retry logic on broker error"""
        from app.services.execution_engine import FailsafeManager
        
        failsafe = FailsafeManager()
        failsafe.max_retries = 3
        failsafe.base_delay = 0.1  # Fast for testing
        
        call_count = 0
        
        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise BrokerError("Connection failed")
            return "success"
        
        result = await failsafe.execute_with_retry(failing_func)
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_emergency_stop(self):
        """Test emergency stop functionality"""
        from app.services.execution_engine import get_failsafe_manager
        
        failsafe = get_failsafe_manager()
        
        with patch("app.services.execution_engine.get_all_active_strategies") as mock_get:
            mock_get.return_value = [
                {"id": "str_1", "user_id": "usr_1"},
                {"id": "str_2", "user_id": "usr_1"}
            ]
            
            with patch("app.services.execution_engine.get_scheduler"):
                with patch("app.services.execution_engine.update_strategy_state"):
                    await failsafe.emergency_stop("usr_1", "Test emergency")
        
        # Verify strategies were stopped
        mock_get.assert_called_once()
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/app/services/execution_engine.py` | Create | Core execution engine |
| `backend/app/workers/tasks.py` | Modify | Add order tasks |
| `backend/app/models/order_log.py` | Create | Order log model |
| `backend/app/api/execution.py` | Create | Execution API endpoints |
| `backend/app/main.py` | Modify | Add execution router |
| `backend/tests/test_execution_engine.py` | Create | Unit tests |

---

## Environment Variables Required

```bash
# Execution Configuration
ORDER_RETRY_ATTEMPTS=3
ORDER_TIMEOUT_SECONDS=30
```

---

## Definition of Done

- [ ] All 10 tasks completed
- [ ] Buy/Sell orders execute correctly
- [ ] Stop-loss orders execute immediately
- [ ] Retry logic working
- [ ] Failsafe mechanisms tested
- [ ] Audit logging working
- [ ] API endpoints functional
- [ ] Unit tests passing
- [ ] Code reviewed and approved

---

## Next Phase

After completing Phase 7, proceed to [Phase 8: Real-Time Status & SSE](./phase-08-real-time-sse.md)
