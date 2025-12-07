---
goal: Implement admin view of all strategies across platform
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [admin-web, nextjs, admin, strategies, oversight, monitoring]
---

# Phase 12: Admin - Strategy Oversight

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement admin view of all strategies across the platform with oversight capabilities including force-stop, bulk actions, and health monitoring.

---

## 1. Requirements & Constraints

### Technical Requirements

- **REQ-001**: View all strategies across all users
- **REQ-002**: Filter by user, status, broker, date
- **REQ-003**: Emergency force-stop capability
- **REQ-004**: Strategy health indicators

### Business Requirements

- **BIZ-001**: Admins can force-stop any strategy
- **BIZ-002**: Audit trail for admin actions
- **BIZ-003**: Strategy health metrics visible

### Constraints

- **CON-001**: Only Admin role can access
- **CON-002**: Force-stop requires confirmation
- **CON-003**: Bulk actions have safety limits

---

## 2. Implementation Tasks

### GOAL-012: Implement admin view of all strategies across platform

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

---

## 3. Dependencies

- **DEP-001**: Shadcn/ui DataTable, Dialog components
- **DEP-002**: Admin strategy API endpoints
- **DEP-003**: SSE for real-time status updates

---

## 4. Files

### Admin Strategy Pages

- **FILE-001**: `admin-web/app/(admin)/admin/strategies/page.tsx` - All strategies
- **FILE-002**: `admin-web/app/(admin)/admin/strategies/[id]/page.tsx` - Strategy detail
- **FILE-003**: `admin-web/app/(admin)/admin/strategies/loading.tsx` - Loading state

### Admin Strategy Components

- **FILE-004**: `admin-web/components/admin/AllStrategiesTable.tsx` - Data table
- **FILE-005**: `admin-web/components/admin/StrategyFilters.tsx` - Filter controls
- **FILE-006**: `admin-web/components/admin/AdminStrategyDetail.tsx` - Detail view
- **FILE-007**: `admin-web/components/admin/ForceStopButton.tsx` - Emergency stop
- **FILE-008**: `admin-web/components/admin/StrategyHealth.tsx` - Health indicators
- **FILE-009**: `admin-web/components/admin/StrategyAuditLog.tsx` - Audit trail
- **FILE-010**: `admin-web/components/admin/BulkStrategyActions.tsx` - Bulk ops

---

## Strategy Table Columns (Admin)

| Column | Description | Sortable | Filterable |
|--------|-------------|----------|------------|
| ID | Strategy ID | No | No |
| User | Owner name | Yes | Dropdown |
| Symbol | Trading symbol | Yes | Search |
| Status | Running/Stopped/Error | No | Dropdown |
| Broker | Zerodha/Dhan/etc | No | Dropdown |
| P&L | Profit/Loss | Yes | No |
| Orders | Executed order count | Yes | No |
| Error Rate | % of failed orders | Yes | No |
| Last Run | Last execution time | Yes | Date range |
| Actions | View, Force-Stop | No | No |

---

## Success Criteria

✅ Phase 12 is complete when:

- [ ] All strategies table with user column
- [ ] Filters by user, status, broker, date range
- [ ] Strategy detail view (admin)
- [ ] Emergency force-stop functionality
- [ ] Execution log viewing
- [ ] Health indicators (error rate, success rate)
- [ ] Bulk force-stop for user
- [ ] Audit trail for admin actions

---

## Next Phase

[Phase 13: Admin - System Monitoring →](./phase-13-admin-system.md)
