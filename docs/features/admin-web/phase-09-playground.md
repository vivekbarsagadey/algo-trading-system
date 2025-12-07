---
goal: Implement strategy testing sandbox without real money
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [admin-web, nextjs, playground, simulation, backtesting]
---

# Phase 9: Strategy Playground

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement the strategy playground for testing strategies in a sandbox environment without real money, including backtesting with historical data.

---

## 1. Requirements & Constraints

### Technical Requirements

- **REQ-001**: Clear "simulation mode" visual indicators
- **REQ-002**: Historical date range selection for backtesting
- **REQ-003**: Simulation speed controls
- **REQ-004**: P&L visualization for simulated trades

### Business Requirements

- **BIZ-001**: No real orders placed from playground
- **BIZ-002**: Simulated results must be clearly labeled
- **BIZ-003**: Compare simulated vs actual results

### Constraints

- **CON-001**: Playground strategies not visible in main strategy list
- **CON-002**: Historical data availability depends on backend
- **CON-003**: Simulation uses synthetic execution (no broker calls)

---

## 2. Implementation Tasks

### GOAL-009: Implement strategy testing sandbox without real money

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

---

## 3. Dependencies

- **DEP-001**: Recharts for P&L visualization
- **DEP-002**: date-fns for date manipulation
- **DEP-003**: Backend simulation API endpoints
- **DEP-004**: StrategyForm component from Phase 7

---

## 4. Files

### Playground Pages

- **FILE-001**: `admin-web/app/(dashboard)/playground/page.tsx` - Playground home
- **FILE-002**: `admin-web/app/(dashboard)/playground/new/page.tsx` - Create simulation
- **FILE-003**: `admin-web/app/(dashboard)/playground/[id]/page.tsx` - Simulation detail
- **FILE-004**: `admin-web/app/(dashboard)/playground/loading.tsx` - Loading state

### Playground Components

- **FILE-005**: `admin-web/components/playground/PlaygroundBanner.tsx` - Simulation warning
- **FILE-006**: `admin-web/components/playground/SimulationForm.tsx` - Strategy + date range
- **FILE-007**: `admin-web/components/playground/SimulationResults.tsx` - P&L display
- **FILE-008**: `admin-web/components/playground/TradeTimeline.tsx` - Trade history
- **FILE-009**: `admin-web/components/playground/SpeedControls.tsx` - Simulation speed
- **FILE-010**: `admin-web/components/playground/ComparisonView.tsx` - Simulated vs actual
- **FILE-011**: `admin-web/components/playground/DateRangeSelector.tsx` - Backtest dates
- **FILE-012**: `admin-web/components/playground/ExportButton.tsx` - CSV export

### Types

- **FILE-013**: `admin-web/types/simulation.ts` - Simulation type definitions

---

## Playground UI Flow

```text
Playground Home
├── [+ New Simulation] → Create Simulation Form
│   ├── Strategy Parameters (reuse StrategyForm)
│   └── Date Range Selection (historical backtesting)
│
└── Simulation List
    └── Simulation Detail
        ├── P&L Chart
        ├── Trade Timeline
        ├── Speed Controls
        ├── Comparison View
        └── Export CSV
```

---

## Success Criteria

✅ Phase 9 is complete when:

- [ ] Playground home page with simulation list
- [ ] Clear "simulation mode" banner on all playground pages
- [ ] Simulation creation form with date range
- [ ] Simulation detail with P&L visualization
- [ ] Trade timeline showing simulated executions
- [ ] Speed controls (1x, 5x, 10x)
- [ ] Comparison view (simulated vs actual)
- [ ] CSV export functionality
- [ ] No real orders placed from playground

---

## Next Phase

[Phase 10: User Profile & Settings →](./phase-10-profile-settings.md)
