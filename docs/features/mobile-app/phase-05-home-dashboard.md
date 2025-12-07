---
goal: Create home dashboard with strategy overview and quick actions
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, dashboard, home, statistics, quick-actions]
---

# Phase 5: Home Dashboard

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Create the home dashboard screen with welcome header, quick statistics (active strategies, today's P&L), active strategies carousel, quick action buttons, and recent activity feed.

---

## 1. Requirements & Constraints

- **PER-001**: App launch to interactive < 2 seconds
- **PER-003**: API response display < 500ms
- **PER-004**: Background refresh for active strategies every 5 seconds
- **UXR-004**: Clear visual feedback for all actions
- **UXR-006**: Loading states for all network operations

---

## 2. Implementation Tasks

### GOAL-005: Create home dashboard with strategy overview and quick actions

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-052 | Create `app/(tabs)/index.tsx` as home dashboard with ScrollView, RefreshControl, skeleton loading | | | Phase 3 |
| TASK-053 | Create `components/home/WelcomeHeader.tsx`: display user name from authStore, greeting based on time of day (Good Morning/Afternoon/Evening) | | | TASK-052 |
| TASK-054 | Create `components/home/QuickStats.tsx`: 3 stat cards - Active Strategies count, Today's P&L (green/red based on +/-), Total Trades today | | | TASK-052, Phase 4 |
| TASK-055 | Create `components/home/ActiveStrategies.tsx`: horizontal FlatList of running strategies, each card shows symbol, status, current price/P&L | | | TASK-052, Phase 4 |
| TASK-056 | Create `components/home/QuickActions.tsx`: 2 large buttons - "Create Strategy" (navigates to create), "Connect Broker" (navigates to broker, only if not connected) | | | TASK-052 |
| TASK-057 | Create `components/home/RecentActivity.tsx`: list of last 5 order executions, each showing symbol, action (BUY/SELL/SL_HIT), time, amount | | | TASK-052, Phase 4 |
| TASK-058 | Implement pull-to-refresh: RefreshControl on ScrollView, refetch all dashboard queries on pull | | | TASK-052 |
| TASK-059 | Add skeleton loading states: use Skeleton component for stats, strategy cards, activity items while data loads | | | TASK-052 |
| TASK-060 | Create `components/home/StrategyStatusCard.tsx`: compact card with symbol, status badge (RUNNING/STOPPED), buy/sell times | | | TASK-055 |
| TASK-061 | Implement real-time status polling: useEffect with 5-second interval, poll active strategies status, update UI on change | | | TASK-055, Phase 4 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/app/(tabs)/index.tsx` | Create | Home dashboard screen |
| `mobile/components/home/WelcomeHeader.tsx` | Create | Welcome greeting with user name |
| `mobile/components/home/QuickStats.tsx` | Create | Statistics cards (active, P&L, trades) |
| `mobile/components/home/ActiveStrategies.tsx` | Create | Horizontal carousel of active strategies |
| `mobile/components/home/StrategyStatusCard.tsx` | Create | Compact strategy card for carousel |
| `mobile/components/home/QuickActions.tsx` | Create | Create Strategy / Connect Broker buttons |
| `mobile/components/home/RecentActivity.tsx` | Create | Recent order executions list |
| `mobile/components/home/ActivityItem.tsx` | Create | Single activity item component |
| `mobile/hooks/useDashboardData.ts` | Create | Combined hook for all dashboard data |
| `mobile/hooks/useActiveStrategiesPolling.ts` | Create | Polling hook for active strategies |

---

## 4. Acceptance Criteria

- [ ] Dashboard displays welcome message with user name
- [ ] Greeting changes based on time of day
- [ ] Quick stats show accurate counts (active strategies, P&L, trades)
- [ ] P&L displays in green for profit, red for loss
- [ ] Active strategies carousel scrolls horizontally
- [ ] Each strategy card shows symbol and status
- [ ] Quick actions navigate to correct screens
- [ ] "Connect Broker" only shows if broker not connected
- [ ] Recent activity shows last 5 orders
- [ ] Pull-to-refresh reloads all data
- [ ] Skeleton loading shown while data loads
- [ ] Status polling updates every 5 seconds

---

## 5. Technical Notes

### Home Dashboard Structure

```typescript
// app/(tabs)/index.tsx
import { ScrollView, RefreshControl, View } from 'react-native';
import { WelcomeHeader } from '@/components/home/WelcomeHeader';
import { QuickStats } from '@/components/home/QuickStats';
import { ActiveStrategies } from '@/components/home/ActiveStrategies';
import { QuickActions } from '@/components/home/QuickActions';
import { RecentActivity } from '@/components/home/RecentActivity';
import { useDashboardData } from '@/hooks/useDashboardData';

export default function HomeScreen() {
  const { data, isLoading, refetch, isRefetching } = useDashboardData();

  return (
    <ScrollView
      style={{ flex: 1, backgroundColor: '#f5f5f5' }}
      refreshControl={
        <RefreshControl refreshing={isRefetching} onRefresh={refetch} />
      }
    >
      <WelcomeHeader />
      <QuickStats data={data?.stats} isLoading={isLoading} />
      <ActiveStrategies strategies={data?.activeStrategies} isLoading={isLoading} />
      <QuickActions hasBroker={data?.hasBroker} />
      <RecentActivity activities={data?.recentActivity} isLoading={isLoading} />
    </ScrollView>
  );
}
```

### Quick Stats Component

```typescript
// components/home/QuickStats.tsx
import { View, Text, StyleSheet } from 'react-native';

interface QuickStatsProps {
  data?: {
    activeStrategies: number;
    todayPnL: number;
    totalTrades: number;
  };
  isLoading: boolean;
}

export function QuickStats({ data, isLoading }: QuickStatsProps) {
  if (isLoading) {
    return <QuickStatsSkeleton />;
  }

  return (
    <View style={styles.container}>
      <StatCard
        title="Active"
        value={data?.activeStrategies ?? 0}
        icon="play-circle"
      />
      <StatCard
        title="Today's P&L"
        value={`₹${data?.todayPnL?.toLocaleString() ?? 0}`}
        valueColor={data?.todayPnL >= 0 ? '#22c55e' : '#ef4444'}
        icon="trending-up"
      />
      <StatCard
        title="Trades"
        value={data?.totalTrades ?? 0}
        icon="activity"
      />
    </View>
  );
}
```

### Active Strategies Polling

```typescript
// hooks/useActiveStrategiesPolling.ts
import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { getActiveStrategies } from '@/api/strategies';

export function useActiveStrategiesPolling(enabled: boolean = true) {
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!enabled) return;

    const interval = setInterval(async () => {
      try {
        const data = await getActiveStrategies();
        queryClient.setQueryData(['strategies', 'active'], data);
      } catch (error) {
        console.error('Polling error:', error);
      }
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, [enabled, queryClient]);
}
```

### Welcome Header with Time-Based Greeting

```typescript
// components/home/WelcomeHeader.tsx
import { View, Text } from 'react-native';
import { useAuthStore } from '@/store/authStore';

function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good Morning';
  if (hour < 17) return 'Good Afternoon';
  return 'Good Evening';
}

export function WelcomeHeader() {
  const { user } = useAuthStore();

  return (
    <View style={styles.container}>
      <Text style={styles.greeting}>{getGreeting()},</Text>
      <Text style={styles.userName}>{user?.name ?? 'Trader'}</Text>
    </View>
  );
}
```

---

## 6. Success Criteria

✅ Phase 5 is complete when:

- Home dashboard displays all sections correctly
- Welcome header shows personalized greeting
- Quick stats show accurate data with proper formatting
- Active strategies carousel is horizontally scrollable
- Quick actions navigate to correct screens
- Recent activity shows order history
- Pull-to-refresh works correctly
- Skeleton loading displays while data loads
- Real-time polling updates active strategies
