---
goal: Implement Zustand stores for application state
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, state-management, zustand, stores, persistence]
---

# Phase 17: State Management

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement comprehensive Zustand stores for authentication, strategies, broker connection, and user settings with persistence and devtools support.

---

## 1. Requirements & Constraints

- **PAT-002**: Zustand for state management
- **SEC-001**: JWT tokens stored in SecureStore
- **REQ-003**: Offline capability for viewing saved strategies

---

## 2. Implementation Tasks

### GOAL-017: Implement Zustand stores for application state

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-190 | Create `store/authStore.ts` with: user, token, isAuthenticated, isLoading, login(), logout(), setUser(), checkAuth() | | | Phase 2 |
| TASK-191 | Create `store/strategyStore.ts` with: strategies, activeStrategy, filters, setStrategies(), setActiveStrategy(), updateStrategy(), setFilters() | | | Phase 4 |
| TASK-192 | Create `store/brokerStore.ts` with: broker, isConnected, connectionStatus, setBroker(), disconnect(), updateStatus() | | | Phase 10 |
| TASK-193 | Create `store/settingsStore.ts` with: biometricEnabled, notifications, darkMode, and setters for each | | | Phase 11 |
| TASK-194 | Implement persist middleware for settingsStore: persist to AsyncStorage | | | TASK-193 |
| TASK-195 | Create selectors for computed state: activeStrategiesCount, runningStrategies, hasBroker | | | TASK-191 |
| TASK-196 | Add devtools integration for debugging in development mode | | | TASK-190 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/store/authStore.ts` | Create | Authentication state |
| `mobile/store/strategyStore.ts` | Create | Strategy state |
| `mobile/store/brokerStore.ts` | Create | Broker connection state |
| `mobile/store/settingsStore.ts` | Create | User preferences |
| `mobile/store/selectors.ts` | Create | Computed selectors |
| `mobile/store/index.ts` | Create | Barrel export |

---

## 4. Acceptance Criteria

- [ ] Auth store manages authentication state
- [ ] Strategy store manages strategy data
- [ ] Broker store manages connection state
- [ ] Settings store persists preferences
- [ ] Selectors compute derived state
- [ ] Devtools work in development
- [ ] Persistence works across app restarts

---

## 5. Technical Notes

### Auth Store

```typescript
// store/authStore.ts
import { create } from 'zustand';
import { getToken, setToken, removeToken } from '@/utils/secureStorage';
import { login as apiLogin, logout as apiLogout } from '@/api/auth';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: User) => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (email, password) => {
    set({ isLoading: true });
    try {
      const { user, access_token, refresh_token } = await apiLogin(email, password);
      await setToken(access_token);
      await setRefreshToken(refresh_token);
      set({ user, token: access_token, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: async () => {
    try {
      await apiLogout();
    } finally {
      await removeToken();
      await removeRefreshToken();
      set({ user: null, token: null, isAuthenticated: false });
    }
  },

  setUser: (user) => set({ user }),

  checkAuth: async () => {
    set({ isLoading: true });
    const token = await getToken();
    if (token) {
      try {
        // Validate token with backend
        const user = await getCurrentUser();
        set({ user, token, isAuthenticated: true, isLoading: false });
      } catch {
        await removeToken();
        set({ isAuthenticated: false, isLoading: false });
      }
    } else {
      set({ isAuthenticated: false, isLoading: false });
    }
  },
}));
```

### Strategy Store

```typescript
// store/strategyStore.ts
import { create } from 'zustand';
import { Strategy, StrategyStatus } from '@/types/strategy';

interface StrategyFilters {
  status: StrategyStatus | 'all';
  search: string;
}

interface StrategyState {
  strategies: Strategy[];
  activeStrategy: Strategy | null;
  filters: StrategyFilters;
  setStrategies: (strategies: Strategy[]) => void;
  addStrategy: (strategy: Strategy) => void;
  updateStrategy: (id: string, updates: Partial<Strategy>) => void;
  removeStrategy: (id: string) => void;
  setActiveStrategy: (strategy: Strategy | null) => void;
  setFilters: (filters: Partial<StrategyFilters>) => void;
}

export const useStrategyStore = create<StrategyState>((set) => ({
  strategies: [],
  activeStrategy: null,
  filters: {
    status: 'all',
    search: '',
  },

  setStrategies: (strategies) => set({ strategies }),

  addStrategy: (strategy) =>
    set((state) => ({ strategies: [...state.strategies, strategy] })),

  updateStrategy: (id, updates) =>
    set((state) => ({
      strategies: state.strategies.map((s) =>
        s.id === id ? { ...s, ...updates } : s
      ),
      activeStrategy:
        state.activeStrategy?.id === id
          ? { ...state.activeStrategy, ...updates }
          : state.activeStrategy,
    })),

  removeStrategy: (id) =>
    set((state) => ({
      strategies: state.strategies.filter((s) => s.id !== id),
    })),

  setActiveStrategy: (strategy) => set({ activeStrategy: strategy }),

  setFilters: (filters) =>
    set((state) => ({ filters: { ...state.filters, ...filters } })),
}));
```

### Selectors

```typescript
// store/selectors.ts
import { useStrategyStore } from './strategyStore';
import { useBrokerStore } from './brokerStore';

// Strategy selectors
export const useFilteredStrategies = () => {
  const { strategies, filters } = useStrategyStore();
  
  return strategies.filter((strategy) => {
    // Filter by status
    if (filters.status !== 'all' && strategy.status !== filters.status) {
      return false;
    }
    
    // Filter by search
    if (filters.search && !strategy.symbol.toLowerCase().includes(filters.search.toLowerCase())) {
      return false;
    }
    
    return true;
  });
};

export const useActiveStrategiesCount = () => {
  const strategies = useStrategyStore((state) => state.strategies);
  return strategies.filter((s) => s.status === 'RUNNING').length;
};

export const useRunningStrategies = () => {
  const strategies = useStrategyStore((state) => state.strategies);
  return strategies.filter((s) => s.status === 'RUNNING');
};

// Broker selectors
export const useHasBroker = () => {
  return useBrokerStore((state) => state.isConnected);
};

export const useBrokerStatus = () => {
  const { broker, isConnected, connectionStatus } = useBrokerStore();
  return { broker, isConnected, connectionStatus };
};
```

### Devtools Integration

```typescript
// store/index.ts
import { useAuthStore } from './authStore';
import { useStrategyStore } from './strategyStore';
import { useBrokerStore } from './brokerStore';
import { useSettingsStore } from './settingsStore';

// Export all stores
export { useAuthStore, useStrategyStore, useBrokerStore, useSettingsStore };

// Export selectors
export * from './selectors';

// Debug helper for development
if (__DEV__) {
  // Enable store inspection in React DevTools
  console.log('Zustand stores initialized in development mode');
}
```

---

## 6. Success Criteria

✅ Phase 17 is complete when:

- All stores are implemented correctly
- Auth store manages login/logout
- Strategy store handles CRUD operations
- Broker store tracks connection state
- Settings persist across app restarts
- Selectors provide computed values
- Devtools work in development
