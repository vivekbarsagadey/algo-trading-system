---
goal: Create strategy list with filtering and status display
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, strategies, list, filtering, flatlist]
---

# Phase 6: Strategy List Screen

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Create the strategy list screen with FlatList for performance, status filtering, search functionality, swipe actions, and pull-to-refresh.

---

## 1. Requirements & Constraints

- **UXR-003**: Single-tap start/stop for strategies
- **UXR-004**: Clear visual feedback for all actions
- **PER-002**: Screen transitions < 300ms

---

## 2. Implementation Tasks

### GOAL-006: Create strategy list with filtering and status display

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-062 | Create `app/(tabs)/strategies/index.tsx` strategy list screen with FlatList, SafeAreaView, search bar | | | Phase 3, Phase 4 |
| TASK-063 | Create `components/strategies/StrategyList.tsx` using FlatList with `keyExtractor`, `renderItem`, optimized with `getItemLayout` | | | TASK-062 |
| TASK-064 | Create `components/strategies/StrategyCard.tsx` displaying symbol, status badge, buy_time, sell_time, quantity | | | TASK-063 |
| TASK-065 | Implement status filter chips: All, Running, Stopped, Completed - horizontal ScrollView with chip buttons | | | TASK-062 |
| TASK-066 | Add search functionality: TextInput with debounced search, filter strategies by symbol name | | | TASK-062 |
| TASK-067 | Create floating action button (FAB) for creating new strategy, position absolute bottom-right, navigates to `/strategies/create` | | | TASK-062 |
| TASK-068 | Implement swipe actions using `react-native-gesture-handler`: swipe right reveals Start/Stop, swipe left reveals Delete | | | TASK-063 |
| TASK-069 | Add pull-to-refresh: RefreshControl on FlatList, calls `refetch()` from useStrategies hook | | | TASK-063 |
| TASK-070 | Create `components/common/EmptyState.tsx` for when no strategies exist - show illustration, "Create your first strategy" CTA | | | TASK-062 |
| TASK-071 | Implement list pagination with infinite scroll using `onEndReached`, `onEndReachedThreshold={0.5}` | | | TASK-063 |
| TASK-072 | Create status badges component with color coding: RUNNING (green), STOPPED (gray), COMPLETED (blue), ERROR (red) | | | TASK-064 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/app/(tabs)/strategies/index.tsx` | Create | Strategy list screen |
| `mobile/app/(tabs)/strategies/_layout.tsx` | Create | Strategies stack navigator |
| `mobile/components/strategies/StrategyList.tsx` | Create | FlatList wrapper with optimization |
| `mobile/components/strategies/StrategyCard.tsx` | Create | Individual strategy card |
| `mobile/components/strategies/StatusFilter.tsx` | Create | Filter chips component |
| `mobile/components/strategies/StatusBadge.tsx` | Create | Status badge with colors |
| `mobile/components/strategies/SwipeableRow.tsx` | Create | Swipeable list item wrapper |
| `mobile/components/common/EmptyState.tsx` | Create | Empty state component |
| `mobile/components/common/FAB.tsx` | Create | Floating action button |
| `mobile/components/common/SearchBar.tsx` | Create | Search input with debounce |

---

## 4. Acceptance Criteria

- [ ] Strategy list displays all user strategies
- [ ] FlatList performs smoothly with 100+ items
- [ ] Status filter chips filter list correctly
- [ ] Search filters by symbol name
- [ ] FAB navigates to strategy creation
- [ ] Swipe right shows Start/Stop action
- [ ] Swipe left shows Delete action
- [ ] Pull-to-refresh reloads data
- [ ] Empty state shows when no strategies
- [ ] Infinite scroll loads more strategies
- [ ] Status badges show correct colors

---

## 5. Technical Notes

### Strategy List with FlatList

```typescript
// components/strategies/StrategyList.tsx
import { FlatList, RefreshControl } from 'react-native';
import { StrategyCard } from './StrategyCard';
import { Strategy } from '@/types/strategy';

interface StrategyListProps {
  strategies: Strategy[];
  onRefresh: () => void;
  isRefreshing: boolean;
  onLoadMore: () => void;
  onStrategyPress: (id: string) => void;
}

export function StrategyList({
  strategies,
  onRefresh,
  isRefreshing,
  onLoadMore,
  onStrategyPress,
}: StrategyListProps) {
  return (
    <FlatList
      data={strategies}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => (
        <StrategyCard
          strategy={item}
          onPress={() => onStrategyPress(item.id)}
        />
      )}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={onRefresh} />
      }
      onEndReached={onLoadMore}
      onEndReachedThreshold={0.5}
      ListEmptyComponent={<EmptyState />}
    />
  );
}
```

### Status Filter Chips

```typescript
// components/strategies/StatusFilter.tsx
const FILTERS = [
  { key: 'all', label: 'All' },
  { key: 'running', label: 'Running' },
  { key: 'stopped', label: 'Stopped' },
  { key: 'completed', label: 'Completed' },
];

export function StatusFilter({ selected, onSelect }) {
  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false}>
      {FILTERS.map((filter) => (
        <Chip
          key={filter.key}
          label={filter.label}
          selected={selected === filter.key}
          onPress={() => onSelect(filter.key)}
        />
      ))}
    </ScrollView>
  );
}
```

---

## 6. Success Criteria

✅ Phase 6 is complete when:

- Strategy list displays with optimized FlatList
- Filtering by status works correctly
- Search functionality filters by symbol
- Swipe actions work for start/stop/delete
- Pull-to-refresh reloads data
- Infinite scroll pagination works
- Empty state displays appropriately
