---
goal: Phase 15 - Database Migrations & Schema Management
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Backend Engineering Team
status: Planned
tags: [backend, database, migrations, alembic, schema]
---

# Phase 15: Database Migrations

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

## Goal

**GOAL-015**: Establish database migration strategy and create all necessary migrations

## Overview

This phase establishes the database migration infrastructure using Alembic and creates migrations for all models defined in previous phases.

---

## Prerequisites

- Phase 1-14 completed
- All models defined
- PostgreSQL running

## Dependencies

```txt
alembic>=1.13.0
```

---

## Implementation Tasks

### TASK-137: Configure Alembic

**File**: `backend/alembic.ini` and `backend/alembic/env.py`

**Description**: Configure Alembic for async SQLAlchemy migrations.

**Acceptance Criteria**:
- [ ] Async SQLAlchemy support
- [ ] Environment variable database URL
- [ ] Auto-generate support
- [ ] Naming conventions
- [ ] Multi-schema support (if needed)

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-138: Create Users & Auth Tables Migration

**File**: `backend/alembic/versions/0001_users_auth.py`

**Description**: Migration for users, sessions, and authentication tables.

**Acceptance Criteria**:
- [ ] users table
- [ ] user_sessions table
- [ ] password_resets table
- [ ] Indexes for email, user_id

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-139: Create Strategies Table Migration

**File**: `backend/alembic/versions/0002_strategies.py`

**Description**: Migration for strategies table.

**Acceptance Criteria**:
- [ ] strategies table
- [ ] All strategy fields
- [ ] Indexes for user_id, status
- [ ] Foreign key to users

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-140: Create Broker Connections Migration

**File**: `backend/alembic/versions/0003_broker_connections.py`

**Description**: Migration for broker connections table.

**Acceptance Criteria**:
- [ ] broker_connections table
- [ ] Encrypted credential columns
- [ ] Foreign key to users
- [ ] Unique constraint user_id + broker

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-141: Create Order Logs Migration

**File**: `backend/alembic/versions/0004_order_logs.py`

**Description**: Migration for order logs table.

**Acceptance Criteria**:
- [ ] order_logs table
- [ ] JSON columns for data/result
- [ ] Indexes for queries
- [ ] Foreign keys to users, strategies

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-142: Create Notifications Migration

**File**: `backend/alembic/versions/0005_notifications.py`

**Description**: Migration for notifications table.

**Acceptance Criteria**:
- [ ] notifications table
- [ ] notification_preferences table
- [ ] device_tokens table
- [ ] Indexes for user_id

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-143: Create Migration Scripts

**File**: `backend/scripts/migrate_db.sh`

**Description**: Create scripts for running migrations in different environments.

**Acceptance Criteria**:
- [ ] migrate_db.sh - Run migrations
- [ ] rollback_db.sh - Rollback
- [ ] create_migration.sh - New migration
- [ ] Docker integration

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

### TASK-144: Add Seed Data

**File**: `backend/alembic/versions/0006_seed_data.py`

**Description**: Add seed data for development and testing.

**Acceptance Criteria**:
- [ ] Admin user
- [ ] Test users (dev only)
- [ ] System configuration
- [ ] Conditional on environment

| Status | Completed | Date |
|--------|-----------|------|
| ⬜ Not Started | | |

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/alembic/env.py` | Modify | Async support |
| `backend/alembic/versions/0001_*.py` | Create | Users migration |
| `backend/alembic/versions/0002_*.py` | Create | Strategies migration |
| `backend/alembic/versions/0003_*.py` | Create | Broker connections |
| `backend/alembic/versions/0004_*.py` | Create | Order logs |
| `backend/alembic/versions/0005_*.py` | Create | Notifications |
| `backend/alembic/versions/0006_*.py` | Create | Seed data |
| `backend/scripts/migrate_db.sh` | Modify | Migration scripts |

---

## Migration Commands

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# Show current version
alembic current

# Show history
alembic history
```

---

## Definition of Done

- [ ] All 8 tasks completed
- [ ] All migrations created
- [ ] Migrations run successfully
- [ ] Rollback tested
- [ ] Seed data working
- [ ] Scripts documented
- [ ] Code reviewed and approved

---

## Backend Phases Complete

After completing Phase 15, the backend is fully implemented. Proceed to mobile app or admin web app development.
