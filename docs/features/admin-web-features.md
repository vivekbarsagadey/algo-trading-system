---
goal: Admin Web Application Features Implementation Plan for Algo Trading System
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [frontend, nextjs, typescript, admin, web-app, react, shadcn]
---

# Admin Web Application Features Implementation Plan

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

This document outlines all features for the Admin Web Application built with Next.js 16 (App Router), providing comprehensive platform management for administrators and web-based strategy management for retail traders.

---

## 1. Requirements & Constraints

### Technical Requirements

- **REQ-001**: Next.js 16 with App Router architecture
- **REQ-002**: TypeScript strict mode enabled throughout
- **REQ-003**: Server-Side Rendering (SSR) for initial page loads
- **REQ-004**: Client-side navigation for seamless UX
- **REQ-005**: Real-time updates via Server-Sent Events (SSE)
- **REQ-006**: Responsive design supporting mobile, tablet, and desktop
- **REQ-007**: WCAG 2.1 Level AA accessibility compliance

### Security Requirements

- **SEC-001**: NextAuth.js v5 for authentication with JWT strategy
- **SEC-002**: Role-based route protection via middleware
- **SEC-003**: CSRF protection on all form submissions
- **SEC-004**: Secure cookie handling (HttpOnly, Secure, SameSite)
- **SEC-005**: Input sanitization for XSS prevention
- **SEC-006**: Rate limiting on authentication endpoints

### UI/UX Requirements

- **UXR-001**: Shadcn/ui component library with Tailwind CSS
- **UXR-002**: Dark mode support
- **UXR-003**: Loading states for all async operations
- **UXR-004**: Toast notifications for user feedback
- **UXR-005**: Form validation with inline error messages
- **UXR-006**: Keyboard navigation support

### Constraints

- **CON-001**: Backend API must be available at `ALGO_TRADING_CORE_URL`
- **CON-002**: JWT token refresh handled automatically
- **CON-003**: Session timeout after 30 minutes of inactivity
- **CON-004**: Maximum file size for uploads: 5MB

### Patterns

- **PAT-001**: Server Components for data fetching
- **PAT-002**: Client Components for interactivity
- **PAT-003**: Server Actions for form submissions
- **PAT-004**: Zustand for client-side state management
- **PAT-005**: React Hook Form + Zod for form validation
- **PAT-006**: Parallel route loading for complex layouts

---

## 2. Implementation Steps

### Phase 1: Project Setup & Configuration

- GOAL-001: Initialize Next.js 16 project with TypeScript and configure development environment

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-001 | Create Next.js 16 project with `npx create-next-app@latest admin-web --typescript --tailwind --eslint --app` | | |
| TASK-002 | Configure `tsconfig.json` with strict mode, path aliases (@/components, @/lib, @/hooks) | | |
| TASK-003 | Install and configure Shadcn/ui: `npx shadcn-ui@latest init` with New York style | | |
| TASK-004 | Install core dependencies: `zustand`, `react-hook-form`, `zod`, `@hookform/resolvers` | | |
| TASK-005 | Install NextAuth.js v5: `npm install next-auth@beta` | | |
| TASK-006 | Install charting library: `npm install recharts` | | |
| TASK-007 | Create `.env.local` with environment variables: NEXTAUTH_SECRET, NEXTAUTH_URL, ALGO_TRADING_CORE_URL | | |
| TASK-008 | Configure `tailwind.config.ts` with custom color scheme matching brand | | |
| TASK-009 | Create `lib/utils.ts` with utility functions (cn for class merging) | | |
| TASK-010 | Set up ESLint and Prettier configuration for code consistency | | |
| TASK-011 | Create project folder structure following App Router conventions | | |
| TASK-012 | Add `components.json` for Shadcn/ui component generation | | |

### Phase 2: Authentication System

- GOAL-002: Implement complete authentication flow with NextAuth.js v5 and role-based access

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

### Phase 3: Middleware & Route Protection

- GOAL-003: Implement middleware for route protection and role-based access control

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

### Phase 4: API Client & Backend Integration

- GOAL-004: Create API client for backend communication with proper authentication

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

### Phase 5: Layout & Navigation

- GOAL-005: Create application layouts with navigation and responsive sidebar

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-053 | Create `app/layout.tsx` root layout with providers, fonts, and metadata | | |
| TASK-054 | Create `components/layout/Sidebar.tsx` with collapsible navigation | | |
| TASK-055 | Create `components/layout/Header.tsx` with user menu, notifications, theme toggle | | |
| TASK-056 | Create `components/layout/MobileSidebar.tsx` for mobile navigation | | |
| TASK-057 | Create `app/(dashboard)/layout.tsx` for authenticated user pages | | |
| TASK-058 | Create `app/(admin)/layout.tsx` for admin pages with admin-specific nav | | |
| TASK-059 | Define navigation items based on user role in `config/navigation.ts` | | |
| TASK-060 | Create `components/layout/NavItem.tsx` with active state and icons | | |
| TASK-061 | Add breadcrumb component `components/layout/Breadcrumb.tsx` | | |
| TASK-062 | Implement dark mode toggle with localStorage persistence | | |
| TASK-063 | Create `components/layout/Footer.tsx` with version and links | | |
| TASK-064 | Add keyboard shortcuts overlay (Cmd+K for search) | | |

### Phase 6: Dashboard & Home

- GOAL-006: Create main dashboard with strategy overview and quick actions

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-065 | Create `app/(dashboard)/page.tsx` as main dashboard | | |
| TASK-066 | Create `components/dashboard/StatsCards.tsx` showing active strategies, P&L, order count | | |
| TASK-067 | Create `components/dashboard/StrategyList.tsx` showing recent/active strategies | | |
| TASK-068 | Create `components/dashboard/QuickActions.tsx` with create strategy, connect broker buttons | | |
| TASK-069 | Create `components/dashboard/RecentActivity.tsx` timeline of recent executions | | |
| TASK-070 | Create `components/dashboard/PerformanceChart.tsx` using Recharts for P&L over time | | |
| TASK-071 | Implement real-time status updates via SSE subscription | | |
| TASK-072 | Add loading skeletons for async data fetching | | |
| TASK-073 | Create dashboard data fetching with React Server Components | | |
| TASK-074 | Add error boundaries for graceful failure handling | | |

### Phase 7: Strategy Management

- GOAL-007: Implement complete strategy CRUD with real-time status updates

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-075 | Create `app/(dashboard)/strategies/page.tsx` with strategy list table | | |
| TASK-076 | Create `components/strategies/StrategyTable.tsx` with sortable columns, pagination | | |
| TASK-077 | Create `components/strategies/StrategyFilters.tsx` for status, date filtering | | |
| TASK-078 | Create `app/(dashboard)/strategies/new/page.tsx` for strategy creation | | |
| TASK-079 | Create `components/strategies/StrategyForm.tsx` with all required fields | | |
| TASK-080 | Implement symbol autocomplete with search functionality | | |
| TASK-081 | Create time picker components for buy_time and sell_time | | |
| TASK-082 | Add stop-loss input with percentage/absolute toggle | | |
| TASK-083 | Implement form validation: mandatory stop_loss, buy_time < sell_time | | |
| TASK-084 | Create `app/(dashboard)/strategies/[id]/page.tsx` for strategy details | | |
| TASK-085 | Create `components/strategies/StrategyDetail.tsx` showing full strategy info | | |
| TASK-086 | Create `components/strategies/StrategyControls.tsx` with Start/Stop buttons | | |
| TASK-087 | Create `components/strategies/ExecutionLog.tsx` showing order history | | |
| TASK-088 | Create `app/(dashboard)/strategies/[id]/edit/page.tsx` for strategy editing | | |
| TASK-089 | Implement real-time status updates using useStrategyStream hook | | |
| TASK-090 | Create `hooks/useStrategyStream.ts` for SSE subscription | | |
| TASK-091 | Add strategy deletion with confirmation dialog | | |
| TASK-092 | Create strategy status badges component | | |

### Phase 8: Broker Integration

- GOAL-008: Implement broker connection management interface

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-093 | Create `app/(dashboard)/brokers/page.tsx` showing connected brokers | | |
| TASK-094 | Create `components/brokers/BrokerList.tsx` with connection status | | |
| TASK-095 | Create `app/(dashboard)/brokers/connect/page.tsx` for new broker connection | | |
| TASK-096 | Create `components/brokers/BrokerSelector.tsx` with Zerodha, Dhan, Fyers, Angel One options | | |
| TASK-097 | Create `components/brokers/BrokerCredentialsForm.tsx` with secure input fields | | |
| TASK-098 | Implement credential validation before saving (test connection) | | |
| TASK-099 | Show broker connection status with health indicator | | |
| TASK-100 | Add broker disconnection with confirmation | | |
| TASK-101 | Create token expiry warning component | | |
| TASK-102 | Implement broker help documentation modal per broker | | |
| TASK-103 | Add broker reconnection flow for expired tokens | | |

### Phase 9: Strategy Playground

- GOAL-009: Implement strategy testing sandbox without real money

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-104 | Create `app/(dashboard)/playground/page.tsx` as playground home | | |
| TASK-105 | Create `components/playground/PlaygroundBanner.tsx` with "This is simulated" warning | | |
| TASK-106 | Create `app/(dashboard)/playground/new/page.tsx` for simulated strategy creation | | |
| TASK-107 | Create `components/playground/SimulationForm.tsx` extending StrategyForm | | |
| TASK-108 | Add historical date range selector for backtesting | | |
| TASK-109 | Create `app/(dashboard)/playground/[id]/page.tsx` for simulation details | | |
| TASK-110 | Create `components/playground/SimulationResults.tsx` with P&L visualization | | |
| TASK-111 | Create `components/playground/TradeTimeline.tsx` showing simulated executions | | |
| TASK-112 | Implement simulation speed controls (1x, 5x, 10x) | | |
| TASK-113 | Create comparison view between simulated and actual results | | |
| TASK-114 | Add export simulation results to CSV | | |

### Phase 10: User Profile & Settings

- GOAL-010: Implement user profile management and application settings

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-115 | Create `app/(dashboard)/profile/page.tsx` for user profile | | |
| TASK-116 | Create `components/profile/ProfileForm.tsx` for name, email updates | | |
| TASK-117 | Create `app/(dashboard)/profile/security/page.tsx` for password change | | |
| TASK-118 | Create `components/profile/ChangePasswordForm.tsx` with validation | | |
| TASK-119 | Create `app/(dashboard)/settings/page.tsx` for app settings | | |
| TASK-120 | Implement notification preferences toggles | | |
| TASK-121 | Implement timezone selection (default IST) | | |
| TASK-122 | Add theme preference (Light/Dark/System) | | |
| TASK-123 | Create session management - view active sessions, logout all | | |
| TASK-124 | Add API key management for programmatic access (future) | | |

### Phase 11: Admin - User Management

- GOAL-011: Implement admin user management dashboard

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-125 | Create `app/(admin)/admin/users/page.tsx` with user list | | |
| TASK-126 | Create `components/admin/UserTable.tsx` with search, filter, pagination | | |
| TASK-127 | Create `app/(admin)/admin/users/new/page.tsx` for user creation | | |
| TASK-128 | Create `components/admin/UserForm.tsx` with role assignment | | |
| TASK-129 | Create `app/(admin)/admin/users/[id]/page.tsx` for user details | | |
| TASK-130 | Create `components/admin/UserDetail.tsx` with strategy count, activity | | |
| TASK-131 | Implement user role modification (Admin/User/Broker) | | |
| TASK-132 | Implement user activation/deactivation toggle | | |
| TASK-133 | Add user impersonation for support (view as user) | | |
| TASK-134 | Create user activity log view | | |
| TASK-135 | Add bulk user actions (export, deactivate) | | |
| TASK-136 | Create user deletion with data handling confirmation | | |

### Phase 12: Admin - Strategy Oversight

- GOAL-012: Implement admin view of all strategies across platform

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-137 | Create `app/(admin)/admin/strategies/page.tsx` with all strategies | | |
| TASK-138 | Create `components/admin/AllStrategiesTable.tsx` with user column | | |
| TASK-139 | Add filters: user, status, broker, date range | | |
| TASK-140 | Create `app/(admin)/admin/strategies/[id]/page.tsx` for strategy detail | | |
| TASK-141 | Implement emergency force-stop for any strategy | | |
| TASK-142 | Add execution log viewing for any strategy | | |
| TASK-143 | Create strategy health indicators (error rate, success rate) | | |
| TASK-144 | Add bulk strategy actions (force-stop all for user) | | |
| TASK-145 | Create strategy audit trail view | | |

### Phase 13: Admin - System Monitoring

- GOAL-013: Implement system health monitoring and metrics dashboard

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-146 | Create `app/(admin)/admin/system/page.tsx` as system dashboard | | |
| TASK-147 | Create `components/admin/SystemHealth.tsx` with service status | | |
| TASK-148 | Display API health: database, Redis, broker connections | | |
| TASK-149 | Create `components/admin/OrderMetrics.tsx` with order volume chart | | |
| TASK-150 | Create `components/admin/ErrorRate.tsx` with error trending | | |
| TASK-151 | Display active strategy count and concurrent connections | | |
| TASK-152 | Create `components/admin/LatencyChart.tsx` for API response times | | |
| TASK-153 | Implement real-time metrics update via SSE | | |
| TASK-154 | Add alerting threshold configuration | | |
| TASK-155 | Create system configuration management interface | | |

### Phase 14: Admin - Analytics Dashboard

- GOAL-014: Implement platform-wide analytics and reporting

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-156 | Create `app/(admin)/admin/analytics/page.tsx` as analytics home | | |
| TASK-157 | Create `components/admin/UserGrowthChart.tsx` with user registration trends | | |
| TASK-158 | Create `components/admin/OrderVolumeChart.tsx` with daily/weekly/monthly views | | |
| TASK-159 | Create `components/admin/BrokerDistribution.tsx` pie chart of broker usage | | |
| TASK-160 | Create `components/admin/SuccessRateChart.tsx` showing order success trends | | |
| TASK-161 | Implement date range selector for all charts | | |
| TASK-162 | Add data export functionality (CSV, JSON) | | |
| TASK-163 | Create top performers list (most active users, strategies) | | |
| TASK-164 | Add comparison view (this week vs last week) | | |
| TASK-165 | Create custom report builder interface | | |

### Phase 15: Admin - Logs & Audit

- GOAL-015: Implement log viewing and audit trail for compliance

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-166 | Create `app/(admin)/admin/logs/page.tsx` as logs dashboard | | |
| TASK-167 | Create `app/(admin)/admin/logs/orders/page.tsx` for order execution logs | | |
| TASK-168 | Create `components/admin/OrderLogTable.tsx` with filtering | | |
| TASK-169 | Create `app/(admin)/admin/logs/errors/page.tsx` for error logs | | |
| TASK-170 | Create `components/admin/ErrorLogTable.tsx` with severity filtering | | |
| TASK-171 | Create `app/(admin)/admin/logs/audit/page.tsx` for admin audit trail | | |
| TASK-172 | Create `components/admin/AuditLogTable.tsx` with admin action history | | |
| TASK-173 | Implement log search with regex support | | |
| TASK-174 | Add log export functionality | | |
| TASK-175 | Create log retention policy display | | |

### Phase 16: Real-Time Features

- GOAL-016: Implement SSE-based real-time updates throughout the application

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-176 | Create `hooks/useSSE.ts` generic SSE hook | | |
| TASK-177 | Create `hooks/useStrategyStream.ts` for strategy status updates | | |
| TASK-178 | Create `hooks/useSystemMetrics.ts` for admin system monitoring | | |
| TASK-179 | Implement SSE connection management with automatic reconnection | | |
| TASK-180 | Create `components/common/ConnectionStatus.tsx` showing SSE status | | |
| TASK-181 | Add notification toast on order execution events | | |
| TASK-182 | Implement optimistic UI updates with SSE confirmation | | |
| TASK-183 | Add SSE authentication via query parameter token | | |
| TASK-184 | Create SSE event type handlers: ORDER_EXECUTED, SL_TRIGGERED, STRATEGY_STARTED | | |
| TASK-185 | Implement SSE cleanup on component unmount | | |

### Phase 17: Common UI Components

- GOAL-017: Build reusable UI component library using Shadcn/ui

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-186 | Install Shadcn components: button, input, form, table, card, dialog, dropdown-menu | | |
| TASK-187 | Install Shadcn components: tabs, toast, tooltip, badge, avatar, separator | | |
| TASK-188 | Create `components/ui/DataTable.tsx` with sorting, filtering, pagination | | |
| TASK-189 | Create `components/ui/SearchInput.tsx` with debounced search | | |
| TASK-190 | Create `components/ui/DateRangePicker.tsx` for date filtering | | |
| TASK-191 | Create `components/ui/TimeInput.tsx` for time selection | | |
| TASK-192 | Create `components/ui/ConfirmDialog.tsx` for destructive actions | | |
| TASK-193 | Create `components/ui/LoadingSpinner.tsx` and LoadingSkeleton | | |
| TASK-194 | Create `components/ui/EmptyState.tsx` for empty lists | | |
| TASK-195 | Create `components/ui/ErrorBoundary.tsx` for error handling | | |
| TASK-196 | Create `components/ui/StatusBadge.tsx` for strategy/order status | | |
| TASK-197 | Create `components/ui/CurrencyDisplay.tsx` for P&L formatting | | |

### Phase 18: State Management

- GOAL-018: Implement client-side state management with Zustand

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-198 | Create `store/authStore.ts` for authentication state | | |
| TASK-199 | Create `store/strategyStore.ts` for active strategy data | | |
| TASK-200 | Create `store/brokerStore.ts` for broker connection state | | |
| TASK-201 | Create `store/notificationStore.ts` for notification management | | |
| TASK-202 | Create `store/uiStore.ts` for UI state (sidebar, theme) | | |
| TASK-203 | Implement store persistence with zustand/middleware for selected stores | | |
| TASK-204 | Create store selectors for optimized re-renders | | |
| TASK-205 | Add devtools integration for debugging | | |

### Phase 19: Error Handling & Notifications

- GOAL-019: Implement comprehensive error handling and notification system

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-206 | Create `lib/errors.ts` with custom error classes | | |
| TASK-207 | Implement global error boundary in root layout | | |
| TASK-208 | Create `app/error.tsx` for error page | | |
| TASK-209 | Create `app/not-found.tsx` for 404 page | | |
| TASK-210 | Implement toast notification system with `sonner` or `react-hot-toast` | | |
| TASK-211 | Create notification types: success, error, warning, info | | |
| TASK-212 | Add notification center dropdown with history | | |
| TASK-213 | Implement notification persistence in localStorage | | |
| TASK-214 | Create notification preference management | | |
| TASK-215 | Add error reporting to backend for critical errors | | |

### Phase 20: Testing & Quality

- GOAL-020: Implement testing infrastructure and quality assurance

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-216 | Configure Jest and React Testing Library | | |
| TASK-217 | Create test utilities and mock providers | | |
| TASK-218 | Write unit tests for authentication forms | | |
| TASK-219 | Write unit tests for strategy forms and validation | | |
| TASK-220 | Write integration tests for API client | | |
| TASK-221 | Configure Playwright for E2E testing | | |
| TASK-222 | Write E2E tests for login flow | | |
| TASK-223 | Write E2E tests for strategy creation flow | | |
| TASK-224 | Write E2E tests for admin user management | | |
| TASK-225 | Add accessibility testing with axe-core | | |
| TASK-226 | Configure CI/CD pipeline with test execution | | |

---

## 3. Dependencies

- **DEP-001**: Next.js 16 with App Router
- **DEP-002**: TypeScript 5.x
- **DEP-003**: React 19
- **DEP-004**: NextAuth.js v5 (beta)
- **DEP-005**: Tailwind CSS 3.x
- **DEP-006**: Shadcn/ui component library
- **DEP-007**: Zustand for state management
- **DEP-008**: React Hook Form for form handling
- **DEP-009**: Zod for validation
- **DEP-010**: Recharts for data visualization
- **DEP-011**: Lucide React for icons
- **DEP-012**: date-fns for date manipulation
- **DEP-013**: Jest and React Testing Library for unit tests
- **DEP-014**: Playwright for E2E testing

---

## 4. Files

### Configuration Files

- **FILE-001**: `admin-web/package.json` - Dependencies and scripts
- **FILE-002**: `admin-web/tsconfig.json` - TypeScript configuration
- **FILE-003**: `admin-web/tailwind.config.ts` - Tailwind configuration
- **FILE-004**: `admin-web/next.config.js` - Next.js configuration
- **FILE-005**: `admin-web/components.json` - Shadcn/ui configuration
- **FILE-006**: `admin-web/.env.local` - Environment variables

### Core Files

- **FILE-007**: `admin-web/middleware.ts` - Route protection middleware
- **FILE-008**: `admin-web/lib/auth.ts` - NextAuth configuration
- **FILE-009**: `admin-web/lib/utils.ts` - Utility functions
- **FILE-010**: `admin-web/lib/api/client.ts` - API client

### Layout Files

- **FILE-011**: `admin-web/app/layout.tsx` - Root layout
- **FILE-012**: `admin-web/app/(auth)/layout.tsx` - Auth pages layout
- **FILE-013**: `admin-web/app/(dashboard)/layout.tsx` - Dashboard layout
- **FILE-014**: `admin-web/app/(admin)/layout.tsx` - Admin layout

### Auth Pages

- **FILE-015**: `admin-web/app/(auth)/login/page.tsx` - Login page
- **FILE-016**: `admin-web/app/(auth)/register/page.tsx` - Register page
- **FILE-017**: `admin-web/app/(auth)/forgot-password/page.tsx` - Forgot password
- **FILE-018**: `admin-web/app/(auth)/reset-password/page.tsx` - Reset password

### Dashboard Pages

- **FILE-019**: `admin-web/app/(dashboard)/page.tsx` - Main dashboard
- **FILE-020**: `admin-web/app/(dashboard)/strategies/page.tsx` - Strategy list
- **FILE-021**: `admin-web/app/(dashboard)/strategies/new/page.tsx` - Create strategy
- **FILE-022**: `admin-web/app/(dashboard)/strategies/[id]/page.tsx` - Strategy detail
- **FILE-023**: `admin-web/app/(dashboard)/brokers/page.tsx` - Broker list
- **FILE-024**: `admin-web/app/(dashboard)/brokers/connect/page.tsx` - Connect broker
- **FILE-025**: `admin-web/app/(dashboard)/playground/page.tsx` - Playground home
- **FILE-026**: `admin-web/app/(dashboard)/profile/page.tsx` - User profile
- **FILE-027**: `admin-web/app/(dashboard)/settings/page.tsx` - Settings

### Admin Pages

- **FILE-028**: `admin-web/app/(admin)/admin/users/page.tsx` - User management
- **FILE-029**: `admin-web/app/(admin)/admin/users/[id]/page.tsx` - User detail
- **FILE-030**: `admin-web/app/(admin)/admin/strategies/page.tsx` - All strategies
- **FILE-031**: `admin-web/app/(admin)/admin/system/page.tsx` - System health
- **FILE-032**: `admin-web/app/(admin)/admin/analytics/page.tsx` - Analytics
- **FILE-033**: `admin-web/app/(admin)/admin/logs/page.tsx` - Log viewer

### Component Files

- **FILE-034**: `admin-web/components/layout/Sidebar.tsx` - Navigation sidebar
- **FILE-035**: `admin-web/components/layout/Header.tsx` - Page header
- **FILE-036**: `admin-web/components/auth/LoginForm.tsx` - Login form
- **FILE-037**: `admin-web/components/auth/RegisterForm.tsx` - Register form
- **FILE-038**: `admin-web/components/dashboard/StatsCards.tsx` - Stats display
- **FILE-039**: `admin-web/components/strategies/StrategyForm.tsx` - Strategy form
- **FILE-040**: `admin-web/components/strategies/StrategyTable.tsx` - Strategy list
- **FILE-041**: `admin-web/components/brokers/BrokerForm.tsx` - Broker form
- **FILE-042**: `admin-web/components/admin/UserTable.tsx` - Admin user table
- **FILE-043**: `admin-web/components/admin/SystemHealth.tsx` - Health display

### Store Files

- **FILE-044**: `admin-web/store/authStore.ts` - Auth state
- **FILE-045**: `admin-web/store/strategyStore.ts` - Strategy state
- **FILE-046**: `admin-web/store/uiStore.ts` - UI state

### Hook Files

- **FILE-047**: `admin-web/hooks/useSSE.ts` - SSE hook
- **FILE-048**: `admin-web/hooks/useStrategyStream.ts` - Strategy stream hook

### Type Files

- **FILE-049**: `admin-web/types/auth.ts` - Auth types
- **FILE-050**: `admin-web/types/api.ts` - API response types
- **FILE-051**: `admin-web/types/strategy.ts` - Strategy types

---

## Success Criteria

✅ Implementation plan is complete when:

- All 20 phases have defined goals and tasks
- 226 tasks are defined with specific implementation details
- All file paths and component names are explicitly stated
- Authentication with NextAuth.js v5 is fully specified
- Role-based access control (Admin, User, Broker) is defined
- Real-time SSE implementation is detailed
- Shadcn/ui component usage is specified
- All 51 files to be created are listed
- Testing strategy is defined
- Ready for handoff to implementation agents
