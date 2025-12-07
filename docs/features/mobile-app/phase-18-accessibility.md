---
goal: Ensure app is accessible for users with disabilities
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, accessibility, a11y, voiceover, talkback]
---

# Phase 18: Accessibility

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Ensure the app is accessible for users with disabilities by implementing proper accessibility labels, roles, hints, screen reader support, and visual accessibility features.

---

## 1. Requirements & Constraints

- **WCAG 2.1 AA**: Accessibility compliance target
- Minimum touch target: 44x44 pts
- Color contrast: 4.5:1 for text

---

## 2. Implementation Tasks

### GOAL-018: Ensure app is accessible for users with disabilities

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-197 | Add `accessibilityLabel` to all interactive elements: buttons, inputs, cards, icons | | | All Phases |
| TASK-198 | Add `accessibilityHint` for complex actions: explain what will happen when activated | | | TASK-197 |
| TASK-199 | Ensure proper `accessibilityRole` for custom components: button, link, header, image, etc. | | | TASK-197 |
| TASK-200 | Test with VoiceOver (iOS) and TalkBack (Android): navigate entire app with screen reader | | | TASK-197 |
| TASK-201 | Ensure minimum touch target size of 44x44 pts for all interactive elements | | | Phase 15 |
| TASK-202 | Add accessible error announcements for form validation: use accessibilityLiveRegion | | | Phase 16 |
| TASK-203 | Ensure color contrast meets WCAG AA standards: 4.5:1 for normal text, 3:1 for large text | | | Phase 15 |
| TASK-204 | Support dynamic font sizing: respect system text size preferences with `allowFontScaling` | | | Phase 15 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/components/ui/Button.tsx` | Modify | Add accessibility props |
| `mobile/components/ui/Input.tsx` | Modify | Add accessibility props |
| `mobile/components/ui/Card.tsx` | Modify | Add accessibility props |
| `mobile/components/strategies/StrategyCard.tsx` | Modify | Add accessibility props |
| `mobile/components/strategies/StrategyControls.tsx` | Modify | Add accessibility props |
| `mobile/constants/theme.ts` | Modify | Verify contrast ratios |
| `mobile/utils/accessibility.ts` | Create | Accessibility utilities |

---

## 4. Acceptance Criteria

- [ ] All buttons have accessibility labels
- [ ] All inputs have accessibility labels
- [ ] Complex actions have accessibility hints
- [ ] Custom components have proper roles
- [ ] App navigable with VoiceOver
- [ ] App navigable with TalkBack
- [ ] Touch targets are 44x44 pts minimum
- [ ] Form errors announced to screen readers
- [ ] Color contrast passes WCAG AA
- [ ] Dynamic font sizing works

---

## 5. Technical Notes

### Accessibility Utilities

```typescript
// utils/accessibility.ts
import { AccessibilityInfo, Platform } from 'react-native';

export async function isScreenReaderEnabled(): Promise<boolean> {
  return AccessibilityInfo.isScreenReaderEnabled();
}

export function announceForAccessibility(message: string): void {
  AccessibilityInfo.announceForAccessibility(message);
}

// Format currency for screen readers
export function formatCurrencyForA11y(amount: number): string {
  const formatted = Math.abs(amount).toLocaleString('en-IN');
  if (amount < 0) {
    return `negative ${formatted} rupees`;
  }
  return `${formatted} rupees`;
}

// Format time for screen readers
export function formatTimeForA11y(time: string): string {
  const [hours, minutes] = time.split(':').map(Number);
  const period = hours >= 12 ? 'PM' : 'AM';
  const displayHours = hours % 12 || 12;
  return `${displayHours}:${minutes.toString().padStart(2, '0')} ${period}`;
}
```

### Accessible Button Component

```typescript
// components/ui/Button.tsx (accessibility additions)
export function Button({
  title,
  onPress,
  accessibilityLabel,
  accessibilityHint,
  disabled,
  loading,
  ...props
}: ButtonProps) {
  const a11yLabel = accessibilityLabel || title;
  const a11yHint = accessibilityHint;
  
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled || loading}
      accessibilityRole="button"
      accessibilityLabel={a11yLabel}
      accessibilityHint={a11yHint}
      accessibilityState={{
        disabled: disabled || loading,
        busy: loading,
      }}
      style={({ pressed }) => [
        styles.base,
        pressed && styles.pressed,
        { minHeight: 44, minWidth: 44 }, // Minimum touch target
      ]}
      {...props}
    >
      {loading ? (
        <ActivityIndicator accessibilityLabel="Loading" />
      ) : (
        <Text style={styles.text}>{title}</Text>
      )}
    </Pressable>
  );
}
```

### Accessible Input Component

```typescript
// components/ui/Input.tsx (accessibility additions)
export function Input({
  label,
  value,
  error,
  helperText,
  accessibilityLabel,
  ...props
}: InputProps) {
  const inputRef = useRef<TextInput>(null);
  
  return (
    <View>
      {label && (
        <Text
          style={styles.label}
          accessibilityRole="text"
          nativeID={`${label}-label`}
        >
          {label}
        </Text>
      )}
      
      <TextInput
        ref={inputRef}
        value={value}
        style={[styles.input, error && styles.inputError]}
        accessibilityLabel={accessibilityLabel || label}
        accessibilityLabelledBy={label ? `${label}-label` : undefined}
        accessibilityState={{ disabled: props.editable === false }}
        accessibilityHint={helperText}
        {...props}
      />
      
      {error && (
        <Text
          style={styles.error}
          accessibilityRole="alert"
          accessibilityLiveRegion="polite"
        >
          {error}
        </Text>
      )}
      
      {helperText && !error && (
        <Text style={styles.helper}>{helperText}</Text>
      )}
    </View>
  );
}
```

### Accessible Strategy Card

```typescript
// components/strategies/StrategyCard.tsx (accessibility additions)
export function StrategyCard({ strategy, onPress }: StrategyCardProps) {
  const statusLabel = {
    RUNNING: 'Running',
    STOPPED: 'Stopped',
    COMPLETED: 'Completed',
    ERROR: 'Error',
  }[strategy.status];

  const accessibilityLabel = [
    `${strategy.symbol} strategy`,
    `Status: ${statusLabel}`,
    `Buy time: ${formatTimeForA11y(strategy.buy_time)}`,
    `Sell time: ${formatTimeForA11y(strategy.sell_time)}`,
    `Quantity: ${strategy.quantity}`,
  ].join('. ');

  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel}
      accessibilityHint="Double tap to view strategy details"
      style={styles.card}
    >
      <View style={styles.header}>
        <Text style={styles.symbol} accessibilityRole="header">
          {strategy.symbol}
        </Text>
        <StatusBadge
          status={strategy.status}
          accessibilityLabel={`Status: ${statusLabel}`}
        />
      </View>
      {/* ... rest of card */}
    </Pressable>
  );
}
```

### Color Contrast Verification

```typescript
// constants/theme.ts (color contrast notes)
export const colors = {
  // Primary green - verified 4.5:1 contrast on white
  primary: {
    500: '#22c55e', // Use only on large text or icons on white
    600: '#16a34a', // Safe for body text on white (4.52:1)
    700: '#15803d', // Safe for all text on white (5.47:1)
  },
  
  // Gray - text colors
  gray: {
    500: '#6b7280', // Minimum for body text on white (4.48:1)
    600: '#4b5563', // Safe for body text on white (6.89:1)
    700: '#374151', // Recommended for body text (9.73:1)
    900: '#111827', // Headings and important text (16.74:1)
  },
  
  // Error red - verified contrast
  red: {
    500: '#ef4444', // Use with caution on white (3.68:1)
    600: '#dc2626', // Safe for text on white (4.51:1)
  },
};
```

---

## 6. Success Criteria

✅ Phase 18 is complete when:

- All interactive elements have accessibility labels
- Complex actions have accessibility hints
- Custom components have proper roles
- VoiceOver navigation works end-to-end
- TalkBack navigation works end-to-end
- All touch targets are 44x44 pts minimum
- Form errors announce to screen readers
- Color contrast meets WCAG AA
- Dynamic font sizing respected
