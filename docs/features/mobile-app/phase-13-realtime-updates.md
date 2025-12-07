---
goal: Implement polling and WebSocket for real-time strategy status
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, real-time, polling, websocket, status-updates]
---

# Phase 13: Real-Time Status Updates

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement real-time strategy status updates using polling (primary) with optional WebSocket enhancement for lower latency updates.

---

## 1. Requirements & Constraints

- **PER-004**: Background refresh for active strategies every 5 seconds
- **UXR-004**: Clear visual feedback for all actions
- **CON-003**: Real-time prices require active network connection

---

## 2. Implementation Tasks

### GOAL-013: Implement polling and WebSocket for real-time strategy status

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-150 | Create `hooks/useStrategyPolling.ts`: poll strategy status every 5 seconds when strategy is RUNNING | | | Phase 4 |
| TASK-151 | Implement polling logic: useEffect with setInterval, only when app is in foreground and strategy is active | | | TASK-150 |
| TASK-152 | Update Zustand store with new status data: merge updates into strategyStore | | | TASK-150 |
| TASK-153 | Trigger re-render of strategy cards on status change: compare previous and current state | | | TASK-152 |
| TASK-154 | Display visual indicator when status changes: brief pulse animation on changed fields | | | TASK-153 |
| TASK-155 | Implement optimistic UI updates for start/stop actions: update UI immediately, rollback on error | | | TASK-150 |
| TASK-156 | Create WebSocket connection for real-time updates (optional enhancement): connect to /ws/strategies | | | TASK-150 |
| TASK-157 | Handle connection loss gracefully: show connection status, auto-reconnect with exponential backoff | | | TASK-156 |
| TASK-158 | Show connection status indicator in header: green dot when connected, yellow when reconnecting, red when offline | | | TASK-157 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/hooks/useStrategyPolling.ts` | Create | Strategy status polling hook |
| `mobile/hooks/useAppState.ts` | Create | App foreground/background state hook |
| `mobile/services/websocket.ts` | Create | WebSocket connection service (optional) |
| `mobile/components/common/ConnectionIndicator.tsx` | Create | Connection status indicator |
| `mobile/components/common/PulseAnimation.tsx` | Create | Pulse animation for changes |
| `mobile/store/strategyStore.ts` | Modify | Add real-time update handling |
| `mobile/store/connectionStore.ts` | Create | Connection state management |

---

## 4. Acceptance Criteria

- [ ] Polling fetches updates every 5 seconds for running strategies
- [ ] Polling pauses when app is in background
- [ ] Store updates with new status data
- [ ] UI re-renders when status changes
- [ ] Pulse animation shows on changed values
- [ ] Optimistic updates work for start/stop
- [ ] Connection status visible in UI
- [ ] Reconnection works after network loss

---

## 5. Technical Notes

### Strategy Polling Hook

```typescript
// hooks/useStrategyPolling.ts
import { useEffect, useRef, useCallback } from 'react';
import { AppState, AppStateStatus } from 'react-native';
import { useQueryClient } from '@tanstack/react-query';
import { getStrategy } from '@/api/strategies';

interface UseStrategyPollingOptions {
  strategyId: string;
  enabled: boolean;
  interval?: number;
}

export function useStrategyPolling({
  strategyId,
  enabled,
  interval = 5000,
}: UseStrategyPollingOptions) {
  const queryClient = useQueryClient();
  const appState = useRef(AppState.currentState);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const poll = useCallback(async () => {
    try {
      const data = await getStrategy(strategyId);
      queryClient.setQueryData(['strategy', strategyId], data);
    } catch (error) {
      console.error('Polling error:', error);
    }
  }, [strategyId, queryClient]);

  useEffect(() => {
    if (!enabled) return;

    // Start polling
    intervalRef.current = setInterval(poll, interval);

    // Handle app state changes
    const subscription = AppState.addEventListener('change', (nextAppState: AppStateStatus) => {
      if (appState.current === 'active' && nextAppState.match(/inactive|background/)) {
        // App going to background - stop polling
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      } else if (appState.current.match(/inactive|background/) && nextAppState === 'active') {
        // App coming to foreground - resume polling
        poll(); // Immediate poll
        intervalRef.current = setInterval(poll, interval);
      }
      appState.current = nextAppState;
    });

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      subscription.remove();
    };
  }, [enabled, poll, interval]);
}
```

### Optimistic Updates

```typescript
// hooks/useStartStrategy.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { startStrategy } from '@/api/strategies';

export function useStartStrategy() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: startStrategy,
    onMutate: async (strategyId) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['strategy', strategyId] });

      // Snapshot previous value
      const previousStrategy = queryClient.getQueryData(['strategy', strategyId]);

      // Optimistically update
      queryClient.setQueryData(['strategy', strategyId], (old: Strategy) => ({
        ...old,
        status: 'RUNNING',
      }));

      return { previousStrategy };
    },
    onError: (err, strategyId, context) => {
      // Rollback on error
      queryClient.setQueryData(
        ['strategy', strategyId],
        context?.previousStrategy
      );
    },
    onSettled: (data, error, strategyId) => {
      // Always refetch after error or success
      queryClient.invalidateQueries({ queryKey: ['strategy', strategyId] });
    },
  });
}
```

### Connection Status Store

```typescript
// store/connectionStore.ts
import { create } from 'zustand';

type ConnectionStatus = 'connected' | 'connecting' | 'disconnected';

interface ConnectionState {
  status: ConnectionStatus;
  lastConnected: Date | null;
  setStatus: (status: ConnectionStatus) => void;
}

export const useConnectionStore = create<ConnectionState>((set) => ({
  status: 'connected',
  lastConnected: null,
  setStatus: (status) => set({ 
    status,
    lastConnected: status === 'connected' ? new Date() : undefined,
  }),
}));
```

### Connection Indicator Component

```typescript
// components/common/ConnectionIndicator.tsx
import { View, Text, StyleSheet } from 'react-native';
import { useConnectionStore } from '@/store/connectionStore';

const STATUS_CONFIG = {
  connected: { color: '#22c55e', label: 'Connected' },
  connecting: { color: '#eab308', label: 'Reconnecting...' },
  disconnected: { color: '#ef4444', label: 'Offline' },
};

export function ConnectionIndicator() {
  const { status } = useConnectionStore();
  const config = STATUS_CONFIG[status];

  return (
    <View style={styles.container}>
      <View style={[styles.dot, { backgroundColor: config.color }]} />
      {status !== 'connected' && (
        <Text style={styles.label}>{config.label}</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  label: {
    marginLeft: 4,
    fontSize: 12,
    color: '#6b7280',
  },
});
```

### Pulse Animation Component

```typescript
// components/common/PulseAnimation.tsx
import { useEffect, useRef } from 'react';
import { Animated, ViewStyle } from 'react-native';

interface PulseAnimationProps {
  trigger: boolean;
  children: React.ReactNode;
  style?: ViewStyle;
}

export function PulseAnimation({ trigger, children, style }: PulseAnimationProps) {
  const opacity = useRef(new Animated.Value(1)).current;
  const scale = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    if (trigger) {
      Animated.sequence([
        Animated.parallel([
          Animated.timing(opacity, { toValue: 0.7, duration: 100, useNativeDriver: true }),
          Animated.timing(scale, { toValue: 1.05, duration: 100, useNativeDriver: true }),
        ]),
        Animated.parallel([
          Animated.timing(opacity, { toValue: 1, duration: 200, useNativeDriver: true }),
          Animated.timing(scale, { toValue: 1, duration: 200, useNativeDriver: true }),
        ]),
      ]).start();
    }
  }, [trigger]);

  return (
    <Animated.View style={[style, { opacity, transform: [{ scale }] }]}>
      {children}
    </Animated.View>
  );
}
```

---

## 6. Success Criteria

✅ Phase 13 is complete when:

- Polling updates running strategies every 5 seconds
- Polling pauses when app is in background
- Status changes trigger UI updates
- Visual feedback shows on changes
- Optimistic updates improve perceived performance
- Connection status is visible
- Network loss handled gracefully
