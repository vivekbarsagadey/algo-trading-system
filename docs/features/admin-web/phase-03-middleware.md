---
goal: Implement middleware for route protection and role-based access control
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [admin-web, nextjs, middleware, rbac, security, route-protection]
---

# Phase 3: Middleware & Route Protection

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement Next.js middleware for route protection and role-based access control, ensuring secure access to admin, broker, and user-specific routes.

---

## 1. Requirements & Constraints

### Security Requirements

- **SEC-001**: Protect all authenticated routes from unauthenticated access
- **SEC-002**: Role-based access control for admin routes
- **SEC-003**: Role-based access control for broker routes
- **SEC-004**: JWT token validation in middleware

### Patterns

- **PAT-001**: Middleware-based route protection
- **PAT-002**: Public routes allowlist
- **PAT-003**: Role-based route patterns
- **PAT-004**: Return URL for post-login redirect

### Constraints

- **CON-001**: Middleware runs on Edge Runtime
- **CON-002**: Cannot access database directly in middleware
- **CON-003**: Must extract role from JWT token

---

## 2. Implementation Tasks

### GOAL-003: Implement middleware for route protection and role-based access control

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-029 | Create `middleware.ts` in project root for route protection | | |
| TASK-030 | Define public routes array: ['/login', '/register', '/forgot-password', '/reset-password'] | | |
| TASK-031 | Define admin routes pattern: '/admin/*' requiring Admin role | | |
| TASK-032 | Define broker routes pattern: '/broker/*' requiring Broker role | | |
| TASK-033 | Implement JWT token extraction from cookies | | |
| TASK-034 | Implement token validation and role extraction | | |
| TASK-035 | Redirect unauthenticated users to `/login` with return URL | | |
| TASK-036 | Redirect unauthorized role access to `/unauthorized` page | | |
| TASK-037 | Create `app/unauthorized/page.tsx` with role mismatch message | | |
| TASK-038 | Add session refresh logic for expiring tokens | | |
| TASK-039 | Create `lib/auth-helpers.ts` with getCurrentUser(), requireRole() utilities | | |
| TASK-040 | Write tests for middleware route protection scenarios | | |

---

## 3. Dependencies

- **DEP-001**: NextAuth.js v5 (beta)
- **DEP-002**: jose for JWT manipulation (Edge-compatible)
- **DEP-003**: next/server for middleware utilities

---

## 4. Files

### Middleware

- **FILE-001**: `admin-web/middleware.ts` - Main middleware for route protection

### Auth Helpers

- **FILE-002**: `admin-web/lib/auth-helpers.ts` - getCurrentUser(), requireRole() utilities

### Error Pages

- **FILE-003**: `admin-web/app/unauthorized/page.tsx` - Unauthorized access page

### Configuration

- **FILE-004**: `admin-web/config/routes.ts` - Route definitions (public, admin, broker patterns)

### Tests

- **FILE-005**: `admin-web/__tests__/middleware.test.ts` - Middleware test cases

---

## Route Protection Matrix

| Route Pattern | Required Role | Unauthenticated | Wrong Role |
|---------------|---------------|-----------------|------------|
| `/login` | None | Allow | Allow |
| `/register` | None | Allow | Allow |
| `/forgot-password` | None | Allow | Allow |
| `/` (dashboard) | Any authenticated | Redirect to /login | Allow |
| `/strategies/*` | Any authenticated | Redirect to /login | Allow |
| `/brokers/*` | Any authenticated | Redirect to /login | Allow |
| `/admin/*` | Admin | Redirect to /login | /unauthorized |
| `/broker/*` | Broker | Redirect to /login | /unauthorized |

---

## Success Criteria

✅ Phase 3 is complete when:

- [ ] Middleware protects all authenticated routes
- [ ] Public routes accessible without authentication
- [ ] Admin routes require Admin role
- [ ] Broker routes require Broker role
- [ ] Unauthenticated users redirected to login with return URL
- [ ] Unauthorized access shows proper error page
- [ ] Session refresh works for expiring tokens
- [ ] Helper utilities available throughout app

---

## Next Phase

[Phase 4: API Client & Backend Integration →](./phase-04-api-client.md)
