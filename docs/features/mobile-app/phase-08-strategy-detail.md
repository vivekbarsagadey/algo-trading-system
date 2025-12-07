---
goal: Create strategy detail view with start/stop controls and execution log
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, strategy, detail, controls, execution-log]
---

# Phase 8: Strategy Detail & Control

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Create the strategy detail screen with comprehensive information display, prominent start/stop controls, position status, execution log, and real-time status updates.

---

## 1. Requirements & Constraints

- **UXR-003**: Single-tap start/stop for strategies
- **UXR-004**: Clear visual feedback for all actions
- **PER-004**: Background refresh for active strategies every 5 seconds

---

## 2. Implementation Tasks

### GOAL-008: Create strategy detail view with start/stop controls and execution log

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-088 | Create `app/(tabs)/strategies/[id].tsx` strategy detail screen with ScrollView, loading state | | | Phase 3, Phase 4 |
| TASK-089 | Create `components/strategies/StrategyHeader.tsx`: large symbol text, status badge, created date | | | TASK-088 |
| TASK-090 | Display all strategy parameters in card layout: symbol, buy_time, sell_time, stop_loss, quantity with labels | | | TASK-088 |
| TASK-091 | Create `components/strategies/StrategyControls.tsx` with single prominent Start/Stop button | | | TASK-088 |
| TASK-092 | Implement Start button: large green button with play icon, text "Start Strategy", only when STOPPED | | | TASK-091 |
| TASK-093 | Implement Stop button: large red button with stop icon, text "Stop Strategy", only when RUNNING | | | TASK-091 |
| TASK-094 | Add confirmation dialog before stopping: "Are you sure you want to stop this strategy? Any open position will remain." | | | TASK-093 |
| TASK-095 | Create `components/strategies/PositionStatus.tsx`: show current position NONE/BOUGHT/SOLD/SL_HIT with icon and color | | | TASK-088 |
| TASK-096 | Create `components/strategies/LastAction.tsx`: display last executed action with timestamp, e.g., "BUY executed at 09:30 AM" | | | TASK-088 |
| TASK-097 | Create `components/strategies/ExecutionLog.tsx`: FlatList of order history with action, price, time, status | | | TASK-088 |
| TASK-098 | Implement real-time status polling: useEffect with setInterval 5s when status is RUNNING | | | TASK-088 |
| TASK-099 | Add edit button in header: navigates to `strategies/[id]/edit` | | | TASK-088 |
| TASK-100 | Add delete button with confirmation dialog: "Delete this strategy? This action cannot be undone." | | | TASK-088 |
| TASK-101 | Create P&L display component: show profit/loss if position entered and exited, green for profit, red for loss | | | TASK-088 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/app/(tabs)/strategies/[id].tsx` | Create | Strategy detail screen |
| `mobile/components/strategies/StrategyHeader.tsx` | Create | Header with symbol and status |
| `mobile/components/strategies/StrategyDetails.tsx` | Create | Parameters display card |
| `mobile/components/strategies/StrategyControls.tsx` | Create | Start/Stop button |
| `mobile/components/strategies/PositionStatus.tsx` | Create | Position indicator |
| `mobile/components/strategies/LastAction.tsx` | Create | Last action display |
| `mobile/components/strategies/ExecutionLog.tsx` | Create | Order history list |
| `mobile/components/strategies/PnLDisplay.tsx` | Create | Profit/Loss display |
| `mobile/components/common/ConfirmDialog.tsx` | Create | Confirmation modal |
| `mobile/hooks/useStrategyDetail.ts` | Create | Strategy detail query hook |

---

## 4. Acceptance Criteria

- [ ] Strategy detail loads with all parameters
- [ ] Header shows symbol and status badge
- [ ] All 5 parameters displayed clearly
- [ ] Start button shows when strategy is stopped
- [ ] Stop button shows when strategy is running
- [ ] Confirmation required before stopping
- [ ] Position status shows current state
- [ ] Last action displays with timestamp
- [ ] Execution log shows order history
- [ ] Real-time polling updates every 5 seconds
- [ ] Edit navigates to edit screen
- [ ] Delete removes strategy after confirmation
- [ ] P&L displays when applicable

---

## 5. Technical Notes

### Strategy Detail Screen

```typescript
// app/(tabs)/strategies/[id].tsx
import { useLocalSearchParams } from 'expo-router';
import { useStrategyDetail } from '@/hooks/useStrategyDetail';

export default function StrategyDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { data: strategy, isLoading, refetch } = useStrategyDetail(id);

  // Real-time polling when running
  useEffect(() => {
    if (strategy?.status !== 'RUNNING') return;
    
    const interval = setInterval(() => {
      refetch();
    }, 5000);
    
    return () => clearInterval(interval);
  }, [strategy?.status, refetch]);

  if (isLoading) return <LoadingScreen />;
  if (!strategy) return <NotFoundScreen />;

  return (
    <ScrollView>
      <StrategyHeader strategy={strategy} />
      <StrategyDetails strategy={strategy} />
      <StrategyControls 
        strategy={strategy} 
        onStart={handleStart}
        onStop={handleStop}
      />
      <PositionStatus position={strategy.position} />
      <LastAction action={strategy.last_action} />
      <ExecutionLog strategyId={id} />
      {strategy.pnl && <PnLDisplay pnl={strategy.pnl} />}
    </ScrollView>
  );
}
```

### Strategy Controls Component

```typescript
// components/strategies/StrategyControls.tsx
import { Pressable, View, Text, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export function StrategyControls({ strategy, onStart, onStop, isLoading }) {
  const handleStop = () => {
    Alert.alert(
      'Stop Strategy',
      'Are you sure you want to stop this strategy? Any open position will remain.',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Stop', style: 'destructive', onPress: onStop },
      ]
    );
  };

  if (strategy.status === 'RUNNING') {
    return (
      <Pressable
        style={[styles.button, styles.stopButton]}
        onPress={handleStop}
        disabled={isLoading}
      >
        <Ionicons name="stop" size={24} color="white" />
        <Text style={styles.buttonText}>Stop Strategy</Text>
      </Pressable>
    );
  }

  return (
    <Pressable
      style={[styles.button, styles.startButton]}
      onPress={onStart}
      disabled={isLoading}
    >
      <Ionicons name="play" size={24} color="white" />
      <Text style={styles.buttonText}>Start Strategy</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    marginHorizontal: 16,
    marginVertical: 8,
  },
  startButton: { backgroundColor: '#22c55e' },
  stopButton: { backgroundColor: '#ef4444' },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
    marginLeft: 8,
  },
});
```

### Position Status Display

```typescript
// components/strategies/PositionStatus.tsx
const POSITION_CONFIG = {
  NONE: { icon: 'remove-circle', color: '#6b7280', label: 'No Position' },
  BOUGHT: { icon: 'arrow-up-circle', color: '#22c55e', label: 'Position Bought' },
  SOLD: { icon: 'arrow-down-circle', color: '#3b82f6', label: 'Position Sold' },
  SL_HIT: { icon: 'alert-circle', color: '#f59e0b', label: 'Stop-Loss Hit' },
};

export function PositionStatus({ position }) {
  const config = POSITION_CONFIG[position] || POSITION_CONFIG.NONE;
  
  return (
    <View style={[styles.container, { borderColor: config.color }]}>
      <Ionicons name={config.icon} size={32} color={config.color} />
      <Text style={[styles.label, { color: config.color }]}>{config.label}</Text>
    </View>
  );
}
```

---

## 6. Success Criteria

✅ Phase 8 is complete when:

- Strategy detail screen displays all information
- Start/Stop buttons work with proper states
- Confirmation dialogs prevent accidental stops
- Position status displays accurately
- Execution log shows order history
- Real-time polling keeps data fresh
- Edit and delete actions work correctly
- P&L displays when trade completed
