---
goal: Create application layouts with navigation and responsive sidebar
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [admin-web, nextjs, layout, navigation, sidebar, responsive]
---

# Phase 5: Layout & Navigation

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Create responsive application layouts with collapsible sidebar navigation, role-based menu items, dark mode support, and mobile-friendly design.

---

## 1. Requirements & Constraints

### UI/UX Requirements

- **UXR-001**: Collapsible sidebar navigation
- **UXR-002**: Role-based navigation items
- **UXR-003**: Dark mode support with persistence
- **UXR-004**: Mobile-responsive navigation
- **UXR-005**: Breadcrumb navigation

### Patterns

- **PAT-001**: Layout composition with route groups
- **PAT-002**: Client-side navigation state
- **PAT-003**: Role-based menu filtering
- **PAT-004**: Theme persistence with localStorage

### Constraints

- **CON-001**: Admin nav items only visible to Admin role
- **CON-002**: Broker nav items only visible to Broker role
- **CON-003**: Sidebar state persists across sessions

---

## 2. Implementation Tasks

### GOAL-005: Create application layouts with navigation and responsive sidebar

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

---

## 3. Dependencies

- **DEP-001**: Shadcn/ui components (sheet, button, dropdown-menu)
- **DEP-002**: Lucide React icons
- **DEP-003**: next-themes for dark mode
- **DEP-004**: Zustand for sidebar state

---

## 4. Files

### Root Layout

- **FILE-001**: `admin-web/app/layout.tsx` - Root layout with providers

### Layouts

- **FILE-002**: `admin-web/app/(dashboard)/layout.tsx` - Dashboard layout
- **FILE-003**: `admin-web/app/(admin)/layout.tsx` - Admin layout
- **FILE-004**: `admin-web/app/(broker)/layout.tsx` - Broker layout

### Layout Components

- **FILE-005**: `admin-web/components/layout/Sidebar.tsx` - Main sidebar
- **FILE-006**: `admin-web/components/layout/MobileSidebar.tsx` - Mobile navigation
- **FILE-007**: `admin-web/components/layout/Header.tsx` - Page header
- **FILE-008**: `admin-web/components/layout/NavItem.tsx` - Navigation item
- **FILE-009**: `admin-web/components/layout/Breadcrumb.tsx` - Breadcrumb navigation
- **FILE-010**: `admin-web/components/layout/Footer.tsx` - Page footer
- **FILE-011**: `admin-web/components/layout/UserMenu.tsx` - User dropdown menu
- **FILE-012**: `admin-web/components/layout/ThemeToggle.tsx` - Dark mode toggle
- **FILE-013**: `admin-web/components/layout/SearchCommand.tsx` - Cmd+K search overlay

### Configuration

- **FILE-014**: `admin-web/config/navigation.ts` - Navigation item definitions

### Providers

- **FILE-015**: `admin-web/providers/ThemeProvider.tsx` - Theme context provider

---

## Navigation Structure

### User Navigation

```text
Dashboard
├── Strategies
│   ├── All Strategies
│   ├── Create Strategy
│   └── [Strategy Detail]
├── Brokers
│   ├── Connected Brokers
│   └── Connect New
├── Playground
└── Profile
    └── Settings
```

### Admin Navigation

```text
Admin
├── Users
│   ├── All Users
│   └── [User Detail]
├── All Strategies
├── System Health
├── Analytics
└── Logs
    ├── Order Logs
    ├── Error Logs
    └── Audit Trail
```

---

## Success Criteria

✅ Phase 5 is complete when:

- [ ] Root layout with all providers
- [ ] Collapsible sidebar navigation
- [ ] Mobile-responsive navigation (Sheet/Drawer)
- [ ] Role-based navigation items
- [ ] User menu with logout, profile links
- [ ] Dark mode toggle with persistence
- [ ] Breadcrumb navigation
- [ ] Dashboard layout for user pages
- [ ] Admin layout with admin navigation
- [ ] Keyboard shortcuts (Cmd+K)

---

## Next Phase

[Phase 6: Dashboard & Home →](./phase-06-dashboard.md)
