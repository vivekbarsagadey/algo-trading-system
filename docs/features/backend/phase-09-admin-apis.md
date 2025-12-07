---
goal: Phase 9 - Admin APIs for Platform Management
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Backend Engineering Team
status: Planned
tags: [backend, admin, rbac, management, monitoring]
---

# Phase 9: Admin APIs

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

## Goal

**GOAL-009**: Implement admin-only APIs for user management, system monitoring, and platform configuration

## Overview

This phase implements administrative endpoints that are restricted to users with Admin role. These APIs enable platform administrators to manage users, view system-wide analytics, monitor broker connections, and configure system settings.

---

## Prerequisites

- Phase 1-8 completed
- RBAC implemented in authentication
- User roles defined (Admin, User, Broker)

## Dependencies

```txt
# Uses existing dependencies
```

---

## Implementation Tasks

### TASK-094: Create Admin Role Decorator

**File**: `backend/app/api/admin.py`

**Description**: Create decorator/dependency to restrict endpoints to Admin role.

**Acceptance Criteria**:
- [ ] Verify user has Admin role
- [ ] Return 403 if not admin
- [ ] Log admin access attempts
- [ ] Reusable across endpoints

**Code Reference**:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from functools import wraps
import logging

from app.api.auth import get_current_user
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to require admin role"""
    if current_user.role != UserRole.ADMIN:
        logger.warning(
            f"Non-admin user {current_user.id} attempted admin access"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    logger.info(f"Admin access granted to {current_user.id}")
    return current_user

def admin_only(func):
    """Decorator for admin-only endpoints"""
    @wraps(func)
    async def wrapper(*args, current_user: User = Depends(require_admin), **kwargs):
        return await func(*args, current_user=current_user, **kwargs)
    return wrapper
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-095: Implement User Management API

**File**: `backend/app/api/admin.py`

**Description**: Implement CRUD APIs for user management (list, view, update, deactivate).

**Acceptance Criteria**:
- [ ] List all users with pagination
- [ ] View user details
- [ ] Update user role
- [ ] Deactivate/reactivate user
- [ ] Filter by role/status

**Code Reference**:
```python
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from pydantic import BaseModel

from app.core.database import get_db

class UserListResponse(BaseModel):
    users: List[dict]
    total: int
    page: int
    limit: int

class UserUpdateRequest(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None

@router.get("/users")
async def list_users(
    page: int = 1,
    limit: int = 20,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> UserListResponse:
    """List all users with pagination and filters"""
    query = select(User)
    
    # Apply filters
    if role:
        query = query.where(User.role == UserRole(role))
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if search:
        query = query.where(
            User.email.ilike(f"%{search}%") |
            User.name.ilike(f"%{search}%")
        )
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Paginate
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(User.created_at.desc())
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return UserListResponse(
        users=[u.to_admin_dict() for u in users],
        total=total,
        page=page,
        limit=limit
    )

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get user details"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user.to_admin_dict()

@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    update: UserUpdateRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update user (role, status)"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent self-demotion
    if user.id == current_user.id and update.role:
        raise HTTPException(
            status_code=400,
            detail="Cannot change your own role"
        )
    
    if update.role:
        user.role = UserRole(update.role)
    if update.is_active is not None:
        user.is_active = update.is_active
    
    await db.commit()
    
    logger.info(
        f"Admin {current_user.id} updated user {user_id}: "
        f"role={update.role}, is_active={update.is_active}"
    )
    
    return {"status": "updated", "user": user.to_admin_dict()}

@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate a user account"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate your own account"
        )
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    await db.commit()
    
    logger.info(f"Admin {current_user.id} deactivated user {user_id}")
    
    return {"status": "deactivated", "user_id": user_id}
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-096: Implement System Dashboard API

**File**: `backend/app/api/admin.py`

**Description**: Implement dashboard API with system-wide statistics.

**Acceptance Criteria**:
- [ ] Total users count
- [ ] Active strategies count
- [ ] Orders today count
- [ ] System health status
- [ ] Broker connection status

**Code Reference**:
```python
from datetime import datetime, timedelta

@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get admin dashboard statistics"""
    from app.services.redis_service import get_all_active_strategies
    from app.services.listener_manager import get_listener_manager
    
    # User statistics
    total_users_result = await db.execute(
        select(func.count()).select_from(User)
    )
    total_users = total_users_result.scalar()
    
    active_users_result = await db.execute(
        select(func.count()).select_from(User).where(User.is_active == True)
    )
    active_users = active_users_result.scalar()
    
    # Strategy statistics
    active_strategies = await get_all_active_strategies()
    running_count = len([s for s in active_strategies if s.get("status") == "RUNNING"])
    
    # Order statistics (today)
    today = datetime.utcnow().date()
    orders_today_result = await db.execute(
        select(func.count()).select_from(OrderLog).where(
            OrderLog.attempted_at >= datetime.combine(today, datetime.min.time())
        )
    )
    orders_today = orders_today_result.scalar()
    
    # Broker connection status
    listener_manager = get_listener_manager()
    listener_health = await listener_manager.get_all_health()
    
    # System health
    from app.services.redis_service import get_redis
    redis = await get_redis()
    redis_healthy = await redis.health_check()
    
    return {
        "users": {
            "total": total_users,
            "active": active_users
        },
        "strategies": {
            "running": running_count,
            "total_active": len(active_strategies)
        },
        "orders": {
            "today": orders_today
        },
        "system_health": {
            "redis": "healthy" if redis_healthy else "unhealthy",
            "database": "healthy",  # Would check DB connection
            "scheduler": "healthy"   # Would check scheduler status
        },
        "broker_connections": listener_health,
        "timestamp": datetime.utcnow().isoformat()
    }
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-097: Implement All Strategies View

**File**: `backend/app/api/admin.py`

**Description**: Implement API to view all strategies across all users.

**Acceptance Criteria**:
- [ ] List all strategies
- [ ] Filter by status, user, symbol
- [ ] Pagination support
- [ ] Include user info
- [ ] Sort options

**Code Reference**:
```python
from app.models.strategy import Strategy, StrategyStatus

@router.get("/strategies")
async def list_all_strategies(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    user_id: Optional[str] = None,
    symbol: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all strategies across all users"""
    query = select(Strategy)
    
    # Apply filters
    if status:
        query = query.where(Strategy.status == StrategyStatus(status))
    if user_id:
        query = query.where(Strategy.user_id == user_id)
    if symbol:
        query = query.where(Strategy.symbol == symbol.upper())
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Paginate
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Strategy.created_at.desc())
    
    # Join user for user info
    query = query.options(selectinload(Strategy.user))
    
    result = await db.execute(query)
    strategies = result.scalars().all()
    
    return {
        "strategies": [
            {
                **s.to_dict(),
                "user_email": s.user.email,
                "user_name": s.user.name
            }
            for s in strategies
        ],
        "total": total,
        "page": page,
        "limit": limit
    }

@router.post("/strategies/{strategy_id}/stop")
async def admin_stop_strategy(
    strategy_id: str,
    reason: str = "Stopped by admin",
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin force stop a strategy"""
    from app.services.redis_service import update_strategy_state
    from app.services.scheduler_service import get_scheduler
    
    result = await db.execute(
        select(Strategy).where(Strategy.id == strategy_id)
    )
    strategy = result.scalar_one_or_none()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    # Stop in Redis
    await update_strategy_state(
        strategy_id,
        strategy.user_id,
        {
            "status": "STOPPED",
            "stop_reason": f"ADMIN: {reason}",
            "stopped_by": current_user.id,
            "stopped_at": datetime.utcnow().isoformat()
        }
    )
    
    # Cancel scheduled jobs
    scheduler = await get_scheduler()
    await scheduler.cancel_strategy_jobs(strategy_id)
    
    # Update DB
    strategy.status = StrategyStatus.STOPPED
    await db.commit()
    
    logger.info(
        f"Admin {current_user.id} stopped strategy {strategy_id}: {reason}"
    )
    
    return {"status": "stopped", "strategy_id": strategy_id}
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-098: Implement Broker Status API

**File**: `backend/app/api/admin.py`

**Description**: Implement API to view all broker connections and their status.

**Acceptance Criteria**:
- [ ] List all broker connections
- [ ] Show connection status
- [ ] Show last sync time
- [ ] Show error counts
- [ ] Support reconnect action

**Code Reference**:
```python
from app.models.broker import BrokerConnection

@router.get("/brokers")
async def list_broker_connections(
    broker_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all broker connections"""
    query = select(BrokerConnection)
    
    if broker_type:
        query = query.where(BrokerConnection.broker_name == broker_type)
    if status:
        query = query.where(BrokerConnection.status == status)
    
    query = query.options(selectinload(BrokerConnection.user))
    
    result = await db.execute(query)
    connections = result.scalars().all()
    
    # Get live status from listener manager
    from app.services.listener_manager import get_listener_manager
    listener_manager = get_listener_manager()
    
    broker_list = []
    for conn in connections:
        # Check live WebSocket status
        live_status = None
        if conn.user_id in listener_manager.listeners:
            if conn.broker_name in listener_manager.listeners[conn.user_id]:
                listener = listener_manager.listeners[conn.user_id][conn.broker_name]
                live_status = await listener.health_check()
        
        broker_list.append({
            "id": conn.id,
            "user_id": conn.user_id,
            "user_email": conn.user.email,
            "broker_name": conn.broker_name,
            "status": conn.status,
            "is_active": conn.is_active,
            "last_connected": conn.last_connected.isoformat() if conn.last_connected else None,
            "error_count": conn.error_count,
            "live_status": live_status
        })
    
    return {"brokers": broker_list}

@router.post("/brokers/{broker_id}/reconnect")
async def reconnect_broker(
    broker_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Force reconnect a broker WebSocket"""
    result = await db.execute(
        select(BrokerConnection).where(BrokerConnection.id == broker_id)
    )
    conn = result.scalar_one_or_none()
    
    if not conn:
        raise HTTPException(status_code=404, detail="Broker connection not found")
    
    from app.services.listener_manager import get_listener_manager
    from app.services.broker_service import get_broker_config
    
    listener_manager = get_listener_manager()
    
    # Stop existing listener
    await listener_manager.stop_listener(conn.user_id, conn.broker_name)
    
    # Get config and restart
    config = await get_broker_config(conn.user_id, conn.broker_name)
    await listener_manager.start_listener(conn.user_id, conn.broker_name, config)
    
    logger.info(
        f"Admin {current_user.id} reconnected broker {broker_id}"
    )
    
    return {"status": "reconnected", "broker_id": broker_id}
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-099: Implement System Logs API

**File**: `backend/app/api/admin.py`

**Description**: Implement API to view system logs and audit trail.

**Acceptance Criteria**:
- [ ] View order logs
- [ ] View error logs
- [ ] Filter by date range
- [ ] Filter by user
- [ ] Export capability

**Code Reference**:
```python
from datetime import date

@router.get("/logs/orders")
async def get_order_logs(
    page: int = 1,
    limit: int = 50,
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get order execution logs"""
    query = select(OrderLog)
    
    if user_id:
        query = query.where(OrderLog.user_id == user_id)
    if status:
        query = query.where(OrderLog.status == status)
    if start_date:
        query = query.where(OrderLog.attempted_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.where(OrderLog.attempted_at <= datetime.combine(end_date, datetime.max.time()))
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Paginate
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(OrderLog.attempted_at.desc())
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return {
        "logs": [l.to_dict() for l in logs],
        "total": total,
        "page": page,
        "limit": limit
    }

@router.get("/logs/errors")
async def get_error_logs(
    page: int = 1,
    limit: int = 50,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get system error logs"""
    # Query order logs with errors
    query = select(OrderLog).where(OrderLog.status == "ERROR")
    
    if start_date:
        query = query.where(OrderLog.attempted_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.where(OrderLog.attempted_at <= datetime.combine(end_date, datetime.max.time()))
    
    # Paginate
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(OrderLog.attempted_at.desc())
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return {
        "errors": [
            {
                **l.to_dict(),
                "error_message": l.error_message
            }
            for l in logs
        ],
        "page": page,
        "limit": limit
    }

@router.get("/logs/export")
async def export_logs(
    log_type: str,  # "orders" or "errors"
    start_date: date,
    end_date: date,
    format: str = "csv",  # "csv" or "json"
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Export logs as CSV or JSON"""
    from fastapi.responses import StreamingResponse
    import csv
    import io
    
    if log_type == "orders":
        query = select(OrderLog)
    else:
        query = select(OrderLog).where(OrderLog.status == "ERROR")
    
    query = query.where(
        OrderLog.attempted_at >= datetime.combine(start_date, datetime.min.time()),
        OrderLog.attempted_at <= datetime.combine(end_date, datetime.max.time())
    ).order_by(OrderLog.attempted_at.desc())
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "id", "user_id", "strategy_id", "order_type",
            "status", "attempted_at", "completed_at", "error_message"
        ])
        
        for log in logs:
            writer.writerow([
                log.id, log.user_id, log.strategy_id, log.order_type,
                log.status, log.attempted_at, log.completed_at, log.error_message
            ])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=logs_{start_date}_{end_date}.csv"
            }
        )
    else:
        return {"logs": [l.to_dict() for l in logs]}
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-100: Implement System Configuration API

**File**: `backend/app/api/admin.py`

**Description**: Implement API to view and update system configuration.

**Acceptance Criteria**:
- [ ] View current configuration
- [ ] Update configuration
- [ ] Validate changes
- [ ] Persist to database/config
- [ ] Reload without restart

**Code Reference**:
```python
from pydantic import BaseModel
from typing import Dict, Any

class SystemConfig(BaseModel):
    max_strategies_per_user: int = 10
    max_order_retries: int = 3
    order_timeout_seconds: int = 30
    market_open_time: str = "09:15:00"
    market_close_time: str = "15:30:00"
    enable_playground: bool = True
    maintenance_mode: bool = False

# Store config in database or Redis
CONFIG_KEY = "system:config"

@router.get("/config")
async def get_system_config(
    current_user: User = Depends(require_admin)
):
    """Get current system configuration"""
    from app.services.redis_service import get_redis
    
    redis = await get_redis()
    config_json = await redis.get(CONFIG_KEY)
    
    if config_json:
        return json.loads(config_json)
    else:
        # Return defaults
        return SystemConfig().dict()

@router.put("/config")
async def update_system_config(
    config: SystemConfig,
    current_user: User = Depends(require_admin)
):
    """Update system configuration"""
    from app.services.redis_service import get_redis
    
    redis = await get_redis()
    await redis.set(CONFIG_KEY, json.dumps(config.dict()))
    
    logger.info(f"Admin {current_user.id} updated system config: {config.dict()}")
    
    return {"status": "updated", "config": config.dict()}

@router.post("/config/reload")
async def reload_config(
    current_user: User = Depends(require_admin)
):
    """Reload configuration across all services"""
    from app.core.config import reload_config
    
    await reload_config()
    
    logger.info(f"Admin {current_user.id} triggered config reload")
    
    return {"status": "reloaded"}

@router.post("/maintenance")
async def toggle_maintenance(
    enable: bool,
    current_user: User = Depends(require_admin)
):
    """Enable/disable maintenance mode"""
    from app.services.redis_service import get_redis
    
    redis = await get_redis()
    config_json = await redis.get(CONFIG_KEY)
    
    if config_json:
        config = json.loads(config_json)
    else:
        config = SystemConfig().dict()
    
    config["maintenance_mode"] = enable
    await redis.set(CONFIG_KEY, json.dumps(config))
    
    logger.warning(
        f"Admin {current_user.id} {'enabled' if enable else 'disabled'} maintenance mode"
    )
    
    return {"maintenance_mode": enable}
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-101: Write Admin API Tests

**File**: `backend/tests/test_admin.py`

**Description**: Write tests for admin API endpoints.

**Acceptance Criteria**:
- [ ] Test role-based access
- [ ] Test user management
- [ ] Test strategy management
- [ ] Test dashboard API
- [ ] Test configuration API

**Code Reference**:
```python
import pytest
from httpx import AsyncClient
from app.main import app
from app.models.user import UserRole

class TestAdminAccess:
    
    @pytest.fixture
    def admin_token(self, test_admin_user):
        """Get token for admin user"""
        from app.core.security import create_access_token
        return create_access_token({"sub": test_admin_user.id})
    
    @pytest.fixture
    def user_token(self, test_regular_user):
        """Get token for regular user"""
        from app.core.security import create_access_token
        return create_access_token({"sub": test_regular_user.id})
    
    @pytest.mark.asyncio
    async def test_admin_can_access(self, client, admin_token):
        """Test admin can access admin endpoints"""
        response = await client.get(
            "/admin/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_user_cannot_access(self, client, user_token):
        """Test regular user cannot access admin endpoints"""
        response = await client.get(
            "/admin/dashboard",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403

class TestUserManagement:
    
    @pytest.mark.asyncio
    async def test_list_users(self, client, admin_token):
        """Test listing users"""
        response = await client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert "users" in response.json()
        assert "total" in response.json()
    
    @pytest.mark.asyncio
    async def test_update_user_role(self, client, admin_token, test_regular_user):
        """Test updating user role"""
        response = await client.patch(
            f"/admin/users/{test_regular_user.id}",
            json={"role": "Broker"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["user"]["role"] == "Broker"
    
    @pytest.mark.asyncio
    async def test_cannot_self_demote(self, client, admin_token, test_admin_user):
        """Test admin cannot change own role"""
        response = await client.patch(
            f"/admin/users/{test_admin_user.id}",
            json={"role": "User"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400

class TestSystemConfig:
    
    @pytest.mark.asyncio
    async def test_get_config(self, client, admin_token):
        """Test getting system config"""
        response = await client.get(
            "/admin/config",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert "max_strategies_per_user" in response.json()
    
    @pytest.mark.asyncio
    async def test_update_config(self, client, admin_token):
        """Test updating system config"""
        response = await client.put(
            "/admin/config",
            json={
                "max_strategies_per_user": 20,
                "max_order_retries": 5,
                "order_timeout_seconds": 60,
                "market_open_time": "09:15:00",
                "market_close_time": "15:30:00",
                "enable_playground": True,
                "maintenance_mode": False
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/app/api/admin.py` | Create | Admin API endpoints |
| `backend/app/main.py` | Modify | Add admin router |
| `backend/tests/test_admin.py` | Create | Admin API tests |

---

## Environment Variables Required

```bash
# No additional env vars required
```

---

## Definition of Done

- [ ] All 8 tasks completed
- [ ] Role-based access working
- [ ] User management working
- [ ] Dashboard API returning data
- [ ] Broker status working
- [ ] Logs API working
- [ ] Configuration API working
- [ ] Tests passing
- [ ] Code reviewed and approved

---

## Next Phase

After completing Phase 9, proceed to [Phase 10: Analytics & Reporting](./phase-10-analytics-reporting.md)
