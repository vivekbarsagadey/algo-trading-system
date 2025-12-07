---
goal: Phase 5 - Scheduler Service for Time-Based Execution
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Backend Engineering Team
status: Planned
tags: [backend, scheduler, apscheduler, time-based, automation]
---

# Phase 5: Scheduler Service

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

## Goal

**GOAL-005**: Implement APScheduler-based scheduler for time-based strategy execution

## Overview

This phase implements the scheduler service using APScheduler. The scheduler monitors active strategies and triggers buy/sell actions at the configured times. It integrates with Redis for strategy state and the execution engine for order placement.

---

## Prerequisites

- Phase 1-4 completed
- Redis service running and tested
- APScheduler library installed

## Dependencies

```txt
apscheduler>=4.0.0a5
```

---

## Implementation Tasks

### TASK-055: Create SchedulerService Class

**File**: `backend/app/services/scheduler_service.py`

**Description**: Create SchedulerService class using APScheduler with Redis job store.

**Acceptance Criteria**:
- [ ] APScheduler with async scheduler
- [ ] Redis job store for persistence
- [ ] Graceful start/stop
- [ ] Configurable timezone
- [ ] Error handling for job failures

**Code Reference**:
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from datetime import datetime, time as dt_time
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

class SchedulerService:
    """APScheduler-based scheduler for time-based strategy execution"""
    
    def __init__(self):
        self.scheduler = None
        self.timezone = timezone(settings.SCHEDULER_TIMEZONE or "Asia/Kolkata")
    
    async def start(self):
        """Initialize and start the scheduler"""
        jobstores = {
            "default": RedisJobStore(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_SCHEDULER_DB or 1
            )
        }
        
        executors = {
            "default": AsyncIOExecutor()
        }
        
        job_defaults = {
            "coalesce": True,  # Combine missed runs into one
            "max_instances": 1,  # Only one instance per job
            "misfire_grace_time": 60  # 60 second grace for misfires
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=self.timezone
        )
        
        self.scheduler.start()
        logger.info("Scheduler service started")
    
    async def stop(self):
        """Stop the scheduler gracefully"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("Scheduler service stopped")
    
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self.scheduler and self.scheduler.running
    
    def get_jobs(self):
        """Get all scheduled jobs"""
        return self.scheduler.get_jobs() if self.scheduler else []

# Singleton instance
_scheduler_service: SchedulerService = None

async def get_scheduler() -> SchedulerService:
    """Get scheduler service instance"""
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
        await _scheduler_service.start()
    return _scheduler_service
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-056: Implement schedule_buy_trigger

**File**: `backend/app/services/scheduler_service.py`

**Description**: Implement `schedule_buy_trigger(strategy)` to schedule buy order at strategy.buy_time.

**Acceptance Criteria**:
- [ ] Schedule job at buy_time
- [ ] Pass strategy_id to job
- [ ] Handle timezone correctly
- [ ] Avoid duplicate jobs
- [ ] Market hours validation

**Code Reference**:
```python
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

async def schedule_buy_trigger(self, strategy: dict):
    """Schedule buy order at strategy buy_time"""
    strategy_id = strategy["id"]
    buy_time = strategy["buy_time"]  # HH:MM:SS format
    
    # Parse time
    if isinstance(buy_time, str):
        hour, minute, second = map(int, buy_time.split(":"))
    else:
        hour, minute, second = buy_time.hour, buy_time.minute, buy_time.second
    
    job_id = f"buy_{strategy_id}"
    
    # Remove existing job if any
    if self.scheduler.get_job(job_id):
        self.scheduler.remove_job(job_id)
    
    # Create cron trigger for daily execution
    trigger = CronTrigger(
        hour=hour,
        minute=minute,
        second=second,
        timezone=self.timezone
    )
    
    # Add job
    self.scheduler.add_job(
        execute_buy_order,
        trigger=trigger,
        id=job_id,
        args=[strategy_id],
        name=f"Buy order for {strategy_id}",
        replace_existing=True
    )
    
    logger.info(f"Scheduled buy trigger for {strategy_id} at {buy_time}")

async def execute_buy_order(strategy_id: str):
    """Execute buy order callback"""
    from app.services.execution_engine import place_buy_order
    from app.services.redis_service import get_active_strategy
    
    logger.info(f"Buy trigger fired for strategy {strategy_id}")
    
    # Get strategy from Redis
    strategy = await get_active_strategy(strategy_id)
    if not strategy:
        logger.warning(f"Strategy {strategy_id} not found, skipping buy")
        return
    
    # Check if already bought
    if strategy.get("position") != "NONE":
        logger.info(f"Strategy {strategy_id} already has position, skipping buy")
        return
    
    # Execute buy
    await place_buy_order(strategy)
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-057: Implement schedule_sell_trigger

**File**: `backend/app/services/scheduler_service.py`

**Description**: Implement `schedule_sell_trigger(strategy)` to schedule sell order at strategy.sell_time.

**Acceptance Criteria**:
- [ ] Schedule job at sell_time
- [ ] Pass strategy_id to job
- [ ] Handle timezone correctly
- [ ] Only sell if position is BOUGHT
- [ ] Avoid duplicate jobs

**Code Reference**:
```python
async def schedule_sell_trigger(self, strategy: dict):
    """Schedule sell order at strategy sell_time"""
    strategy_id = strategy["id"]
    sell_time = strategy["sell_time"]  # HH:MM:SS format
    
    # Parse time
    if isinstance(sell_time, str):
        hour, minute, second = map(int, sell_time.split(":"))
    else:
        hour, minute, second = sell_time.hour, sell_time.minute, sell_time.second
    
    job_id = f"sell_{strategy_id}"
    
    # Remove existing job if any
    if self.scheduler.get_job(job_id):
        self.scheduler.remove_job(job_id)
    
    # Create cron trigger for daily execution
    trigger = CronTrigger(
        hour=hour,
        minute=minute,
        second=second,
        timezone=self.timezone
    )
    
    # Add job
    self.scheduler.add_job(
        execute_sell_order,
        trigger=trigger,
        id=job_id,
        args=[strategy_id],
        name=f"Sell order for {strategy_id}",
        replace_existing=True
    )
    
    logger.info(f"Scheduled sell trigger for {strategy_id} at {sell_time}")

async def execute_sell_order(strategy_id: str):
    """Execute sell order callback"""
    from app.services.execution_engine import place_sell_order
    from app.services.redis_service import get_active_strategy
    
    logger.info(f"Sell trigger fired for strategy {strategy_id}")
    
    # Get strategy from Redis
    strategy = await get_active_strategy(strategy_id)
    if not strategy:
        logger.warning(f"Strategy {strategy_id} not found, skipping sell")
        return
    
    # Check if has position to sell
    if strategy.get("position") != "BOUGHT":
        logger.info(f"Strategy {strategy_id} has no position to sell")
        return
    
    # Execute sell
    await place_sell_order(strategy)
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-058: Implement schedule_all_strategies

**File**: `backend/app/services/scheduler_service.py`

**Description**: Implement `schedule_all_strategies()` to load and schedule all active strategies on startup.

**Acceptance Criteria**:
- [ ] Load all running strategies from Redis
- [ ] Schedule buy/sell for each
- [ ] Handle errors gracefully
- [ ] Log scheduling status
- [ ] Skip already-triggered strategies

**Code Reference**:
```python
async def schedule_all_strategies(self):
    """Schedule all active strategies on startup"""
    from app.services.redis_service import get_all_active_strategies
    
    strategies = await get_all_active_strategies()
    
    scheduled_count = 0
    skipped_count = 0
    
    for strategy in strategies:
        if strategy.get("status") != "RUNNING":
            skipped_count += 1
            continue
        
        try:
            # Schedule buy (if not already bought)
            if strategy.get("position") == "NONE":
                await self.schedule_buy_trigger(strategy)
            
            # Schedule sell (always schedule for position exit)
            await self.schedule_sell_trigger(strategy)
            
            scheduled_count += 1
        except Exception as e:
            logger.error(f"Failed to schedule strategy {strategy['id']}: {e}")
    
    logger.info(f"Scheduled {scheduled_count} strategies, skipped {skipped_count}")
    return scheduled_count
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-059: Implement cancel_strategy_jobs

**File**: `backend/app/services/scheduler_service.py`

**Description**: Implement `cancel_strategy_jobs(strategy_id)` to remove all scheduled jobs for a strategy.

**Acceptance Criteria**:
- [ ] Remove buy job
- [ ] Remove sell job
- [ ] Handle non-existent jobs
- [ ] Log cancellation

**Code Reference**:
```python
async def cancel_strategy_jobs(self, strategy_id: str):
    """Cancel all scheduled jobs for a strategy"""
    buy_job_id = f"buy_{strategy_id}"
    sell_job_id = f"sell_{strategy_id}"
    
    cancelled = []
    
    if self.scheduler.get_job(buy_job_id):
        self.scheduler.remove_job(buy_job_id)
        cancelled.append("buy")
    
    if self.scheduler.get_job(sell_job_id):
        self.scheduler.remove_job(sell_job_id)
        cancelled.append("sell")
    
    if cancelled:
        logger.info(f"Cancelled jobs for {strategy_id}: {cancelled}")
    else:
        logger.info(f"No jobs found to cancel for {strategy_id}")
    
    return cancelled
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-060: Add Market Hours Validation

**File**: `backend/app/services/scheduler_service.py`

**Description**: Add market hours validation to prevent scheduling outside 9:15 AM - 3:30 PM.

**Acceptance Criteria**:
- [ ] Validate buy_time in market hours
- [ ] Validate sell_time in market hours
- [ ] Reject invalid times
- [ ] Handle market holidays (optional)
- [ ] Configurable market hours

**Code Reference**:
```python
from datetime import time as dt_time

# Indian market hours
MARKET_OPEN = dt_time(9, 15, 0)
MARKET_CLOSE = dt_time(15, 30, 0)

class MarketHoursError(Exception):
    """Raised when time is outside market hours"""
    pass

def validate_market_hours(buy_time: str, sell_time: str):
    """Validate that times are within market hours"""
    
    # Parse times
    buy_h, buy_m, buy_s = map(int, buy_time.split(":"))
    sell_h, sell_m, sell_s = map(int, sell_time.split(":"))
    
    buy_dt = dt_time(buy_h, buy_m, buy_s)
    sell_dt = dt_time(sell_h, sell_m, sell_s)
    
    # Validate buy time
    if buy_dt < MARKET_OPEN or buy_dt > MARKET_CLOSE:
        raise MarketHoursError(
            f"Buy time {buy_time} is outside market hours "
            f"({MARKET_OPEN.strftime('%H:%M')} - {MARKET_CLOSE.strftime('%H:%M')})"
        )
    
    # Validate sell time
    if sell_dt < MARKET_OPEN or sell_dt > MARKET_CLOSE:
        raise MarketHoursError(
            f"Sell time {sell_time} is outside market hours "
            f"({MARKET_OPEN.strftime('%H:%M')} - {MARKET_CLOSE.strftime('%H:%M')})"
        )
    
    # Validate sell is after buy
    if sell_dt <= buy_dt:
        raise MarketHoursError(
            f"Sell time {sell_time} must be after buy time {buy_time}"
        )
    
    return True

def is_market_open() -> bool:
    """Check if market is currently open"""
    from datetime import datetime
    now = datetime.now(timezone("Asia/Kolkata")).time()
    return MARKET_OPEN <= now <= MARKET_CLOSE

def is_trading_day() -> bool:
    """Check if today is a trading day (not weekend)"""
    from datetime import datetime
    today = datetime.now(timezone("Asia/Kolkata"))
    # Saturday = 5, Sunday = 6
    return today.weekday() < 5
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-061: Implement Job Status API

**File**: `backend/app/api/scheduler.py`

**Description**: Implement API endpoint to list scheduled jobs and their status.

**Acceptance Criteria**:
- [ ] List all jobs for current user
- [ ] Show next run time
- [ ] Show job status
- [ ] Filter by strategy
- [ ] Admin endpoint for all jobs

**Code Reference**:
```python
from fastapi import APIRouter, Depends
from app.services.scheduler_service import get_scheduler
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])

@router.get("/jobs")
async def list_jobs(
    current_user: User = Depends(get_current_user)
):
    """List scheduled jobs for current user"""
    scheduler = await get_scheduler()
    
    jobs = []
    for job in scheduler.get_jobs():
        # Extract strategy_id from job_id
        parts = job.id.split("_")
        if len(parts) >= 2:
            job_type, strategy_id = parts[0], "_".join(parts[1:])
        else:
            continue
        
        # Filter by user's strategies
        # TODO: Implement user filtering based on strategy ownership
        
        jobs.append({
            "job_id": job.id,
            "strategy_id": strategy_id,
            "job_type": job_type,  # "buy" or "sell"
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        })
    
    return {"jobs": jobs}

@router.get("/jobs/{strategy_id}")
async def get_strategy_jobs(
    strategy_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get jobs for a specific strategy"""
    scheduler = await get_scheduler()
    
    buy_job = scheduler.scheduler.get_job(f"buy_{strategy_id}")
    sell_job = scheduler.scheduler.get_job(f"sell_{strategy_id}")
    
    return {
        "strategy_id": strategy_id,
        "buy_job": {
            "scheduled": buy_job is not None,
            "next_run": buy_job.next_run_time.isoformat() if buy_job and buy_job.next_run_time else None
        },
        "sell_job": {
            "scheduled": sell_job is not None,
            "next_run": sell_job.next_run_time.isoformat() if sell_job and sell_job.next_run_time else None
        }
    }

@router.post("/jobs/{strategy_id}/reschedule")
async def reschedule_strategy(
    strategy_id: str,
    current_user: User = Depends(get_current_user)
):
    """Reschedule jobs for a strategy"""
    from app.services.redis_service import get_active_strategy
    
    strategy = await get_active_strategy(strategy_id, current_user.id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    scheduler = await get_scheduler()
    await scheduler.cancel_strategy_jobs(strategy_id)
    await scheduler.schedule_buy_trigger(strategy)
    await scheduler.schedule_sell_trigger(strategy)
    
    return {"message": f"Strategy {strategy_id} rescheduled"}
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-062: Add Scheduler Error Handling

**File**: `backend/app/services/scheduler_service.py`

**Description**: Add error handling for scheduler failures with retry logic and notifications.

**Acceptance Criteria**:
- [ ] Catch job execution errors
- [ ] Retry failed jobs (configurable)
- [ ] Log failures with context
- [ ] Notify user on critical failures
- [ ] Update strategy status on failure

**Code Reference**:
```python
from apscheduler.events import (
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MISSED
)

def add_scheduler_listeners(self):
    """Add event listeners for scheduler events"""
    
    self.scheduler.add_listener(
        self._on_job_error,
        EVENT_JOB_ERROR
    )
    
    self.scheduler.add_listener(
        self._on_job_executed,
        EVENT_JOB_EXECUTED
    )
    
    self.scheduler.add_listener(
        self._on_job_missed,
        EVENT_JOB_MISSED
    )

async def _on_job_error(self, event):
    """Handle job execution error"""
    job_id = event.job_id
    exception = event.exception
    traceback = event.traceback
    
    logger.error(
        f"Job {job_id} failed with error: {exception}\n{traceback}"
    )
    
    # Extract strategy_id
    parts = job_id.split("_")
    if len(parts) >= 2:
        strategy_id = "_".join(parts[1:])
        
        # Update strategy status to ERROR
        from app.services.redis_service import update_strategy_state, publish_strategy_error
        
        await update_strategy_state(
            strategy_id,
            None,  # Need to lookup user_id
            {"last_error": str(exception)}
        )
        
        # Publish error event
        # await publish_strategy_error(user_id, strategy_id, str(exception))

async def _on_job_executed(self, event):
    """Handle successful job execution"""
    job_id = event.job_id
    logger.info(f"Job {job_id} executed successfully")

async def _on_job_missed(self, event):
    """Handle missed job (scheduler was down)"""
    job_id = event.job_id
    scheduled_time = event.scheduled_run_time
    
    logger.warning(
        f"Job {job_id} missed, was scheduled for {scheduled_time}"
    )
    
    # Optionally execute missed job immediately
    # self._execute_missed_job(job_id)
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-063: Implement Timezone Handling

**File**: `backend/app/services/scheduler_service.py`

**Description**: Implement proper timezone handling for IST (Asia/Kolkata) market.

**Acceptance Criteria**:
- [ ] All times in IST
- [ ] Proper timezone conversion
- [ ] Handle DST (not applicable for IST)
- [ ] Store times in UTC in DB
- [ ] Display times in user timezone

**Code Reference**:
```python
from pytz import timezone
from datetime import datetime, timedelta

IST = timezone("Asia/Kolkata")
UTC = timezone("UTC")

def to_ist(dt: datetime) -> datetime:
    """Convert datetime to IST"""
    if dt.tzinfo is None:
        dt = UTC.localize(dt)
    return dt.astimezone(IST)

def to_utc(dt: datetime) -> datetime:
    """Convert datetime to UTC"""
    if dt.tzinfo is None:
        dt = IST.localize(dt)
    return dt.astimezone(UTC)

def parse_time_to_ist_today(time_str: str) -> datetime:
    """Parse HH:MM:SS string to IST datetime for today"""
    hour, minute, second = map(int, time_str.split(":"))
    now_ist = datetime.now(IST)
    return now_ist.replace(hour=hour, minute=minute, second=second, microsecond=0)

def get_next_market_open() -> datetime:
    """Get next market open time"""
    now_ist = datetime.now(IST)
    market_open = now_ist.replace(hour=9, minute=15, second=0, microsecond=0)
    
    # If market has already opened today, get tomorrow
    if now_ist >= market_open:
        market_open += timedelta(days=1)
    
    # Skip weekends
    while market_open.weekday() >= 5:  # Saturday or Sunday
        market_open += timedelta(days=1)
    
    return market_open

def get_next_market_close() -> datetime:
    """Get next market close time"""
    now_ist = datetime.now(IST)
    market_close = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)
    
    # If market has already closed today, get tomorrow
    if now_ist >= market_close:
        market_close += timedelta(days=1)
    
    # Skip weekends
    while market_close.weekday() >= 5:
        market_close += timedelta(days=1)
    
    return market_close
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-064: Write Scheduler Unit Tests

**File**: `backend/tests/test_scheduler.py`

**Description**: Write unit tests for scheduler service with mocked time.

**Acceptance Criteria**:
- [ ] Test job scheduling
- [ ] Test job cancellation
- [ ] Test market hours validation
- [ ] Test timezone handling
- [ ] Test error handling
- [ ] Mock APScheduler for unit tests

**Code Reference**:
```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, time as dt_time
from app.services.scheduler_service import (
    SchedulerService,
    validate_market_hours,
    MarketHoursError,
    is_market_open,
    to_ist,
    parse_time_to_ist_today
)

class TestMarketHoursValidation:
    
    def test_valid_market_hours(self):
        """Test valid buy/sell times within market hours"""
        assert validate_market_hours("09:30:00", "15:00:00") is True
        assert validate_market_hours("10:00:00", "14:30:00") is True
    
    def test_buy_before_market_open(self):
        """Test buy time before market opens"""
        with pytest.raises(MarketHoursError):
            validate_market_hours("09:00:00", "15:00:00")
    
    def test_sell_after_market_close(self):
        """Test sell time after market closes"""
        with pytest.raises(MarketHoursError):
            validate_market_hours("09:30:00", "16:00:00")
    
    def test_sell_before_buy(self):
        """Test sell time before buy time"""
        with pytest.raises(MarketHoursError):
            validate_market_hours("14:00:00", "10:00:00")

class TestTimezoneHandling:
    
    def test_to_ist(self):
        """Test UTC to IST conversion"""
        from pytz import UTC, timezone
        utc_dt = UTC.localize(datetime(2025, 1, 1, 4, 0, 0))
        ist_dt = to_ist(utc_dt)
        assert ist_dt.hour == 9  # IST is UTC+5:30
        assert ist_dt.minute == 30
    
    def test_parse_time_to_ist(self):
        """Test parsing time string to IST datetime"""
        result = parse_time_to_ist_today("09:30:00")
        assert result.hour == 9
        assert result.minute == 30
        assert result.second == 0
        assert str(result.tzinfo) == "Asia/Kolkata"

class TestSchedulerService:
    
    @pytest.fixture
    def scheduler_service(self):
        return SchedulerService()
    
    @pytest.mark.asyncio
    async def test_schedule_buy_trigger(self, scheduler_service):
        """Test scheduling buy trigger"""
        with patch.object(scheduler_service, 'scheduler') as mock_scheduler:
            mock_scheduler.get_job.return_value = None
            mock_scheduler.add_job = Mock()
            
            strategy = {
                "id": "str_123",
                "buy_time": "10:00:00",
                "sell_time": "14:00:00"
            }
            
            await scheduler_service.schedule_buy_trigger(strategy)
            
            mock_scheduler.add_job.assert_called_once()
            call_kwargs = mock_scheduler.add_job.call_args
            assert call_kwargs.kwargs["id"] == "buy_str_123"
    
    @pytest.mark.asyncio
    async def test_cancel_strategy_jobs(self, scheduler_service):
        """Test cancelling strategy jobs"""
        with patch.object(scheduler_service, 'scheduler') as mock_scheduler:
            mock_scheduler.get_job.return_value = Mock()
            mock_scheduler.remove_job = Mock()
            
            result = await scheduler_service.cancel_strategy_jobs("str_123")
            
            assert "buy" in result
            assert "sell" in result
            assert mock_scheduler.remove_job.call_count == 2
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/app/services/scheduler_service.py` | Create | Scheduler service |
| `backend/app/api/scheduler.py` | Create | Scheduler API endpoints |
| `backend/app/main.py` | Modify | Add scheduler startup |
| `backend/tests/test_scheduler.py` | Create | Unit tests |

---

## Environment Variables Required

```bash
# Scheduler Configuration
SCHEDULER_TIMEZONE="Asia/Kolkata"
REDIS_SCHEDULER_DB=1
```

---

## Definition of Done

- [ ] All 10 tasks completed
- [ ] Unit tests passing
- [ ] Jobs schedule correctly at specified times
- [ ] Market hours validation working
- [ ] Timezone handling correct
- [ ] Jobs persist across restarts
- [ ] Code reviewed and approved

---

## Next Phase

After completing Phase 5, proceed to [Phase 6: Market Data Listener](./phase-06-market-data-listener.md)
