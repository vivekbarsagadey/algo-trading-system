# Instruction Files Structure

**Date**: December 7, 2025

---

## Overview

The Algo Trading System now has **four instruction files** organized by component area with specialized agents.

---

## Instruction Files

### 1. **Main Instruction File** (High-Level Overview)
- **File**: `.github/instructions/algo-trading-system-rules.instructions.md`
- **Applies To**: `**` (all files)
- **Purpose**: High-level architecture, global policies, quick reference
- **Contains**:
  - System architecture overview
  - Critical global policies (multi-tenancy, security, stop-loss)
  - Technology stack
  - Agent selection guide
  - Quick reference for all components

### 2. **Backend Python Rules**
- **File**: `.github/instructions/backend-python-rules.instructions.md`
- **Applies To**: `backend/**`
- **Agent**: `expert-python`
- **Purpose**: Backend-specific implementation patterns
- **Contains**:
  - FastAPI route patterns
  - SQLAlchemy model patterns
  - Database query patterns
  - Alembic migration patterns
  - Broker integration patterns
  - Execution engine patterns
  - Testing standards (pytest)
  - Celery task patterns

### 3. **Admin Web App Rules**
- **File**: `.github/instructions/admin-web-app-rules.instructions.md`
- **Applies To**: `admin-web/**`
- **Agent**: `admin-app`
- **Purpose**: Next.js 16 web application patterns
- **Contains**:
  - NextAuth.js v5 authentication
  - Server Component patterns
  - Client Component patterns
  - Middleware and route protection
  - API integration patterns
  - Server-Sent Events (SSE) patterns
  - Form validation with Zod
  - Shadcn/ui component usage

### 4. **Mobile App Rules**
- **File**: `.github/instructions/mobile-app-rules.instructions.md`
- **Applies To**: `mobile/**`
- **Agent**: `mobile-app`
- **Purpose**: React Native/Expo mobile application patterns
- **Contains**:
  - Expo Router navigation
  - SecureStore for credentials
  - Context API patterns (AuthContext)
  - Custom hooks patterns
  - API client with interceptors
  - Offline support with AsyncStorage
  - Network detection
  - Platform-specific code
  - Performance optimization (memo, useMemo, useCallback)

---

## Agent Selection Guide

| Working On | Use Agent | Instruction File |
|------------|-----------|------------------|
| **Backend API, Database, Brokers, Execution Engine** | `expert-python` | `backend-python-rules.instructions.md` |
| **Admin Web Application (Next.js)** | `admin-app` | `admin-web-app-rules.instructions.md` |
| **Mobile Application (React Native)** | `mobile-app` | `mobile-app-rules.instructions.md` |
| **General Architecture, Documentation** | (default) | `algo-trading-system-rules.instructions.md` |

---

## Usage

### For Developers

When working on a specific area:

1. **Check main file first** for global policies and architecture understanding
2. **Switch to specialized file** for detailed implementation patterns
3. **Use appropriate agent** when requesting AI assistance

### For AI Agents

The instruction files are automatically loaded based on file patterns:

- Files in `backend/**` → loads `backend-python-rules.instructions.md`
- Files in `admin-web/**` → loads `admin-web-app-rules.instructions.md`
- Files in `mobile/**` → loads `mobile-app-rules.instructions.md`
- All files → loads `algo-trading-system-rules.instructions.md`

---

## Key Differences Between Agents

### expert-python (Backend)
- **Focus**: API design, database operations, broker integrations
- **Patterns**: Functional services, SQLAlchemy models, FastAPI routes
- **Testing**: pytest, integration tests, conftest patterns
- **Critical**: Multi-tenancy filtering, credential encryption, stop-loss validation

### admin-app (Admin Web)
- **Focus**: Next.js 16, authentication, role-based access
- **Patterns**: Server components, NextAuth.js v5, SSE streams
- **Testing**: Component testing, API integration
- **Critical**: Server-first rendering, role validation, type safety

### mobile-app (Mobile)
- **Focus**: React Native, Expo Router, offline support
- **Patterns**: Context API, custom hooks, secure storage
- **Testing**: Component testing, offline scenarios
- **Critical**: SecureStore usage, platform-specific code, performance optimization

---

## Global Policies (Apply to All)

These policies are in the main file and apply across all components:

1. **Multi-Tenancy**: Always filter by `user_id`
2. **Secure Credentials**: AES-256 encryption for broker keys
3. **Mandatory Stop-Loss**: Every strategy must have stop-loss
4. **Failsafe Execution**: Graceful error handling without data loss
5. **Independent Strategy Execution**: Isolated contexts
6. **No Private Keys in Code**: Load from environment/KMS

---

## Quick Reference

### Backend Operations (expert-python)

```python
# Query with user isolation
strategies = db.query(Strategy).filter(
    Strategy.user_id == current_user.id
).all()

# Encrypt credentials
encrypted = encrypt_aes256(api_key, master_key)

# Functional service
service = create_strategy_service(db, redis_client)
result = service["validate_strategy"](data)
```

### Admin Web Operations (admin-app)

```typescript
// Server component with auth
const user = await requireAuth()
const data = await apiClient.getStrategies(user.id)

// SSE stream hook
const { data, isConnected } = useStrategyStream(strategyId)

// Role-based rendering
if (session?.user.role === 'Admin') {
  return <AdminControls />
}
```

### Mobile Operations (mobile-app)

```typescript
// Secure storage
await SecureStore.setItemAsync('token', jwtToken)

// Navigation
router.push('/strategies/123')

// API call with auth
const response = await api.getStrategies()

// Network detection
const { isOnline } = useNetworkStatus()
```

---

## Benefits

### Organization
- ✅ Clear separation of concerns
- ✅ Focused instruction files per component
- ✅ Reduced cognitive load (only relevant patterns)

### Maintainability
- ✅ Easier to update specific patterns
- ✅ No cross-contamination between components
- ✅ Version control per component area

### Developer Experience
- ✅ Find relevant patterns quickly
- ✅ Agent-specific best practices
- ✅ Comprehensive code examples

### AI Agent Performance
- ✅ Context-appropriate responses
- ✅ Specialized knowledge per area
- ✅ Reduced token usage (focused content)

---

## File Sizes

| File | Lines | Focus |
|------|-------|-------|
| `algo-trading-system-rules.instructions.md` | ~300 | High-level overview |
| `backend-python-rules.instructions.md` | ~850 | Backend patterns |
| `admin-web-app-rules.instructions.md` | ~700 | Web app patterns |
| `mobile-app-rules.instructions.md` | ~650 | Mobile app patterns |

**Total**: ~2,500 lines of comprehensive, focused documentation

---

## Next Steps

### For New Features

1. Determine which component(s) affected
2. Update relevant specialized instruction file(s)
3. Update main file only if global policy changes
4. Test with appropriate agent

### For Bug Fixes

1. Identify component area
2. Check specialized instruction file for patterns
3. Verify against global policies
4. Apply fix following established patterns

---

**Last Updated**: December 7, 2025  
**Maintained by**: Algo Trading System Engineering Team
