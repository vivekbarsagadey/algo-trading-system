---
goal: Implement client-side state management with Zustand
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [admin-web, nextjs, zustand, state-management, stores]
---

# Phase 18: State Management

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement client-side state management using Zustand for authentication, strategies, brokers, notifications, and UI state with persistence and devtools.

---

## 1. Requirements & Constraints

### Technical Requirements

- **REQ-001**: Zustand for lightweight state management
- **REQ-002**: Store persistence for selected data
- **REQ-003**: Optimized selectors to prevent re-renders
- **REQ-004**: DevTools integration for debugging

### State Categories

- **STA-001**: Authentication state (user, session, role)
- **STA-002**: Strategy state (active strategies, current strategy)
- **STA-003**: Broker state (connected brokers)
- **STA-004**: Notification state (notifications, unread count)
- **STA-005**: UI state (sidebar, theme, modals)

### Constraints

- **CON-001**: Sensitive data not persisted
- **CON-002**: Hydration issues with SSR handled
- **CON-003**: Store cleanup on logout

---

## 2. Implementation Tasks

### GOAL-018: Implement client-side state management with Zustand

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

---

## 3. Dependencies

- **DEP-001**: zustand
- **DEP-002**: zustand/middleware (persist, devtools)
- **DEP-003**: immer (optional, for complex updates)

---

## 4. Files

### Store Files

- **FILE-001**: `admin-web/store/authStore.ts` - Authentication state
- **FILE-002**: `admin-web/store/strategyStore.ts` - Strategy state
- **FILE-003**: `admin-web/store/brokerStore.ts` - Broker state
- **FILE-004**: `admin-web/store/notificationStore.ts` - Notifications
- **FILE-005**: `admin-web/store/uiStore.ts` - UI state
- **FILE-006**: `admin-web/store/index.ts` - Store exports

### Utilities

- **FILE-007**: `admin-web/lib/store-utils.ts` - Persistence helpers

---

## Store Definitions

### Auth Store

```typescript
interface AuthState {
  user: User | null;
  role: Role | null;
  isAuthenticated: boolean;
  
  // Actions
  setUser: (user: User) => void;
  logout: () => void;
}
```

### Strategy Store

```typescript
interface StrategyState {
  strategies: Strategy[];
  currentStrategy: Strategy | null;
  isLoading: boolean;
  
  // Actions
  setStrategies: (strategies: Strategy[]) => void;
  updateStrategy: (id: string, updates: Partial<Strategy>) => void;
  setCurrentStrategy: (strategy: Strategy | null) => void;
}
```

### Broker Store

```typescript
interface BrokerState {
  brokers: Broker[];
  selectedBroker: Broker | null;
  
  // Actions
  setBrokers: (brokers: Broker[]) => void;
  addBroker: (broker: Broker) => void;
  removeBroker: (id: string) => void;
}
```

### Notification Store

```typescript
interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  
  // Actions
  addNotification: (notification: Notification) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearNotifications: () => void;
}
```

### UI Store

```typescript
interface UIState {
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark' | 'system';
  
  // Actions
  toggleSidebar: () => void;
  setTheme: (theme: Theme) => void;
}
```

---

## Persistence Configuration

```typescript
// Stores with persistence
const persistedStores = ['uiStore', 'notificationStore'];

// Stores without persistence (security)
const volatileStores = ['authStore', 'strategyStore', 'brokerStore'];
```

---

## Success Criteria

✅ Phase 18 is complete when:

- [ ] Auth store with user/role state
- [ ] Strategy store with CRUD operations
- [ ] Broker store with connection state
- [ ] Notification store with unread count
- [ ] UI store with sidebar/theme state
- [ ] Persistence for UI and notification stores
- [ ] Optimized selectors preventing re-renders
- [ ] DevTools integration working
- [ ] Store cleanup on logout

---

## Next Phase

[Phase 19: Error Handling & Notifications →](./phase-19-error-handling.md)
