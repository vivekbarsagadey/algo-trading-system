---
goal: Implement complete strategy CRUD with real-time status updates
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [admin-web, nextjs, strategy, crud, forms, sse]
---

# Phase 7: Strategy Management

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement complete strategy management with list, create, detail, edit views, and real-time status updates via SSE.

---

## 1. Requirements & Constraints

### Technical Requirements

- **REQ-001**: Full CRUD operations for strategies
- **REQ-002**: Real-time status updates via SSE
- **REQ-003**: Form validation with Zod
- **REQ-004**: Symbol autocomplete search

### Business Requirements

- **BIZ-001**: Mandatory stop-loss for every strategy
- **BIZ-002**: buy_time must be before sell_time
- **BIZ-003**: Maximum 5 required inputs for creation
- **BIZ-004**: Single-tap start/stop controls

### Constraints

- **CON-001**: Only owner can modify strategy
- **CON-002**: Running strategies cannot be deleted
- **CON-003**: Symbol must be valid tradable instrument

---

## 2. Implementation Tasks

### GOAL-007: Implement complete strategy CRUD with real-time status updates

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

---

## 3. Dependencies

- **DEP-001**: React Hook Form + Zod for forms
- **DEP-002**: Shadcn/ui DataTable, Form, Dialog components
- **DEP-003**: Backend strategy API endpoints
- **DEP-004**: SSE endpoint for strategy updates

---

## 4. Files

### Strategy Pages

- **FILE-001**: `admin-web/app/(dashboard)/strategies/page.tsx` - Strategy list
- **FILE-002**: `admin-web/app/(dashboard)/strategies/new/page.tsx` - Create strategy
- **FILE-003**: `admin-web/app/(dashboard)/strategies/[id]/page.tsx` - Strategy detail
- **FILE-004**: `admin-web/app/(dashboard)/strategies/[id]/edit/page.tsx` - Edit strategy
- **FILE-005**: `admin-web/app/(dashboard)/strategies/loading.tsx` - Loading state

### Strategy Components

- **FILE-006**: `admin-web/components/strategies/StrategyTable.tsx` - Data table
- **FILE-007**: `admin-web/components/strategies/StrategyFilters.tsx` - Filters
- **FILE-008**: `admin-web/components/strategies/StrategyForm.tsx` - Create/Edit form
- **FILE-009**: `admin-web/components/strategies/StrategyDetail.tsx` - Detail view
- **FILE-010**: `admin-web/components/strategies/StrategyControls.tsx` - Start/Stop buttons
- **FILE-011**: `admin-web/components/strategies/ExecutionLog.tsx` - Order history
- **FILE-012**: `admin-web/components/strategies/SymbolAutocomplete.tsx` - Symbol search
- **FILE-013**: `admin-web/components/strategies/StatusBadge.tsx` - Status indicator
- **FILE-014**: `admin-web/components/strategies/DeleteDialog.tsx` - Delete confirmation

### Hooks

- **FILE-015**: `admin-web/hooks/useStrategyStream.ts` - SSE subscription hook

### Types

- **FILE-016**: `admin-web/types/strategy.ts` - Strategy type definitions

---

## Strategy Form Fields

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| symbol | string | Yes | Valid tradable instrument |
| quantity | number | Yes | > 0 |
| buy_time | time | Yes | HH:MM format, < sell_time |
| sell_time | time | Yes | HH:MM format, > buy_time |
| stop_loss | number | Yes | > 0, < 100 if percentage |
| broker_id | string | Yes | Connected broker |
| strategy_type | enum | Yes | INTRADAY |

---

## Success Criteria

✅ Phase 7 is complete when:

- [ ] Strategy list with pagination and sorting
- [ ] Strategy filtering by status and date
- [ ] Strategy creation form with validation
- [ ] Symbol autocomplete working
- [ ] Time pickers for buy/sell time
- [ ] Stop-loss input with percentage toggle
- [ ] Strategy detail page with full info
- [ ] Start/Stop controls working
- [ ] Execution log showing order history
- [ ] Strategy editing functionality
- [ ] Real-time status updates via SSE
- [ ] Delete with confirmation dialog

---

## Next Phase

[Phase 8: Broker Integration →](./phase-08-broker-integration.md)
