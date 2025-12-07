---
goal: Implement simple 5-input strategy creation flow
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, strategy, creation, form, validation]
---

# Phase 7: Strategy Creation

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement the strategy creation flow with exactly 5 inputs (symbol, buy_time, sell_time, stop_loss, quantity), form validation, symbol autocomplete, and time pickers.

---

## 1. Requirements & Constraints

- **UXR-001**: App flow completion under 60 seconds for strategy creation
- **UXR-002**: Maximum 5 inputs for strategy creation (symbol, buy_time, sell_time, stop_loss, quantity)
- **UXR-004**: Clear visual feedback for all actions
- **CON-004**: Execution only during market hours (9:15 AM - 3:30 PM IST)

---

## 2. Implementation Tasks

### GOAL-007: Implement simple 5-input strategy creation flow

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-073 | Create `app/(tabs)/strategies/create.tsx` strategy creation screen with KeyboardAvoidingView, ScrollView | | | Phase 3 |
| TASK-074 | Create `components/strategies/StrategyForm.tsx` with react-hook-form, all 5 inputs in vertical layout | | | TASK-073 |
| TASK-075 | Implement symbol input with autocomplete: TextInput that triggers search API on 2+ characters | | | TASK-074 |
| TASK-076 | Create symbol search results dropdown: FlatList overlay showing matching symbols, tap to select | | | TASK-075 |
| TASK-077 | Create `components/forms/TimePicker.tsx` for buy_time and sell_time using @react-native-community/datetimepicker | | | TASK-074 |
| TASK-078 | Ensure time picker respects market hours: minimum 9:15 AM, maximum 3:30 PM IST, show helper text | | | TASK-077 |
| TASK-079 | Validate buy_time < sell_time: show inline error "Buy time must be before sell time" | | | TASK-077 |
| TASK-080 | Create `components/forms/StopLossInput.tsx` with percentage/absolute toggle, default to percentage | | | TASK-074 |
| TASK-081 | Validate stop_loss is mandatory: show error "Stop-loss is required for risk management" if empty | | | TASK-080 |
| TASK-082 | Create quantity input with numeric keyboard (`keyboardType="number-pad"`), validate quantity > 0 | | | TASK-074 |
| TASK-083 | Validate quantity > 0: show error "Quantity must be at least 1" | | | TASK-082 |
| TASK-084 | Create strategy preview/summary card before submission showing all entered values | | | TASK-074 |
| TASK-085 | Implement form submission: disable button during API call, show loading spinner | | | TASK-074 |
| TASK-086 | Show success toast "Strategy created successfully" and navigate to strategy list on creation | | | TASK-085 |
| TASK-087 | Handle creation errors: show toast with API error message, keep form data | | | TASK-085 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/app/(tabs)/strategies/create.tsx` | Create | Strategy creation screen |
| `mobile/components/strategies/StrategyForm.tsx` | Create | Main form component with all inputs |
| `mobile/components/forms/SymbolInput.tsx` | Create | Symbol input with autocomplete |
| `mobile/components/forms/SymbolSearchResults.tsx` | Create | Autocomplete dropdown |
| `mobile/components/forms/TimePicker.tsx` | Create | Time picker with market hours validation |
| `mobile/components/forms/StopLossInput.tsx` | Create | Stop-loss input with percentage toggle |
| `mobile/components/forms/QuantityInput.tsx` | Create | Numeric quantity input |
| `mobile/components/strategies/StrategyPreview.tsx` | Create | Summary card before submission |
| `mobile/schemas/strategySchema.ts` | Create | Zod validation schema |

---

## 4. Acceptance Criteria

- [ ] Strategy form displays all 5 inputs
- [ ] Symbol search shows autocomplete results
- [ ] Selecting symbol populates input
- [ ] Time pickers only allow market hours
- [ ] buy_time < sell_time validation works
- [ ] Stop-loss is mandatory with clear error
- [ ] Quantity must be > 0
- [ ] Preview shows all values before submit
- [ ] Loading state shown during submission
- [ ] Success navigates to list with toast
- [ ] Errors display without losing form data

---

## 5. Technical Notes

### Strategy Form with Zod Validation

```typescript
// schemas/strategySchema.ts
import { z } from 'zod';

export const strategySchema = z.object({
  symbol: z.string().min(1, 'Symbol is required'),
  buy_time: z.string().regex(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/, 'Invalid time format'),
  sell_time: z.string().regex(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/, 'Invalid time format'),
  stop_loss: z.number().positive('Stop-loss must be positive'),
  quantity: z.number().int().positive('Quantity must be at least 1'),
}).refine((data) => {
  const buyMinutes = timeToMinutes(data.buy_time);
  const sellMinutes = timeToMinutes(data.sell_time);
  return buyMinutes < sellMinutes;
}, {
  message: 'Buy time must be before sell time',
  path: ['sell_time'],
});

function timeToMinutes(time: string): number {
  const [hours, minutes] = time.split(':').map(Number);
  return hours * 60 + minutes;
}
```

### Strategy Form Component

```typescript
// components/strategies/StrategyForm.tsx
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { strategySchema } from '@/schemas/strategySchema';

export function StrategyForm({ onSubmit, isLoading }) {
  const { control, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(strategySchema),
    defaultValues: {
      symbol: '',
      buy_time: '09:30',
      sell_time: '15:00',
      stop_loss: 0,
      quantity: 1,
    },
  });

  return (
    <View>
      <Controller
        control={control}
        name="symbol"
        render={({ field }) => (
          <SymbolInput
            value={field.value}
            onChange={field.onChange}
            error={errors.symbol?.message}
          />
        )}
      />
      {/* ... other inputs */}
    </View>
  );
}
```

### Time Picker with Market Hours

```typescript
// components/forms/TimePicker.tsx
import DateTimePicker from '@react-native-community/datetimepicker';

const MARKET_OPEN = { hours: 9, minutes: 15 };
const MARKET_CLOSE = { hours: 15, minutes: 30 };

export function TimePicker({ value, onChange, label, error }) {
  const [show, setShow] = useState(false);

  const handleChange = (event, selectedDate) => {
    setShow(false);
    if (selectedDate) {
      // Validate market hours
      const hours = selectedDate.getHours();
      const minutes = selectedDate.getMinutes();
      
      if (hours < 9 || (hours === 9 && minutes < 15)) {
        // Set to market open
        selectedDate.setHours(9, 15);
      } else if (hours > 15 || (hours === 15 && minutes > 30)) {
        // Set to market close
        selectedDate.setHours(15, 30);
      }
      
      onChange(formatTime(selectedDate));
    }
  };

  return (
    <View>
      <Text>{label}</Text>
      <Pressable onPress={() => setShow(true)}>
        <Text>{value || 'Select time'}</Text>
      </Pressable>
      <Text style={styles.helper}>Market hours: 9:15 AM - 3:30 PM</Text>
      {error && <Text style={styles.error}>{error}</Text>}
      {show && (
        <DateTimePicker
          value={parseTime(value)}
          mode="time"
          is24Hour={false}
          onChange={handleChange}
        />
      )}
    </View>
  );
}
```

---

## 6. Success Criteria

✅ Phase 7 is complete when:

- Strategy form has exactly 5 inputs
- Symbol autocomplete works with API search
- Time pickers enforce market hours
- All validations show inline errors
- Stop-loss is mandatory
- Form submission creates strategy via API
- Success/error feedback is shown
- Under 60 seconds to complete flow
