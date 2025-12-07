---
goal: Phase 1 - Authentication & Authorization Module
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Backend Engineering Team
status: Planned
tags: [backend, authentication, jwt, rbac, security]
---

# Phase 1: Authentication & Authorization Module

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

## Goal

**GOAL-001**: Implement secure user authentication with JWT and role-based access control

## Overview

This phase establishes the foundation for user authentication and authorization. It includes user registration, login, JWT token management, and role-based access control (RBAC) for Admin, User, and Broker roles.

---

## Prerequisites

- Python 3.11+ installed
- PostgreSQL database running
- Redis running (for token blacklist)
- Project structure created with FastAPI

## Dependencies

```txt
fastapi>=0.100.0
pydantic>=2.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
sqlalchemy>=2.0.0
asyncpg>=0.28.0
```

---

## Implementation Tasks

### TASK-001: Create Registration Endpoint

**File**: `backend/app/api/auth.py`

**Description**: Create `/auth/register` endpoint with email validation, password strength enforcement (min 6 chars), bcrypt password hashing, and `usr_` prefixed user ID generation.

**Acceptance Criteria**:
- [ ] Endpoint accepts `email` and `password` in request body
- [ ] Email format is validated (valid email regex)
- [ ] Password must be minimum 6 characters
- [ ] Password is hashed using bcrypt before storage
- [ ] User ID is generated with `usr_` prefix (e.g., `usr_abc123def456`)
- [ ] Returns 201 Created with user_id and JWT token
- [ ] Returns 400 Bad Request for invalid input
- [ ] Returns 409 Conflict if email already exists

**Code Reference**:
```python
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class RegisterResponse(BaseModel):
    user_id: str
    token: str

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    # 1. Check if email exists
    # 2. Hash password with bcrypt
    # 3. Generate usr_ prefixed ID
    # 4. Save to database
    # 5. Generate JWT token
    # 6. Return response
    pass
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-002: Create Login Endpoint

**File**: `backend/app/api/auth.py`

**Description**: Create `/auth/login` endpoint that validates credentials, generates JWT access token (15 min expiry) and refresh token (7 days expiry), and returns user role in response.

**Acceptance Criteria**:
- [ ] Endpoint accepts `email` and `password`
- [ ] Validates credentials against database
- [ ] Generates JWT access token with 15-minute expiry
- [ ] Generates refresh token with 7-day expiry
- [ ] Returns access_token, refresh_token, token_type, expires_in, and user role
- [ ] Updates `last_login_at` timestamp in database
- [ ] Returns 401 Unauthorized for invalid credentials

**Code Reference**:
```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes in seconds
    role: str

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    # 1. Find user by email
    # 2. Verify password hash
    # 3. Generate access token (15 min)
    # 4. Generate refresh token (7 days)
    # 5. Update last_login_at
    # 6. Return tokens and role
    pass
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-003: Create Token Refresh Endpoint

**File**: `backend/app/api/auth.py`

**Description**: Create `/auth/refresh` endpoint that validates refresh token, issues new access token, and maintains token rotation for security.

**Acceptance Criteria**:
- [ ] Endpoint accepts `refresh_token` in request body
- [ ] Validates refresh token signature and expiry
- [ ] Checks token is not in blacklist (Redis)
- [ ] Issues new access token (15 min expiry)
- [ ] Optionally rotates refresh token
- [ ] Returns 401 if refresh token is invalid or expired

**Code Reference**:
```python
class RefreshRequest(BaseModel):
    refresh_token: str

class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 900

@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(request: RefreshRequest):
    # 1. Decode and validate refresh token
    # 2. Check if token is blacklisted in Redis
    # 3. Generate new access token
    # 4. Return new access token
    pass
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-004: Create Logout Endpoint

**File**: `backend/app/api/auth.py`

**Description**: Create `/auth/logout` endpoint that invalidates refresh token by adding it to Redis blacklist.

**Acceptance Criteria**:
- [ ] Endpoint requires valid access token in Authorization header
- [ ] Accepts `refresh_token` in request body
- [ ] Adds refresh token to Redis blacklist with TTL matching token expiry
- [ ] Returns 200 OK on success
- [ ] Returns 401 if access token is invalid

**Code Reference**:
```python
class LogoutRequest(BaseModel):
    refresh_token: str

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(request: LogoutRequest, current_user: User = Depends(get_current_user)):
    # 1. Add refresh token to Redis blacklist
    # 2. Set TTL to match token expiry
    # 3. Return success message
    pass
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-005: Implement Security Utilities

**File**: `backend/app/core/security.py`

**Description**: Implement JWT token creation/validation, password hashing with bcrypt, and token blacklist checking utilities.

**Acceptance Criteria**:
- [ ] `hash_password(password: str) -> str` - hashes password with bcrypt
- [ ] `verify_password(plain: str, hashed: str) -> bool` - verifies password
- [ ] `create_access_token(data: dict, expires_delta: timedelta) -> str` - creates JWT
- [ ] `create_refresh_token(data: dict) -> str` - creates refresh JWT
- [ ] `decode_token(token: str) -> dict` - decodes and validates JWT
- [ ] `is_token_blacklisted(token: str) -> bool` - checks Redis blacklist
- [ ] `blacklist_token(token: str, ttl: int)` - adds token to blacklist

**Code Reference**:
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-006: Create Role-Based Access Control Middleware

**File**: `backend/app/core/rbac.py`

**Description**: Create RBAC middleware defining Admin, User, Broker roles with permission matrix for endpoint protection.

**Acceptance Criteria**:
- [ ] Define `Role` enum with ADMIN, USER, BROKER values
- [ ] Create permission matrix defining allowed actions per role
- [ ] Create `check_permission(role: Role, action: str) -> bool` function
- [ ] Define action constants: CREATE_USER, DELETE_USER, VIEW_ALL_STRATEGIES, etc.
- [ ] Document which roles can access which endpoints

**Code Reference**:
```python
from enum import Enum
from typing import List

class Role(str, Enum):
    ADMIN = "Admin"
    USER = "User"
    BROKER = "Broker"

class Permission(str, Enum):
    # User Management
    CREATE_USER = "create_user"
    VIEW_ALL_USERS = "view_all_users"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    
    # Strategy Management
    CREATE_STRATEGY = "create_strategy"
    VIEW_OWN_STRATEGIES = "view_own_strategies"
    VIEW_ALL_STRATEGIES = "view_all_strategies"
    FORCE_STOP_STRATEGY = "force_stop_strategy"
    
    # System
    VIEW_SYSTEM_HEALTH = "view_system_health"
    VIEW_ANALYTICS = "view_analytics"

ROLE_PERMISSIONS: dict[Role, List[Permission]] = {
    Role.ADMIN: [p for p in Permission],  # All permissions
    Role.USER: [
        Permission.CREATE_STRATEGY,
        Permission.VIEW_OWN_STRATEGIES,
    ],
    Role.BROKER: [
        Permission.VIEW_ANALYTICS,
    ],
}

def check_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, [])
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-007: Create get_current_user Dependency

**File**: `backend/app/core/security.py`

**Description**: Add `get_current_user` FastAPI dependency that extracts and validates JWT from Authorization header.

**Acceptance Criteria**:
- [ ] Extracts Bearer token from Authorization header
- [ ] Decodes and validates JWT token
- [ ] Checks if token is blacklisted
- [ ] Fetches user from database
- [ ] Returns User object if valid
- [ ] Raises 401 HTTPException if invalid

**Code Reference**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    
    # Check if token is blacklisted
    if await is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token has been revoked")
    
    # Decode token
    payload = decode_token(token)
    
    # Validate token type
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    
    # Get user from database
    user_id = payload.get("sub")
    user = await get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive")
    
    return user
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-008: Create require_role Dependency

**File**: `backend/app/core/security.py`

**Description**: Add `require_role(roles: List[str])` dependency for role-based endpoint protection.

**Acceptance Criteria**:
- [ ] Accepts list of allowed roles
- [ ] Works as a dependency that wraps get_current_user
- [ ] Validates user's role against allowed roles
- [ ] Returns user if role matches
- [ ] Raises 403 Forbidden if role doesn't match

**Code Reference**:
```python
from typing import List
from functools import wraps

def require_role(allowed_roles: List[str]):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker

# Usage in endpoint:
# @router.get("/admin/users")
# async def list_users(user: User = Depends(require_role(["Admin"]))):
#     pass
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-009: Create User SQLAlchemy Model

**File**: `backend/app/models/user.py`

**Description**: Create User SQLAlchemy model with all required fields including role, is_active, and timestamps.

**Acceptance Criteria**:
- [ ] `id` - String primary key with `usr_` prefix
- [ ] `email` - Unique, indexed, not null
- [ ] `hashed_password` - String, not null
- [ ] `role` - String, default "User", enum validation
- [ ] `is_active` - Boolean, default True
- [ ] `created_at` - DateTime, auto-set on creation
- [ ] `last_login_at` - DateTime, nullable, updated on login
- [ ] Proper indexes on email and role columns

**Code Reference**:
```python
from sqlalchemy import Column, String, Boolean, DateTime, Index
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

def generate_user_id() -> str:
    return f"usr_{uuid.uuid4().hex[:12]}"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(50), primary_key=True, default=generate_user_id)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="User")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index('idx_users_role', 'role'),
        Index('idx_users_active', 'is_active'),
    )
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-010: Create Authentication Service

**File**: `backend/app/services/auth_service.py`

**Description**: Create authentication service with `register_user()`, `authenticate_user()`, and `refresh_access_token()` functions.

**Acceptance Criteria**:
- [ ] `register_user(email, password) -> User` - creates new user
- [ ] `authenticate_user(email, password) -> User | None` - validates credentials
- [ ] `refresh_access_token(refresh_token) -> str` - issues new access token
- [ ] `get_user_by_email(email) -> User | None` - fetches user
- [ ] `get_user_by_id(id) -> User | None` - fetches user
- [ ] All functions are async
- [ ] Proper error handling

**Code Reference**:
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, decode_token

async def register_user(db: AsyncSession, email: str, password: str) -> User:
    # Check if user exists
    existing = await get_user_by_email(db, email)
    if existing:
        raise ValueError("Email already registered")
    
    # Create user
    user = User(
        email=email,
        hashed_password=hash_password(password),
        role="User"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-011: Add Password Reset Flow

**File**: `backend/app/api/auth.py`

**Description**: Add `/auth/forgot-password` and `/auth/reset-password` endpoints for password recovery.

**Acceptance Criteria**:
- [ ] `/auth/forgot-password` - accepts email, generates reset token, (logs token for MVP)
- [ ] Reset token expires in 1 hour
- [ ] Reset token stored in Redis with user_id mapping
- [ ] `/auth/reset-password` - accepts token and new password
- [ ] Validates reset token and expiry
- [ ] Updates user password
- [ ] Invalidates reset token after use
- [ ] Returns appropriate success/error messages

**Code Reference**:
```python
import secrets

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, request.email)
    if user:
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        # Store in Redis with 1 hour TTL
        await redis.setex(f"reset:{reset_token}", 3600, user.id)
        # In production: send email
        # For MVP: log token
        logger.info(f"Password reset token for {request.email}: {reset_token}")
    
    # Always return success to prevent email enumeration
    return {"message": "If email exists, reset instructions have been sent"}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    # Get user_id from Redis
    user_id = await redis.get(f"reset:{request.token}")
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Update password
    user = await get_user_by_id(db, user_id)
    user.hashed_password = hash_password(request.new_password)
    await db.commit()
    
    # Invalidate token
    await redis.delete(f"reset:{request.token}")
    
    return {"message": "Password has been reset successfully"}
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-012: Write Authentication Unit Tests

**File**: `backend/tests/test_auth.py`

**Description**: Write comprehensive unit tests for all authentication endpoints.

**Acceptance Criteria**:
- [ ] Test successful registration
- [ ] Test registration with existing email (409)
- [ ] Test registration with invalid email format (400)
- [ ] Test registration with short password (400)
- [ ] Test successful login
- [ ] Test login with wrong password (401)
- [ ] Test login with non-existent email (401)
- [ ] Test token refresh with valid token
- [ ] Test token refresh with invalid token (401)
- [ ] Test logout with token blacklisting
- [ ] Test password reset flow
- [ ] Test accessing protected endpoint without token (401)
- [ ] Test accessing admin endpoint as User (403)

**Code Reference**:
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        assert data["user_id"].startswith("usr_")
        assert "token" in data

@pytest.mark.asyncio
async def test_register_duplicate_email():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First registration
        await client.post("/auth/register", json={
            "email": "dupe@example.com",
            "password": "password123"
        })
        # Second registration with same email
        response = await client.post("/auth/register", json={
            "email": "dupe@example.com",
            "password": "password456"
        })
        assert response.status_code == 409

@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register first
        await client.post("/auth/register", json={
            "email": "login@example.com",
            "password": "password123"
        })
        # Login
        response = await client.post("/auth/login", json={
            "email": "login@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["role"] == "User"

@pytest.mark.asyncio
async def test_login_wrong_password():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/login", json={
            "email": "login@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
```

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/app/api/auth.py` | Create | Authentication endpoints |
| `backend/app/core/security.py` | Create | JWT and password utilities |
| `backend/app/core/rbac.py` | Create | Role-based access control |
| `backend/app/models/user.py` | Create | User SQLAlchemy model |
| `backend/app/services/auth_service.py` | Create | Authentication business logic |
| `backend/tests/test_auth.py` | Create | Authentication tests |
| `backend/alembic/versions/xxxx_add_user_table.py` | Create | Database migration |

---

## Environment Variables Required

```bash
# JWT Configuration
JWT_SECRET_KEY="your-super-secret-key-at-least-32-chars"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/algo_trading"

# Redis (for token blacklist)
REDIS_URL="redis://localhost:6379/0"
```

---

## Definition of Done

- [ ] All 12 tasks completed
- [ ] All unit tests passing
- [ ] Code reviewed and approved
- [ ] Database migration created and tested
- [ ] API documentation updated (OpenAPI/Swagger)
- [ ] Security review completed
- [ ] No linting errors

---

## Next Phase

After completing Phase 1, proceed to [Phase 2: Broker Integration Module](./phase-02-broker-integration.md)
