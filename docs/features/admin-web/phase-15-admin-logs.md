---
goal: Implement log viewing and audit trail for compliance
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [admin-web, nextjs, admin, logs, audit, compliance]
---

# Phase 15: Admin - Logs & Audit

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement log viewing and audit trail for compliance, including order execution logs, error logs, and admin action audit trail.

---

## 1. Requirements & Constraints

### Technical Requirements

- **REQ-001**: Order execution log viewer
- **REQ-002**: Error log viewer with severity levels
- **REQ-003**: Admin audit trail
- **REQ-004**: Log search and filtering

### Compliance Requirements

- **CMP-001**: All admin actions logged
- **CMP-002**: Logs immutable (read-only)
- **CMP-003**: Retention policy visible

### Constraints

- **CON-001**: Only Admin role can access
- **CON-002**: Large log sets paginated
- **CON-003**: Log export for compliance audits

---

## 2. Implementation Tasks

### GOAL-015: Implement log viewing and audit trail for compliance

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

---

## 3. Dependencies

- **DEP-001**: Shadcn/ui DataTable components
- **DEP-002**: Backend logs API endpoints
- **DEP-003**: date-fns for timestamp formatting

---

## 4. Files

### Logs Pages

- **FILE-001**: `admin-web/app/(admin)/admin/logs/page.tsx` - Logs dashboard
- **FILE-002**: `admin-web/app/(admin)/admin/logs/orders/page.tsx` - Order logs
- **FILE-003**: `admin-web/app/(admin)/admin/logs/errors/page.tsx` - Error logs
- **FILE-004**: `admin-web/app/(admin)/admin/logs/audit/page.tsx` - Audit trail
- **FILE-005**: `admin-web/app/(admin)/admin/logs/loading.tsx` - Loading state

### Logs Components

- **FILE-006**: `admin-web/components/admin/OrderLogTable.tsx` - Order log table
- **FILE-007**: `admin-web/components/admin/ErrorLogTable.tsx` - Error log table
- **FILE-008**: `admin-web/components/admin/AuditLogTable.tsx` - Audit log table
- **FILE-009**: `admin-web/components/admin/LogFilters.tsx` - Filter controls
- **FILE-010**: `admin-web/components/admin/LogSearch.tsx` - Search with regex
- **FILE-011**: `admin-web/components/admin/LogExport.tsx` - Export button
- **FILE-012**: `admin-web/components/admin/RetentionPolicy.tsx` - Policy display
- **FILE-013**: `admin-web/components/admin/SeverityBadge.tsx` - Error severity

---

## Log Types

### Order Execution Logs

| Column | Description |
|--------|-------------|
| Timestamp | When order was executed |
| Strategy ID | Related strategy |
| User | Strategy owner |
| Symbol | Trading symbol |
| Action | BUY/SELL |
| Quantity | Number of shares |
| Price | Execution price |
| Status | Success/Failed |
| Broker | Broker used |
| Latency | Execution time |

### Error Logs

| Column | Description |
|--------|-------------|
| Timestamp | When error occurred |
| Severity | ERROR/WARN/INFO |
| Service | Which service |
| Message | Error description |
| Stack Trace | Full stack (expandable) |
| User ID | Affected user (if applicable) |
| Strategy ID | Affected strategy (if applicable) |

### Admin Audit Trail

| Column | Description |
|--------|-------------|
| Timestamp | When action occurred |
| Admin | Admin who performed action |
| Action | What was done |
| Target | User/Strategy affected |
| Details | Additional context |
| IP Address | Admin's IP |

---

## Success Criteria

✅ Phase 15 is complete when:

- [ ] Logs dashboard with navigation
- [ ] Order execution log viewer
- [ ] Order log filtering (user, symbol, status, date)
- [ ] Error log viewer with severity levels
- [ ] Error log filtering (severity, service, date)
- [ ] Admin audit trail viewer
- [ ] Log search with regex support
- [ ] Log export functionality
- [ ] Retention policy display
- [ ] Pagination for large log sets

---

## Next Phase

[Phase 16: Real-Time Features →](./phase-16-realtime.md)
