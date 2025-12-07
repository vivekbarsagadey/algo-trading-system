---
goal: Build reusable UI component library using Shadcn/ui
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [admin-web, nextjs, shadcn, ui-components, design-system]
---

# Phase 17: Common UI Components

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Build reusable UI component library using Shadcn/ui components, including data tables, forms, dialogs, and custom components for the trading platform.

---

## 1. Requirements & Constraints

### Technical Requirements

- **REQ-001**: Shadcn/ui as base component library
- **REQ-002**: Custom components for domain-specific needs
- **REQ-003**: Consistent styling and behavior
- **REQ-004**: Accessibility compliance

### UI/UX Requirements

- **UXR-001**: Loading states for all async operations
- **UXR-002**: Empty states for empty lists
- **UXR-003**: Error boundaries for failures
- **UXR-004**: Confirmation dialogs for destructive actions

### Constraints

- **CON-001**: Use Tailwind CSS for styling
- **CON-002**: Components must be accessible
- **CON-003**: Support dark mode

---

## 2. Implementation Tasks

### GOAL-017: Build reusable UI component library using Shadcn/ui

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

---

## 3. Dependencies

- **DEP-001**: @radix-ui (via Shadcn/ui)
- **DEP-002**: Tailwind CSS
- **DEP-003**: Lucide React icons
- **DEP-004**: date-fns for date handling
- **DEP-005**: @tanstack/react-table for DataTable

---

## 4. Files

### Shadcn UI Components (Generated)

- **FILE-001**: `admin-web/components/ui/button.tsx`
- **FILE-002**: `admin-web/components/ui/input.tsx`
- **FILE-003**: `admin-web/components/ui/form.tsx`
- **FILE-004**: `admin-web/components/ui/table.tsx`
- **FILE-005**: `admin-web/components/ui/card.tsx`
- **FILE-006**: `admin-web/components/ui/dialog.tsx`
- **FILE-007**: `admin-web/components/ui/dropdown-menu.tsx`
- **FILE-008**: `admin-web/components/ui/tabs.tsx`
- **FILE-009**: `admin-web/components/ui/toast.tsx`
- **FILE-010**: `admin-web/components/ui/tooltip.tsx`
- **FILE-011**: `admin-web/components/ui/badge.tsx`
- **FILE-012**: `admin-web/components/ui/avatar.tsx`
- **FILE-013**: `admin-web/components/ui/separator.tsx`

### Custom Components

- **FILE-014**: `admin-web/components/ui/DataTable.tsx` - Sortable, filterable table
- **FILE-015**: `admin-web/components/ui/SearchInput.tsx` - Debounced search
- **FILE-016**: `admin-web/components/ui/DateRangePicker.tsx` - Date range selection
- **FILE-017**: `admin-web/components/ui/TimeInput.tsx` - Time picker
- **FILE-018**: `admin-web/components/ui/ConfirmDialog.tsx` - Confirmation modal
- **FILE-019**: `admin-web/components/ui/LoadingSpinner.tsx` - Spinner component
- **FILE-020**: `admin-web/components/ui/LoadingSkeleton.tsx` - Skeleton loading
- **FILE-021**: `admin-web/components/ui/EmptyState.tsx` - Empty list state
- **FILE-022**: `admin-web/components/ui/ErrorBoundary.tsx` - Error boundary
- **FILE-023**: `admin-web/components/ui/StatusBadge.tsx` - Status indicators
- **FILE-024**: `admin-web/components/ui/CurrencyDisplay.tsx` - P&L formatting

---

## Component Specifications

### DataTable

```typescript
interface DataTableProps<T> {
  data: T[];
  columns: ColumnDef<T>[];
  searchKey?: string;
  filterOptions?: FilterOption[];
  pagination?: boolean;
  pageSize?: number;
  onRowClick?: (row: T) => void;
}
```

### StatusBadge

```typescript
type Status = 'running' | 'stopped' | 'error' | 'pending' | 'completed';

interface StatusBadgeProps {
  status: Status;
  size?: 'sm' | 'md' | 'lg';
  animated?: boolean; // Pulse animation for active states
}
```

### CurrencyDisplay

```typescript
interface CurrencyDisplayProps {
  value: number;
  currency?: 'INR' | 'USD';
  showSign?: boolean; // +/- for P&L
  colorize?: boolean; // Green for profit, red for loss
}
```

---

## Success Criteria

✅ Phase 17 is complete when:

- [ ] All Shadcn base components installed
- [ ] DataTable with sorting, filtering, pagination
- [ ] SearchInput with debounce
- [ ] DateRangePicker for date selection
- [ ] TimeInput for time selection
- [ ] ConfirmDialog for destructive actions
- [ ] LoadingSpinner and LoadingSkeleton
- [ ] EmptyState for empty lists
- [ ] ErrorBoundary for error handling
- [ ] StatusBadge for status indicators
- [ ] CurrencyDisplay for P&L
- [ ] All components support dark mode

---

## Next Phase

[Phase 18: State Management →](./phase-18-state-management.md)
