---
goal: Implement platform-wide analytics and reporting
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [admin-web, nextjs, admin, analytics, reporting, charts]
---

# Phase 14: Admin - Analytics Dashboard

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement platform-wide analytics and reporting dashboard for admins with user growth, order volume, broker distribution, and custom reports.

---

## 1. Requirements & Constraints

### Technical Requirements

- **REQ-001**: Charts for key platform metrics
- **REQ-002**: Date range selection for all charts
- **REQ-003**: Data export to CSV/JSON
- **REQ-004**: Custom report builder

### Analytics Scope

- **ANL-001**: User registration trends
- **ANL-002**: Order volume over time
- **ANL-003**: Broker usage distribution
- **ANL-004**: Order success rate trends
- **ANL-005**: Top performers (users, strategies)

### Constraints

- **CON-001**: Only Admin role can access
- **CON-002**: Large data sets paginated
- **CON-003**: Report generation async for large ranges

---

## 2. Implementation Tasks

### GOAL-014: Implement platform-wide analytics and reporting

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

---

## 3. Dependencies

- **DEP-001**: Recharts for data visualization
- **DEP-002**: date-fns for date manipulation
- **DEP-003**: Backend analytics API endpoints
- **DEP-004**: file-saver for downloads

---

## 4. Files

### Analytics Pages

- **FILE-001**: `admin-web/app/(admin)/admin/analytics/page.tsx` - Analytics home
- **FILE-002**: `admin-web/app/(admin)/admin/analytics/reports/page.tsx` - Custom reports
- **FILE-003**: `admin-web/app/(admin)/admin/analytics/loading.tsx` - Loading state

### Analytics Components

- **FILE-004**: `admin-web/components/admin/UserGrowthChart.tsx` - User trends
- **FILE-005**: `admin-web/components/admin/OrderVolumeChart.tsx` - Order volume
- **FILE-006**: `admin-web/components/admin/BrokerDistribution.tsx` - Broker pie chart
- **FILE-007**: `admin-web/components/admin/SuccessRateChart.tsx` - Success trends
- **FILE-008**: `admin-web/components/admin/DateRangeFilter.tsx` - Date selector
- **FILE-009**: `admin-web/components/admin/ExportButton.tsx` - CSV/JSON export
- **FILE-010**: `admin-web/components/admin/TopPerformers.tsx` - Leaderboard
- **FILE-011**: `admin-web/components/admin/ComparisonChart.tsx` - Period compare
- **FILE-012**: `admin-web/components/admin/ReportBuilder.tsx` - Custom reports

---

## Analytics Dashboard Layout

```text
┌─────────────────────────────────────────────────────────────┐
│  Date Range: [Last 7 Days ▼]  [Export CSV] [Export JSON]    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐   │
│  │   User Growth                                         │   │
│  │   [Area Chart - Registrations over time]              │   │
│  └──────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────────────────┐  ┌────────────────────────┐     │
│  │   Order Volume         │  │   Broker Distribution  │     │
│  │   [Bar Chart]          │  │   [Pie Chart]          │     │
│  └────────────────────────┘  └────────────────────────┘     │
├─────────────────────────────────────────────────────────────┤
│  ┌────────────────────────┐  ┌────────────────────────┐     │
│  │   Success Rate         │  │   Top Performers       │     │
│  │   [Line Chart]         │  │   [Leaderboard]        │     │
│  └────────────────────────┘  └────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Success Criteria

✅ Phase 14 is complete when:

- [ ] Analytics dashboard page
- [ ] User growth chart with registration trends
- [ ] Order volume chart (daily/weekly/monthly)
- [ ] Broker distribution pie chart
- [ ] Order success rate chart
- [ ] Date range selector for all charts
- [ ] Export to CSV and JSON
- [ ] Top performers list
- [ ] Period comparison view
- [ ] Custom report builder

---

## Next Phase

[Phase 15: Admin - Logs & Audit →](./phase-15-admin-logs.md)
