---
goal: Implement complete authentication flow with NextAuth.js v5 and role-based access
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [admin-web, nextjs, authentication, nextauth, jwt, rbac]
---

# Phase 2: Authentication System

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement complete authentication flow using NextAuth.js v5 with credentials provider, JWT strategy, and role-based access control (Admin, User, Broker).

---

## 1. Requirements & Constraints

### Security Requirements

- **SEC-001**: NextAuth.js v5 for authentication with JWT strategy
- **SEC-002**: Role-based route protection via middleware
- **SEC-003**: CSRF protection on all form submissions
- **SEC-004**: Secure cookie handling (HttpOnly, Secure, SameSite)
- **SEC-005**: Input sanitization for XSS prevention

### Patterns

- **PAT-001**: Credentials provider with backend API validation
- **PAT-002**: JWT tokens with role claims
- **PAT-003**: Session management with automatic refresh
- **PAT-004**: React Hook Form + Zod for form validation

### Constraints

- **CON-001**: Backend auth endpoints must be available
- **CON-002**: Session timeout after 30 minutes of inactivity
- **CON-003**: Roles: Admin, User, Broker

---

## 2. Implementation Tasks

### GOAL-002: Implement complete authentication flow with NextAuth.js v5 and role-based access

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-013 | Create `lib/auth.ts` with NextAuth configuration - credentials provider, JWT strategy | | |
| TASK-014 | Define `types/auth.ts` with User, Session, Role types (Admin, User, Broker) | | |
| TASK-015 | Create `app/api/auth/[...nextauth]/route.ts` for NextAuth API routes | | |
| TASK-016 | Implement authorize function in credentials provider - call backend `/auth/login` | | |
| TASK-017 | Configure JWT callback to include user role and id in token | | |
| TASK-018 | Configure session callback to expose role in session object | | |
| TASK-019 | Create `app/(auth)/login/page.tsx` with email/password form | | |
| TASK-020 | Create `app/(auth)/register/page.tsx` with registration form | | |
| TASK-021 | Create `app/(auth)/forgot-password/page.tsx` for password reset request | | |
| TASK-022 | Create `app/(auth)/reset-password/page.tsx` for password reset completion | | |
| TASK-023 | Create `components/auth/LoginForm.tsx` with react-hook-form and Zod validation | | |
| TASK-024 | Create `components/auth/RegisterForm.tsx` with password strength indicator | | |
| TASK-025 | Create `app/(auth)/layout.tsx` with centered card layout for auth pages | | |
| TASK-026 | Implement form error handling with toast notifications | | |
| TASK-027 | Add "Remember me" functionality with extended session duration | | |
| TASK-028 | Create auth context provider `providers/AuthProvider.tsx` | | |

---

## 3. Dependencies

- **DEP-001**: NextAuth.js v5 (beta)
- **DEP-002**: React Hook Form
- **DEP-003**: Zod validation
- **DEP-004**: @hookform/resolvers
- **DEP-005**: Backend auth API endpoints

---

## 4. Files

### Auth Configuration

- **FILE-001**: `admin-web/lib/auth.ts` - NextAuth configuration with credentials provider
- **FILE-002**: `admin-web/app/api/auth/[...nextauth]/route.ts` - NextAuth API routes

### Types

- **FILE-003**: `admin-web/types/auth.ts` - User, Session, Role type definitions

### Auth Pages

- **FILE-004**: `admin-web/app/(auth)/layout.tsx` - Auth pages layout with centered card
- **FILE-005**: `admin-web/app/(auth)/login/page.tsx` - Login page
- **FILE-006**: `admin-web/app/(auth)/register/page.tsx` - Registration page
- **FILE-007**: `admin-web/app/(auth)/forgot-password/page.tsx` - Forgot password page
- **FILE-008**: `admin-web/app/(auth)/reset-password/page.tsx` - Reset password page

### Components

- **FILE-009**: `admin-web/components/auth/LoginForm.tsx` - Login form with validation
- **FILE-010**: `admin-web/components/auth/RegisterForm.tsx` - Registration form
- **FILE-011**: `admin-web/components/auth/ForgotPasswordForm.tsx` - Password reset request
- **FILE-012**: `admin-web/components/auth/ResetPasswordForm.tsx` - Password reset form
- **FILE-013**: `admin-web/components/auth/PasswordStrength.tsx` - Password strength indicator

### Providers

- **FILE-014**: `admin-web/providers/AuthProvider.tsx` - Auth context provider

---

## Success Criteria

✅ Phase 2 is complete when:

- [ ] NextAuth.js v5 configured with credentials provider
- [ ] JWT tokens include user role and id
- [ ] Login page functional with form validation
- [ ] Registration page functional
- [ ] Forgot password flow works
- [ ] Session management with auto-refresh
- [ ] Role types defined (Admin, User, Broker)
- [ ] Auth context available throughout app

---

## Next Phase

[Phase 3: Middleware & Route Protection →](./phase-03-middleware.md)
