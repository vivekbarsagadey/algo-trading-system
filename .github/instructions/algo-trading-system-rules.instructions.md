---
applyTo: "**"
---

# Algo Trading System Project-Specific Rules

> **LLM Knowledge Assumption**: This guide contains **ONLY high-level Algo Trading System-specific rules**. For detailed implementation rules, see specialized instruction files.

**Last Updated**: December 7, 2025  
**Stack**: FastAPI • Python 3.11+ • React Native/Expo • Next.js 16 • Redis • PostgreSQL • AWS

---

## Specialized Instruction Files

This project has **three specialized instruction files** for different areas:

### 1. **Backend Python Rules** (`backend-python-rules.instructions.md`)
- **Agent**: `expert-python`
- **Applies to**: `backend/**`
- **Contains**: FastAPI, SQLAlchemy, Redis, Celery, execution engine patterns
- **Use for**: Backend development, API design, database operations, broker integrations

### 2. **Admin Web App Rules** (`admin-web-app-rules.instructions.md`)
- **Agent**: `admin-app`
- **Applies to**: `admin-web/**`
- **Contains**: Next.js 16, TypeScript, NextAuth.js v5, Shadcn/ui patterns
- **Use for**: Web admin development, authentication, SSE, role-based access

### 3. **Mobile App Rules** (`mobile-app-rules.instructions.md`)
- **Agent**: `mobile-app`
- **Applies to**: `mobile/**`
- **Contains**: React Native, Expo, navigation, offline support patterns
- **Use for**: Mobile app development, navigation, state management

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Critical Global Policies](#critical-global-policies)
3. [Technology Stack](#technology-stack)
4. [Quick Reference](#quick-reference)

---

## 1. Architecture Overview

### System Purpose

Algo Trading System is a **high-speed, multi-tenant automated trading platform** that provides:

- **Dual frontend architecture** - Mobile app AND web application
  - **Mobile app** for retail traders to create and manage strategies on-the-go
  - **Admin web app** for comprehensive platform management and user access
- **Backend execution engine** with Redis-based in-memory runtime
- **Broker integrations** (Zerodha, Dhan, Fyers, Angel One)
- **Real-time market monitoring** via WebSockets
- **Automated order execution** with mandatory stop-loss protection
- **Multi-tenant isolation** for secure strategy execution
- **Role-based access control** (Admin, User, Broker roles)
- **Strategy playground** for testing without real money

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                  CLIENT INTERFACES (Dual Access)                │
│                                                                 │
│  ┌────────────────────────┐    ┌────────────────────────────┐  │
│  │  Mobile App            │    │  Admin Web App             │  │
│  │  (React Native/Expo)   │    │  (Next.js 16)              │  │
│  │                        │    │                            │  │
│  │  • Strategy Creation   │    │  • User Management (Admin) │  │
│  │  • Broker Setup        │    │  • System Monitoring       │  │
│  │  • Status Monitoring   │    │  • Web Strategy Access     │  │
│  └────────────────────────┘    │  • Playground Testing      │  │
│                                 │  • Real-Time Updates (SSE) │  │
│                                 └────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                             │
│          (Auth, Strategy, Broker, Admin Services)               │
│                                                                 │
│   ┌───────────────┐     ┌───────────────────────────────┐      │
│   │  Auth Service │ --> │  Role-Based Access Control    │      │
│   │  (JWT + Roles)│     │  (Admin/User/Broker)          │      │
│   └───────────────┘     └───────────────────────────────┘      │
│           │                         │                           │
│           ▼                         ▼                           │
│   ┌───────────────┐     ┌───────────────────────────────┐      │
│   │ Broker Service│     │  Redis Runtime Store          │      │
│   └───────────────┘     │  + Pub/Sub (SSE)              │      │
│           │             └───────────────────────────────┘      │
│           ▼                         │                           │
│   ┌─────────────────────────────────────────────────────┐      │
│   │        Execution Engine (Order Placement)           │      │
│   └─────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                     PostgreSQL (Persistent Storage)
                     + User Roles + Audit Logs
```

### Key Actors

- **Retail Traders** – End users creating and running automated strategies (mobile OR web)
- **System Administrators** – Managing platform users, monitoring system health
- **Broker Partners** – Monitoring API integrations and performance
- **Backend Developers** – Building FastAPI services and execution logic
- **Frontend Developers** – Developing React Native app and Next.js web app
- **DevOps Engineers** – Managing AWS infrastructure and deployments
- **QA Testers** – Ensuring system reliability and safety

### Technology Stack

| Component         | Technology                      |
| ----------------- | ------------------------------- |
| Backend API       | FastAPI (Python 3.11+)          |
| Mobile App        | React Native / Expo             |
| **Admin Web App** | **Next.js 16 (App Router)**     |
| **Web Auth**      | **NextAuth.js v5**              |
| **Web UI**        | **Shadcn/ui + Tailwind CSS**    |
| **Real-Time**     | **Server-Sent Events (SSE)**    |
| In-Memory Runtime | Redis (+ Pub/Sub for SSE)       |
| Database          | PostgreSQL                      |
| Message Queue     | Celery + Redis                  |
| Authentication    | JWT (with role claims)          |
| Encryption        | AES-256 for credentials         |
| Cloud Platform    | AWS (ECS/EKS, RDS, ElastiCache) |
| Monitoring        | CloudWatch                      |
| WebSocket Feeds   | Broker-specific APIs            |

---

## 2. Critical Global Policies

> **Note**: Detailed implementation policies are in specialized instruction files. These are system-wide critical rules.

### ⚠️ Policy 1: Multi-Tenancy - Always Filter by user_id

**Every database query MUST filter by `user_id` for data isolation between users.**

```python
# ❌ FORBIDDEN - Security vulnerability (data leakage)
strategies = db.query(Strategy).all()

# ✅ REQUIRED - User isolation
strategies = db.query(Strategy).filter(
    Strategy.user_id == current_user.id
).all()
```

### ⚠️ Policy 2: Secure Broker Credential Storage

**All broker API keys, secrets, and tokens MUST be encrypted with AES-256 before storage.**

### ⚠️ Policy 3: Mandatory Stop-Loss Protection

**Every strategy MUST have a stop-loss defined and enforced.**

### ⚠️ Policy 4: Failsafe Execution

**Execution engine MUST handle failures gracefully without losing orders.**

### ⚠️ Policy 5: Independent Strategy Execution

**Strategies MUST run in isolated contexts with no cross-contamination.**

### ⚠️ Policy 6: Never Store Private Keys in Code

**Load all secrets from environment variables or KMS.**

---

## 3. Technology Stack

### Most Common Operations

| Task                      | Code                                                  |
| ------------------------- | ----------------------------------------------------- |
| **Validate strategy**     | `errors = validate_strategy(data)`                    |
| **Create strategy**       | `strategy = create_strategy(user_id, data)`           |
| **Execute order**         | `result = place_order(broker, order_data)`            |
| **Check stop-loss**       | `if price <= strategy.stop_loss: sell()`              |
| **Encrypt credentials**   | `encrypted = encrypt_aes256(api_key, master_key)`     |
| **Get current user (web)** | `user = await getCurrentUser()`                       |
| **Require role (web)**    | `user = await requireRole('Admin')`                   |
| **Stream updates (web)**  | `const { data } = useStrategyStream(strategyId)`      |

### ID Prefixes

| Entity   | Prefix   | Example        |
| -------- | -------- | -------------- |
| User     | `usr_`   | `usr_abc123`   |
| Strategy | `str_`   | `str_xyz789`   |
| Broker   | `brk_`   | `brk_def456`   |
| Order    | `ord_`   | `ord_ghi012`   |
| Queue    | `queue_` | `queue_def456` |
| Source   | `src_`   | `src_ghi012`   |

### Environment Variables

```bash
# Database (optional)
DATABASE_URL="postgresql://user:pass@localhost:5432/algo_trading"

# AI Services
OPENAI_API_KEY="sk-..."
OPENAI_MODEL="gpt-4"

# Redis (for rate limiting)
REDIS_URL="redis://localhost:6379"

# Backend
ALGO_TRADING_CORE_URL="http://localhost:8000"

# Frontend
NEXT_PUBLIC_CORE_URL="http://localhost:8000"
```

### Docker Commands

```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f backend

# Run tests
docker-compose exec backend pytest

# Start frontend (if applicable)
# cd mobile && expo start
```

---

## Summary

**Key Takeaways**:

1. ✅ High-speed multi-tenant trading automation
2. ✅ Redis-based in-memory execution runtime
3. ✅ Mandatory stop-loss protection for safety
4. ✅ AES-256 encrypted broker credentials
5. ✅ Functional services over classes
6. ✅ JWT authentication with user isolation
7. ✅ React Native mobile app interface

**Questions?** See existing code in `/backend/app`, `/docs`, or `/tests` for real examples.

---

**Last Updated**: December 7, 2025  
**Maintained by**: Algo Trading System Engineering Team
