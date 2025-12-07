---
goal: Implement SSE-based real-time updates throughout the application
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [admin-web, nextjs, sse, real-time, hooks, events]
---

# Phase 16: Real-Time Features

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement Server-Sent Events (SSE) based real-time updates throughout the application for strategy status, system metrics, and order notifications.

---

## 1. Requirements & Constraints

### Technical Requirements

- **REQ-001**: Generic SSE hook for reusability
- **REQ-002**: Automatic reconnection on disconnect
- **REQ-003**: Authentication via query parameter
- **REQ-004**: Event type handlers for different events

### Event Types

- **EVT-001**: ORDER_EXECUTED - Order placed successfully
- **EVT-002**: SL_TRIGGERED - Stop-loss triggered
- **EVT-003**: STRATEGY_STARTED - Strategy started
- **EVT-004**: STRATEGY_STOPPED - Strategy stopped
- **EVT-005**: STRATEGY_ERROR - Strategy encountered error

### Constraints

- **CON-001**: SSE must work with authentication
- **CON-002**: Cleanup on component unmount
- **CON-003**: Show connection status indicator

---

## 2. Implementation Tasks

### GOAL-016: Implement SSE-based real-time updates throughout the application

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

---

## 3. Dependencies

- **DEP-001**: eventsource-polyfill (for SSE support)
- **DEP-002**: Zustand for event state management
- **DEP-003**: Toast library for notifications
- **DEP-004**: Backend SSE endpoints

---

## 4. Files

### SSE Hooks

- **FILE-001**: `admin-web/hooks/useSSE.ts` - Generic SSE hook
- **FILE-002**: `admin-web/hooks/useStrategyStream.ts` - Strategy updates
- **FILE-003**: `admin-web/hooks/useSystemMetrics.ts` - System metrics
- **FILE-004**: `admin-web/hooks/useOrderEvents.ts` - Order execution events
- **FILE-005**: `admin-web/hooks/useNotificationStream.ts` - Notifications

### Components

- **FILE-006**: `admin-web/components/common/ConnectionStatus.tsx` - SSE status
- **FILE-007**: `admin-web/components/common/RealtimeIndicator.tsx` - Live indicator

### Types

- **FILE-008**: `admin-web/types/sse.ts` - SSE event type definitions

### Store

- **FILE-009**: `admin-web/store/sseStore.ts` - SSE connection state

---

## SSE Hook Architecture

```typescript
// hooks/useSSE.ts
interface UseSSEOptions {
  url: string;
  events?: string[];
  onMessage?: (event: SSEEvent) => void;
  onError?: (error: Event) => void;
  onOpen?: () => void;
  reconnectInterval?: number;
}

function useSSE(options: UseSSEOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null);
  
  // Connection management
  // Auto-reconnect
  // Cleanup on unmount
  
  return { isConnected, lastEvent, reconnect };
}

// hooks/useStrategyStream.ts
function useStrategyStream(strategyId: string) {
  const { data, isConnected } = useSSE({
    url: `/api/strategies/${strategyId}/stream`,
    events: ['STRATEGY_UPDATED', 'ORDER_EXECUTED', 'SL_TRIGGERED'],
  });
  
  return { strategy: data, isLive: isConnected };
}
```

---

## Event Flow

```text
Backend SSE Endpoint
        │
        ▼
    useSSE Hook
        │
        ├── Parse Event Type
        │
        ├── ORDER_EXECUTED → Toast + Update UI
        ├── SL_TRIGGERED → Toast + Update UI  
        ├── STRATEGY_STARTED → Update Status Badge
        ├── STRATEGY_STOPPED → Update Status Badge
        └── STRATEGY_ERROR → Toast + Error Display
```

---

## Success Criteria

✅ Phase 16 is complete when:

- [ ] Generic useSSE hook created
- [ ] Strategy stream hook working
- [ ] System metrics stream hook working
- [ ] Automatic reconnection on disconnect
- [ ] Connection status indicator visible
- [ ] Toast notifications on order events
- [ ] SSE authentication with token
- [ ] Event type handlers for all events
- [ ] Proper cleanup on unmount
- [ ] Optimistic UI updates

---

## Next Phase

[Phase 17: Common UI Components →](./phase-17-ui-components.md)
