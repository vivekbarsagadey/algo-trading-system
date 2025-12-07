---
goal: Implement offline data viewing and sync when reconnected
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, offline, caching, sync, persistence]
---

# Phase 14: Offline Support

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement offline data viewing with cached strategies, offline indicators, disabled actions, and sync mechanism when network is restored.

---

## 1. Requirements & Constraints

- **REQ-003**: Offline capability for viewing saved strategies (execution requires connectivity)
- **CON-001**: Backend API required for all operations except viewing cached data
- **CON-003**: Real-time prices require active network connection

---

## 2. Implementation Tasks

### GOAL-014: Implement offline data viewing and sync when reconnected

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-159 | Configure React Query persistence: use @tanstack/react-query-persist-client with expo-file-system | | | Phase 4 |
| TASK-160 | Cache strategy list data for offline viewing: persist strategies query with 24-hour max age | | | TASK-159 |
| TASK-161 | Cache user profile data: persist profile query for offline access | | | TASK-159 |
| TASK-162 | Show "Offline" banner when network unavailable: use @react-native-community/netinfo to detect | | | Phase 1 |
| TASK-163 | Disable strategy start/stop when offline: gray out buttons, show tooltip "Requires internet" | | | TASK-162 |
| TASK-164 | Queue strategy creation/updates for sync when online: store mutations in AsyncStorage | | | TASK-162 |
| TASK-165 | Sync queued actions when network restored: process queue in order, handle conflicts | | | TASK-164 |
| TASK-166 | Show sync status indicator during sync: "Syncing..." with spinner, "Synced" on complete | | | TASK-165 |
| TASK-167 | Handle sync conflicts: if server data newer, prompt user to keep local or server version | | | TASK-165 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/providers/QueryProvider.tsx` | Modify | Add persistence configuration |
| `mobile/services/offlineStorage.ts` | Create | Offline data persistence utilities |
| `mobile/hooks/useNetworkStatus.ts` | Create | Network connectivity hook |
| `mobile/hooks/useOfflineSync.ts` | Create | Offline sync queue management |
| `mobile/components/common/OfflineBanner.tsx` | Create | Offline status banner |
| `mobile/components/common/SyncIndicator.tsx` | Create | Sync status indicator |
| `mobile/store/syncStore.ts` | Create | Sync queue state management |

---

## 4. Acceptance Criteria

- [ ] Strategy list visible when offline (cached data)
- [ ] User profile visible when offline
- [ ] "Offline" banner displayed when no network
- [ ] Start/Stop buttons disabled when offline
- [ ] Create strategy queued when offline
- [ ] Queued actions sync when online
- [ ] Sync status visible during sync
- [ ] Conflicts handled appropriately

---

## 5. Technical Notes

### React Query Persistence Setup

```typescript
// providers/QueryProvider.tsx
import { QueryClient } from '@tanstack/react-query';
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client';
import { createAsyncStoragePersister } from '@tanstack/query-async-storage-persister';
import AsyncStorage from '@react-native-async-storage/async-storage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      cacheTime: 1000 * 60 * 60 * 24, // 24 hours
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 2,
      retryDelay: 1000,
    },
  },
});

const asyncStoragePersister = createAsyncStoragePersister({
  storage: AsyncStorage,
  key: 'ALGO_TRADING_QUERY_CACHE',
});

export function QueryProvider({ children }: { children: React.ReactNode }) {
  return (
    <PersistQueryClientProvider
      client={queryClient}
      persistOptions={{ persister: asyncStoragePersister }}
      onSuccess={() => {
        // Resume mutations after hydration
        queryClient.resumePausedMutations().then(() => {
          queryClient.invalidateQueries();
        });
      }}
    >
      {children}
    </PersistQueryClientProvider>
  );
}
```

### Network Status Hook

```typescript
// hooks/useNetworkStatus.ts
import { useState, useEffect } from 'react';
import NetInfo, { NetInfoState } from '@react-native-community/netinfo';

export function useNetworkStatus() {
  const [isConnected, setIsConnected] = useState<boolean | null>(true);
  const [networkType, setNetworkType] = useState<string | null>(null);

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener((state: NetInfoState) => {
      setIsConnected(state.isConnected);
      setNetworkType(state.type);
    });

    // Initial check
    NetInfo.fetch().then((state) => {
      setIsConnected(state.isConnected);
      setNetworkType(state.type);
    });

    return () => unsubscribe();
  }, []);

  return { isConnected, networkType };
}
```

### Offline Banner Component

```typescript
// components/common/OfflineBanner.tsx
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useNetworkStatus } from '@/hooks/useNetworkStatus';

export function OfflineBanner() {
  const { isConnected } = useNetworkStatus();

  if (isConnected) return null;

  return (
    <View style={styles.banner}>
      <Ionicons name="cloud-offline" size={16} color="white" />
      <Text style={styles.text}>You're offline. Some features are unavailable.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f59e0b',
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  text: {
    color: 'white',
    fontSize: 14,
    marginLeft: 8,
  },
});
```

### Sync Queue Store

```typescript
// store/syncStore.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface QueuedAction {
  id: string;
  type: 'CREATE_STRATEGY' | 'UPDATE_STRATEGY' | 'DELETE_STRATEGY';
  payload: any;
  timestamp: number;
}

interface SyncState {
  queue: QueuedAction[];
  isSyncing: boolean;
  lastSyncAt: Date | null;
  addToQueue: (action: Omit<QueuedAction, 'id' | 'timestamp'>) => void;
  removeFromQueue: (id: string) => void;
  clearQueue: () => void;
  setSyncing: (isSyncing: boolean) => void;
  setLastSyncAt: (date: Date) => void;
}

export const useSyncStore = create<SyncState>()(
  persist(
    (set) => ({
      queue: [],
      isSyncing: false,
      lastSyncAt: null,
      addToQueue: (action) =>
        set((state) => ({
          queue: [
            ...state.queue,
            {
              ...action,
              id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
              timestamp: Date.now(),
            },
          ],
        })),
      removeFromQueue: (id) =>
        set((state) => ({
          queue: state.queue.filter((item) => item.id !== id),
        })),
      clearQueue: () => set({ queue: [] }),
      setSyncing: (isSyncing) => set({ isSyncing }),
      setLastSyncAt: (date) => set({ lastSyncAt: date }),
    }),
    {
      name: 'sync-queue',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
```

### Offline Sync Hook

```typescript
// hooks/useOfflineSync.ts
import { useEffect } from 'react';
import { useNetworkStatus } from './useNetworkStatus';
import { useSyncStore } from '@/store/syncStore';
import { createStrategy, updateStrategy, deleteStrategy } from '@/api/strategies';

export function useOfflineSync() {
  const { isConnected } = useNetworkStatus();
  const { queue, isSyncing, removeFromQueue, setSyncing, setLastSyncAt } = useSyncStore();

  useEffect(() => {
    if (!isConnected || isSyncing || queue.length === 0) return;

    const syncQueue = async () => {
      setSyncing(true);

      for (const action of queue) {
        try {
          switch (action.type) {
            case 'CREATE_STRATEGY':
              await createStrategy(action.payload);
              break;
            case 'UPDATE_STRATEGY':
              await updateStrategy(action.payload.id, action.payload.data);
              break;
            case 'DELETE_STRATEGY':
              await deleteStrategy(action.payload.id);
              break;
          }
          removeFromQueue(action.id);
        } catch (error) {
          console.error('Sync error:', error);
          // Keep in queue for retry
          break;
        }
      }

      setSyncing(false);
      setLastSyncAt(new Date());
    };

    syncQueue();
  }, [isConnected, queue.length]);

  return { isSyncing, queueLength: queue.length };
}
```

---

## 6. Success Criteria

✅ Phase 14 is complete when:

- Cached data visible when offline
- Offline banner displays appropriately
- Actions disabled when offline
- Mutations queued when offline
- Queue syncs when online
- Sync status visible to user
- Conflicts handled gracefully
