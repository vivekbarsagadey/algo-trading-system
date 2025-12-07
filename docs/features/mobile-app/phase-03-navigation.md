---
goal: Implement file-based navigation with Expo Router and tab navigation
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, navigation, expo-router, tabs, deep-linking]
---

# Phase 3: Navigation Structure

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement the complete navigation structure using Expo Router with file-based routing, bottom tab navigation, stack navigation for detail screens, authentication guards, and deep linking configuration.

---

## 1. Requirements & Constraints

- **REQ-006**: Deep linking for notification navigation
- **PAT-001**: Expo Router for file-based navigation
- **CON-001**: Backend API required for all operations except viewing cached data

---

## 2. Implementation Tasks

### GOAL-003: Implement file-based navigation with Expo Router and tab navigation

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-030 | Create `app/_layout.tsx` root layout with QueryClientProvider, Zustand providers, SafeAreaProvider, theme provider | | | Phase 1 |
| TASK-031 | Create `app/(auth)/_layout.tsx` for authentication screens stack with header hidden, keyboard avoiding view | | | Phase 2 |
| TASK-032 | Create `app/(tabs)/_layout.tsx` with bottom tab navigation using Tabs component from Expo Router | | | TASK-030 |
| TASK-033 | Configure 4 tabs: Home (index), Strategies, Broker, Profile with proper titles and icons | | | TASK-032 |
| TASK-034 | Add tab icons using `@expo/vector-icons` (Ionicons): home, list, link, person icons | | | TASK-033 |
| TASK-035 | Implement auth guard in root layout: check `isAuthenticated` from authStore, redirect to `/login` if false, redirect to `/(tabs)` if true | | | TASK-030, Phase 2 |
| TASK-036 | Create stack navigation for strategy details: `app/(tabs)/strategies/[id].tsx` with dynamic route parameter | | | TASK-032 |
| TASK-037 | Add header configuration: back button for nested screens, dynamic title from strategy data, consistent styling | | | TASK-036 |
| TASK-038 | Implement deep linking in `app.json`: scheme `algotrading`, pathConfigMap for `/strategy/:id`, `/notifications` | | | TASK-036 |
| TASK-039 | Create navigation type definitions in `types/navigation.ts`: RootStackParamList, TabParamList, StrategyStackParamList | | | TASK-030 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/app/_layout.tsx` | Create | Root layout with providers and auth guard |
| `mobile/app/(auth)/_layout.tsx` | Create | Auth screens stack navigator |
| `mobile/app/(tabs)/_layout.tsx` | Create | Tab navigator with 4 tabs |
| `mobile/app/(tabs)/index.tsx` | Create | Home tab screen placeholder |
| `mobile/app/(tabs)/strategies/_layout.tsx` | Create | Strategies stack navigator |
| `mobile/app/(tabs)/strategies/index.tsx` | Create | Strategies list screen placeholder |
| `mobile/app/(tabs)/strategies/[id].tsx` | Create | Strategy detail screen with dynamic route |
| `mobile/app/(tabs)/broker/_layout.tsx` | Create | Broker stack navigator |
| `mobile/app/(tabs)/broker/index.tsx` | Create | Broker status screen placeholder |
| `mobile/app/(tabs)/profile/_layout.tsx` | Create | Profile stack navigator |
| `mobile/app/(tabs)/profile/index.tsx` | Create | Profile screen placeholder |
| `mobile/app.json` | Modify | Add deep linking scheme configuration |
| `mobile/types/navigation.ts` | Create | Navigation TypeScript types |
| `mobile/providers/QueryProvider.tsx` | Create | React Query provider wrapper |

---

## 4. Acceptance Criteria

- [ ] Root layout renders with all providers
- [ ] Unauthenticated users are redirected to login
- [ ] Authenticated users see tab navigation
- [ ] 4 tabs display with correct icons and labels
- [ ] Tab switching works smoothly
- [ ] Strategy detail screen receives `id` parameter
- [ ] Back navigation works correctly from detail screens
- [ ] Deep links open correct screens (e.g., `algotrading://strategy/123`)
- [ ] Navigation types provide proper TypeScript autocomplete

---

## 5. Technical Notes

### Root Layout Structure

```typescript
// app/_layout.tsx
import { Stack } from 'expo-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { useAuthStore } from '@/store/authStore';
import { useEffect } from 'react';
import { useRouter, useSegments } from 'expo-router';

const queryClient = new QueryClient();

export default function RootLayout() {
  const { isAuthenticated } = useAuthStore();
  const segments = useSegments();
  const router = useRouter();

  useEffect(() => {
    const inAuthGroup = segments[0] === '(auth)';
    
    if (!isAuthenticated && !inAuthGroup) {
      router.replace('/login');
    } else if (isAuthenticated && inAuthGroup) {
      router.replace('/(tabs)');
    }
  }, [isAuthenticated, segments]);

  return (
    <QueryClientProvider client={queryClient}>
      <SafeAreaProvider>
        <Stack screenOptions={{ headerShown: false }} />
      </SafeAreaProvider>
    </QueryClientProvider>
  );
}
```

### Tab Layout Structure

```typescript
// app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#2563eb',
        tabBarInactiveTintColor: '#6b7280',
        headerShown: true,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="home" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="strategies"
        options={{
          title: 'Strategies',
          headerShown: false,
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="list" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="broker"
        options={{
          title: 'Broker',
          headerShown: false,
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="link" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          headerShown: false,
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="person" size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}
```

### Deep Linking Configuration

```json
// app.json (partial)
{
  "expo": {
    "scheme": "algotrading",
    "experiments": {
      "typedRoutes": true
    }
  }
}
```

### Navigation Types

```typescript
// types/navigation.ts
export type RootStackParamList = {
  '(auth)': undefined;
  '(tabs)': undefined;
};

export type TabParamList = {
  index: undefined;
  strategies: undefined;
  broker: undefined;
  profile: undefined;
};

export type StrategyStackParamList = {
  index: undefined;
  '[id]': { id: string };
  create: undefined;
  '[id]/edit': { id: string };
};
```

---

## 6. Success Criteria

✅ Phase 3 is complete when:

- Root layout initializes all providers correctly
- Auth guard redirects unauthenticated users to login
- Tab navigation displays 4 tabs with icons
- Stack navigation works for nested screens
- Dynamic routes receive parameters correctly
- Deep linking configuration is set up
- Navigation types provide TypeScript safety
