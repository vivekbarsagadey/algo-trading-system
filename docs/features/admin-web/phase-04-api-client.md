---
goal: Create API client for backend communication with proper authentication
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [admin-web, nextjs, api-client, fetch, authentication, typescript]
---

# Phase 4: API Client & Backend Integration

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Create a typed API client for backend communication with automatic authentication token injection, error handling, and retry logic.

---

## 1. Requirements & Constraints

### Technical Requirements

- **REQ-001**: Typed API client with TypeScript generics
- **REQ-002**: Automatic token injection from session
- **REQ-003**: Proper error handling with typed errors
- **REQ-004**: Request retry with exponential backoff

### Patterns

- **PAT-001**: Fetch wrapper with authentication
- **PAT-002**: Domain-specific API modules
- **PAT-003**: Typed request/response interfaces
- **PAT-004**: Error class hierarchy

### Constraints

- **CON-001**: Backend API available at `ALGO_TRADING_CORE_URL`
- **CON-002**: All requests require JWT token (except auth endpoints)
- **CON-003**: API returns JSON with consistent error format

---

## 2. Implementation Tasks

### GOAL-004: Create API client for backend communication with proper authentication

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-041 | Create `lib/api/client.ts` with base fetch wrapper including auth headers | | |
| TASK-042 | Implement automatic token injection from session | | |
| TASK-043 | Implement error handling with typed error responses | | |
| TASK-044 | Create `lib/api/auth.ts` with login(), register(), logout() functions | | |
| TASK-045 | Create `lib/api/strategies.ts` with CRUD operations for strategies | | |
| TASK-046 | Create `lib/api/brokers.ts` with broker connection operations | | |
| TASK-047 | Create `lib/api/admin.ts` with admin-specific API calls | | |
| TASK-048 | Create `lib/api/analytics.ts` with analytics data fetching | | |
| TASK-049 | Create `lib/api/playground.ts` with simulation API calls | | |
| TASK-050 | Define API response types in `types/api.ts` | | |
| TASK-051 | Implement request retry logic with exponential backoff | | |
| TASK-052 | Add request/response logging for debugging | | |

---

## 3. Dependencies

- **DEP-001**: next-auth for session access
- **DEP-002**: TypeScript for type safety
- **DEP-003**: Backend API endpoints

---

## 4. Files

### Core API Client

- **FILE-001**: `admin-web/lib/api/client.ts` - Base fetch wrapper with auth and error handling
- **FILE-002**: `admin-web/lib/api/index.ts` - API module exports

### Domain APIs

- **FILE-003**: `admin-web/lib/api/auth.ts` - Authentication API (login, register, logout)
- **FILE-004**: `admin-web/lib/api/strategies.ts` - Strategy CRUD operations
- **FILE-005**: `admin-web/lib/api/brokers.ts` - Broker connection management
- **FILE-006**: `admin-web/lib/api/admin.ts` - Admin-specific operations
- **FILE-007**: `admin-web/lib/api/analytics.ts` - Analytics data fetching
- **FILE-008**: `admin-web/lib/api/playground.ts` - Playground simulation API
- **FILE-009**: `admin-web/lib/api/users.ts` - User management (admin)

### Types

- **FILE-010**: `admin-web/types/api.ts` - API response types, error types

---

## API Client Architecture

```typescript
// lib/api/client.ts
class ApiClient {
  private baseUrl: string;
  private getToken: () => Promise<string | null>;

  async get<T>(path: string): Promise<T>;
  async post<T>(path: string, body: unknown): Promise<T>;
  async put<T>(path: string, body: unknown): Promise<T>;
  async delete<T>(path: string): Promise<T>;
}

// Usage
const strategies = await api.strategies.list();
const strategy = await api.strategies.create({ ... });
```

---

## Error Handling

```typescript
// types/api.ts
interface ApiError {
  code: string;
  message: string;
  details?: Record<string, string[]>;
}

// Custom error classes
class UnauthorizedError extends Error {}
class ValidationError extends Error {}
class NetworkError extends Error {}
```

---

## Success Criteria

✅ Phase 4 is complete when:

- [ ] Base API client with auth header injection
- [ ] Typed error handling with custom error classes
- [ ] Auth API module with login/register/logout
- [ ] Strategies API module with CRUD operations
- [ ] Brokers API module with connection management
- [ ] Admin API module with user management
- [ ] Analytics API module for data fetching
- [ ] Request retry with exponential backoff
- [ ] All API types defined

---

## Next Phase

[Phase 5: Layout & Navigation →](./phase-05-layout-navigation.md)
