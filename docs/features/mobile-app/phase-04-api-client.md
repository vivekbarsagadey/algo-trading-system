---
goal: Create API client with authentication and React Query integration
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, api, axios, react-query, data-fetching]
---

# Phase 4: API Client & Data Fetching

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Create a robust API client using Axios with authentication interceptors, error handling, and React Query integration for efficient data fetching, caching, and offline support.

---

## 1. Requirements & Constraints

- **REQ-003**: Offline capability for viewing saved strategies
- **SEC-004**: Certificate pinning for API calls (production)
- **PAT-004**: React Query (TanStack Query) for data fetching and caching
- **PAT-005**: Axios for HTTP client with interceptors
- **PER-003**: API response display < 500ms

---

## 2. Implementation Tasks

### GOAL-004: Create API client with authentication and React Query integration

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-040 | Create `api/client.ts` with Axios instance: baseURL from `Constants.expoConfig.extra.apiUrl`, timeout 30s, JSON headers | | | Phase 1 |
| TASK-041 | Implement request interceptor: get JWT from SecureStore, add `Authorization: Bearer <token>` header to all requests | | | TASK-040, Phase 2 |
| TASK-042 | Implement response interceptor: on 401, attempt token refresh, retry original request; on failure, logout and redirect | | | TASK-041 |
| TASK-043 | Create `api/strategies.ts`: `getStrategies()`, `getStrategy(id)`, `createStrategy(data)`, `updateStrategy(id, data)`, `deleteStrategy(id)`, `startStrategy(id)`, `stopStrategy(id)` | | | TASK-040 |
| TASK-044 | Create `api/broker.ts`: `connectBroker(type, credentials)`, `validateBroker()`, `getBrokerStatus()`, `disconnectBroker()`, `refreshBrokerToken()` | | | TASK-040 |
| TASK-045 | Create `api/user.ts`: `getProfile()`, `updateProfile(data)`, `changePassword(currentPassword, newPassword)` | | | TASK-040 |
| TASK-046 | Configure React Query in `providers/QueryProvider.tsx`: default staleTime 5min, cacheTime 30min, retry 3 times with exponential backoff | | | Phase 1 |
| TASK-047 | Create `hooks/useStrategies.ts`: `useStrategies()` using useQuery with query key `['strategies']`, returns list with loading/error states | | | TASK-043, TASK-046 |
| TASK-048 | Create `hooks/useCreateStrategy.ts`: `useCreateStrategy()` using useMutation, invalidates `['strategies']` on success, handles optimistic update | | | TASK-043, TASK-046 |
| TASK-049 | Implement offline support: configure React Query persistence with `expo-file-system`, cache strategies locally | | | TASK-046 |
| TASK-050 | Create `utils/apiErrors.ts`: `parseApiError(error)` returns user-friendly message, handle network errors, validation errors, server errors | | | TASK-040 |
| TASK-051 | Create API response types in `types/api.ts`: `ApiResponse<T>`, `PaginatedResponse<T>`, `ApiError`, `ValidationError` | | | Phase 1 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/api/client.ts` | Create | Axios instance with interceptors |
| `mobile/api/strategies.ts` | Create | Strategy API functions |
| `mobile/api/broker.ts` | Create | Broker API functions |
| `mobile/api/user.ts` | Create | User/profile API functions |
| `mobile/providers/QueryProvider.tsx` | Create | React Query configuration |
| `mobile/hooks/useStrategies.ts` | Create | Strategy list query hook |
| `mobile/hooks/useStrategy.ts` | Create | Single strategy query hook |
| `mobile/hooks/useCreateStrategy.ts` | Create | Create strategy mutation hook |
| `mobile/hooks/useUpdateStrategy.ts` | Create | Update strategy mutation hook |
| `mobile/hooks/useDeleteStrategy.ts` | Create | Delete strategy mutation hook |
| `mobile/hooks/useBroker.ts` | Create | Broker status query hook |
| `mobile/utils/apiErrors.ts` | Create | Error parsing utilities |
| `mobile/types/api.ts` | Create | API TypeScript types |
| `mobile/types/strategy.ts` | Create | Strategy TypeScript types |
| `mobile/types/broker.ts` | Create | Broker TypeScript types |

---

## 4. Acceptance Criteria

- [ ] Axios client configured with base URL from environment
- [ ] JWT token automatically added to all API requests
- [ ] 401 responses trigger token refresh attempt
- [ ] Failed token refresh triggers logout
- [ ] All strategy CRUD operations work correctly
- [ ] React Query caches data appropriately
- [ ] Queries show loading and error states
- [ ] Mutations invalidate related queries on success
- [ ] Offline data persists and loads on app restart
- [ ] Error messages are user-friendly

---

## 5. Technical Notes

### Axios Client Setup

```typescript
// api/client.ts
import axios from 'axios';
import Constants from 'expo-constants';
import { getToken, removeToken } from '@/utils/secureStorage';
import { useAuthStore } from '@/store/authStore';

const API_BASE_URL = Constants.expoConfig?.extra?.apiUrl || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  async (config) => {
    const token = await getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Attempt token refresh
        const newToken = await refreshToken();
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout
        await removeToken();
        useAuthStore.getState().logout();
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);
```

### Strategy API Functions

```typescript
// api/strategies.ts
import { apiClient } from './client';
import { Strategy, CreateStrategyData, UpdateStrategyData } from '@/types/strategy';

export const getStrategies = async (): Promise<Strategy[]> => {
  const response = await apiClient.get('/api/v1/strategies');
  return response.data;
};

export const getStrategy = async (id: string): Promise<Strategy> => {
  const response = await apiClient.get(`/api/v1/strategies/${id}`);
  return response.data;
};

export const createStrategy = async (data: CreateStrategyData): Promise<Strategy> => {
  const response = await apiClient.post('/api/v1/strategies', data);
  return response.data;
};

export const startStrategy = async (id: string): Promise<Strategy> => {
  const response = await apiClient.post(`/api/v1/strategies/${id}/start`);
  return response.data;
};

export const stopStrategy = async (id: string): Promise<Strategy> => {
  const response = await apiClient.post(`/api/v1/strategies/${id}/stop`);
  return response.data;
};
```

### React Query Hooks

```typescript
// hooks/useStrategies.ts
import { useQuery } from '@tanstack/react-query';
import { getStrategies } from '@/api/strategies';

export const useStrategies = () => {
  return useQuery({
    queryKey: ['strategies'],
    queryFn: getStrategies,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// hooks/useCreateStrategy.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createStrategy } from '@/api/strategies';

export const useCreateStrategy = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createStrategy,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] });
    },
  });
};
```

### API Error Handling

```typescript
// utils/apiErrors.ts
import { AxiosError } from 'axios';

export interface ParsedError {
  message: string;
  code?: string;
  fields?: Record<string, string[]>;
}

export const parseApiError = (error: unknown): ParsedError => {
  if (error instanceof AxiosError) {
    if (!error.response) {
      return { message: 'Network error. Please check your connection.' };
    }
    
    const { status, data } = error.response;
    
    if (status === 422 && data.detail) {
      // Validation error
      return {
        message: 'Validation failed',
        fields: parseValidationErrors(data.detail),
      };
    }
    
    return {
      message: data.detail || 'An unexpected error occurred',
      code: String(status),
    };
  }
  
  return { message: 'An unexpected error occurred' };
};
```

---

## 6. Success Criteria

✅ Phase 4 is complete when:

- Axios client is configured with authentication interceptors
- All strategy API functions are implemented
- All broker API functions are implemented
- React Query is configured with proper caching
- Query hooks return loading, error, and data states
- Mutation hooks invalidate queries on success
- Offline persistence is configured
- Error messages are parsed to user-friendly format
