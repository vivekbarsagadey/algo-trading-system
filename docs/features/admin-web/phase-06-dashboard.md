---
goal: Create main dashboard with strategy overview and quick actions
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [admin-web, nextjs, dashboard, recharts, sse, real-time]
---

# Phase 6: Dashboard & Home

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Create the main dashboard page with strategy overview, performance metrics, quick actions, and real-time status updates.

---

## 1. Requirements & Constraints

### Technical Requirements

- **REQ-001**: Server Components for initial data fetching
- **REQ-002**: Real-time updates via SSE subscription
- **REQ-003**: Responsive grid layout for stats cards
- **REQ-004**: Performance charts using Recharts

### UI/UX Requirements

- **UXR-001**: Loading skeletons for async data
- **UXR-002**: Error boundaries for graceful failures
- **UXR-003**: Quick actions for common tasks
- **UXR-004**: Recent activity timeline

### Constraints

- **CON-001**: Dashboard data refreshes in real-time via SSE
- **CON-002**: Charts must be client components (Recharts limitation)
- **CON-003**: Initial data fetched server-side for SEO/performance

---

## 2. Implementation Tasks

### GOAL-006: Create main dashboard with strategy overview and quick actions

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

---

## 3. Dependencies

- **DEP-001**: Recharts for data visualization
- **DEP-002**: Shadcn/ui Card, Badge components
- **DEP-003**: SSE hook from Phase 16
- **DEP-004**: Strategy API from Phase 4

---

## 4. Files

### Dashboard Page

- **FILE-001**: `admin-web/app/(dashboard)/page.tsx` - Main dashboard page

### Dashboard Components

- **FILE-002**: `admin-web/components/dashboard/StatsCards.tsx` - Statistics cards
- **FILE-003**: `admin-web/components/dashboard/StrategyList.tsx` - Recent strategies list
- **FILE-004**: `admin-web/components/dashboard/QuickActions.tsx` - Quick action buttons
- **FILE-005**: `admin-web/components/dashboard/RecentActivity.tsx` - Activity timeline
- **FILE-006**: `admin-web/components/dashboard/PerformanceChart.tsx` - P&L chart

### Loading States

- **FILE-007**: `admin-web/components/dashboard/DashboardSkeleton.tsx` - Loading skeleton
- **FILE-008**: `admin-web/app/(dashboard)/loading.tsx` - Page-level loading state

### Error Handling

- **FILE-009**: `admin-web/app/(dashboard)/error.tsx` - Error boundary page

---

## Dashboard Layout

```text
┌─────────────────────────────────────────────────────────────┐
│                     Header / Navigation                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Active   │  │ Today's  │  │ Orders   │  │ Success  │     │
│  │Strategies│  │   P&L    │  │ Executed │  │   Rate   │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────┐  ┌───────────────────────────┐ │
│  │    Performance Chart    │  │      Quick Actions        │ │
│  │    (P&L over time)      │  │  [+ Strategy] [+ Broker]  │ │
│  └─────────────────────────┘  └───────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────┐  ┌───────────────────────────┐ │
│  │   Active Strategies     │  │    Recent Activity        │ │
│  │   (List with status)    │  │    (Execution timeline)   │ │
│  └─────────────────────────┘  └───────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Success Criteria

✅ Phase 6 is complete when:

- [ ] Dashboard page loads with server-side data
- [ ] Stats cards show active strategies, P&L, orders, success rate
- [ ] Performance chart displays P&L over time
- [ ] Recent strategies list with status badges
- [ ] Quick actions for common tasks
- [ ] Recent activity timeline
- [ ] Real-time updates via SSE
- [ ] Loading skeletons during data fetch
- [ ] Error boundaries for failures

---

## Next Phase

[Phase 7: Strategy Management →](./phase-07-strategy-management.md)
