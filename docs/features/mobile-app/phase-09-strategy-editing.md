---
goal: Enable editing of strategy parameters with validation
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, strategy, editing, form, validation]
---

# Phase 9: Strategy Editing

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Enable editing of strategy parameters with contextual validation based on strategy status (RUNNING vs STOPPED), form pre-population, and proper error handling.

---

## 1. Requirements & Constraints

- **UXR-004**: Clear visual feedback for all actions
- **CON-004**: Execution only during market hours (9:15 AM - 3:30 PM IST)

---

## 2. Implementation Tasks

### GOAL-009: Enable editing of strategy parameters with validation

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-102 | Create `app/(tabs)/strategies/[id]/edit.tsx` strategy edit screen | | | Phase 7, Phase 8 |
| TASK-103 | Pre-populate form with existing strategy values from useStrategyDetail hook | | | TASK-102 |
| TASK-104 | Allow editing of ALL parameters when strategy status is STOPPED | | | TASK-102 |
| TASK-105 | Allow editing ONLY stop_loss and sell_time when strategy status is RUNNING | | | TASK-102 |
| TASK-106 | Disable symbol and buy_time inputs when RUNNING: gray out, add lock icon, show tooltip "Cannot change while running" | | | TASK-105 |
| TASK-107 | Show warning banner when editing a running strategy: "Changes will take effect immediately" | | | TASK-105 |
| TASK-108 | Implement update API call with loading state, use useUpdateStrategy mutation hook | | | TASK-102 |
| TASK-109 | Navigate back to detail screen on successful update with success toast | | | TASK-108 |
| TASK-110 | Handle update errors: show toast with error message, keep form data for correction | | | TASK-108 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/app/(tabs)/strategies/[id]/edit.tsx` | Create | Strategy edit screen |
| `mobile/components/strategies/EditStrategyForm.tsx` | Create | Edit form with conditional fields |
| `mobile/components/common/DisabledInput.tsx` | Create | Disabled input with lock icon |
| `mobile/components/common/WarningBanner.tsx` | Create | Warning message banner |
| `mobile/hooks/useUpdateStrategy.ts` | Modify | Add update mutation if not exists |

---

## 4. Acceptance Criteria

- [ ] Edit screen loads with pre-populated values
- [ ] All fields editable when strategy is STOPPED
- [ ] Only stop_loss and sell_time editable when RUNNING
- [ ] Disabled fields show lock icon and tooltip
- [ ] Warning banner shows for running strategies
- [ ] Update API call works correctly
- [ ] Success navigates back with toast
- [ ] Errors display without losing data
- [ ] All validations from creation still apply

---

## 5. Technical Notes

### Edit Strategy Screen

```typescript
// app/(tabs)/strategies/[id]/edit.tsx
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useStrategyDetail } from '@/hooks/useStrategyDetail';
import { useUpdateStrategy } from '@/hooks/useUpdateStrategy';

export default function EditStrategyScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const { data: strategy, isLoading } = useStrategyDetail(id);
  const updateMutation = useUpdateStrategy();

  const isRunning = strategy?.status === 'RUNNING';

  const handleSubmit = async (data: UpdateStrategyData) => {
    try {
      await updateMutation.mutateAsync({ id, data });
      Toast.show({ type: 'success', text1: 'Strategy updated successfully' });
      router.back();
    } catch (error) {
      Toast.show({ type: 'error', text1: parseApiError(error).message });
    }
  };

  if (isLoading) return <LoadingScreen />;
  if (!strategy) return <NotFoundScreen />;

  return (
    <ScrollView>
      {isRunning && (
        <WarningBanner message="Changes will take effect immediately" />
      )}
      <EditStrategyForm
        strategy={strategy}
        isRunning={isRunning}
        onSubmit={handleSubmit}
        isSubmitting={updateMutation.isPending}
      />
    </ScrollView>
  );
}
```

### Conditional Edit Form

```typescript
// components/strategies/EditStrategyForm.tsx
export function EditStrategyForm({ strategy, isRunning, onSubmit, isSubmitting }) {
  const { control, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(updateStrategySchema),
    defaultValues: {
      symbol: strategy.symbol,
      buy_time: strategy.buy_time,
      sell_time: strategy.sell_time,
      stop_loss: strategy.stop_loss,
      quantity: strategy.quantity,
    },
  });

  return (
    <View style={styles.container}>
      {/* Symbol - disabled when running */}
      <Controller
        control={control}
        name="symbol"
        render={({ field }) => (
          isRunning ? (
            <DisabledInput
              label="Symbol"
              value={field.value}
              tooltip="Cannot change symbol while strategy is running"
            />
          ) : (
            <SymbolInput
              value={field.value}
              onChange={field.onChange}
              error={errors.symbol?.message}
            />
          )
        )}
      />

      {/* Buy Time - disabled when running */}
      <Controller
        control={control}
        name="buy_time"
        render={({ field }) => (
          isRunning ? (
            <DisabledInput
              label="Buy Time"
              value={field.value}
              tooltip="Cannot change buy time while strategy is running"
            />
          ) : (
            <TimePicker
              label="Buy Time"
              value={field.value}
              onChange={field.onChange}
              error={errors.buy_time?.message}
            />
          )
        )}
      />

      {/* Sell Time - always editable */}
      <Controller
        control={control}
        name="sell_time"
        render={({ field }) => (
          <TimePicker
            label="Sell Time"
            value={field.value}
            onChange={field.onChange}
            error={errors.sell_time?.message}
          />
        )}
      />

      {/* Stop Loss - always editable */}
      <Controller
        control={control}
        name="stop_loss"
        render={({ field }) => (
          <StopLossInput
            value={field.value}
            onChange={field.onChange}
            error={errors.stop_loss?.message}
          />
        )}
      />

      {/* Quantity - disabled when running */}
      <Controller
        control={control}
        name="quantity"
        render={({ field }) => (
          isRunning ? (
            <DisabledInput
              label="Quantity"
              value={String(field.value)}
              tooltip="Cannot change quantity while strategy is running"
            />
          ) : (
            <QuantityInput
              value={field.value}
              onChange={field.onChange}
              error={errors.quantity?.message}
            />
          )
        )}
      />

      <Button
        title="Save Changes"
        onPress={handleSubmit(onSubmit)}
        loading={isSubmitting}
        disabled={isSubmitting}
      />
    </View>
  );
}
```

### Disabled Input Component

```typescript
// components/common/DisabledInput.tsx
import { Ionicons } from '@expo/vector-icons';
import { Tooltip } from 'react-native-paper';

export function DisabledInput({ label, value, tooltip }) {
  return (
    <View style={styles.container}>
      <View style={styles.labelRow}>
        <Text style={styles.label}>{label}</Text>
        <Tooltip title={tooltip}>
          <Ionicons name="lock-closed" size={16} color="#9ca3af" />
        </Tooltip>
      </View>
      <View style={styles.inputContainer}>
        <Text style={styles.disabledValue}>{value}</Text>
      </View>
    </View>
  );
}
```

---

## 6. Success Criteria

✅ Phase 9 is complete when:

- Edit screen loads with correct values
- Conditional editing based on status works
- Disabled fields clearly indicate locked state
- Warning banner shows for running strategies
- All validations apply correctly
- Update API works with proper feedback
- Navigation and toasts work correctly
