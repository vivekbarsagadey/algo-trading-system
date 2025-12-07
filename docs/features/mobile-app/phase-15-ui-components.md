---
goal: Create reusable UI component library for consistent design
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, ui-components, design-system, theme, accessibility]
---

# Phase 15: UI Components Library

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Create a reusable UI component library with consistent design tokens, variants, and accessibility support for use across the entire application.

---

## 1. Requirements & Constraints

- **UXR-004**: Clear visual feedback for all actions
- **PER-002**: Screen transitions < 300ms
- **WCAG**: Accessibility compliance

---

## 2. Implementation Tasks

### GOAL-015: Create reusable UI component library for consistent design

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-168 | Create `components/ui/Button.tsx` with variants: primary (green), secondary (gray), danger (red), outline, ghost | | | Phase 1 |
| TASK-169 | Create `components/ui/Input.tsx` with label, error message, helper text, icons, disabled state | | | Phase 1 |
| TASK-170 | Create `components/ui/Card.tsx` with shadow options, border options, padding variants | | | Phase 1 |
| TASK-171 | Create `components/ui/Badge.tsx` for status indicators with colors: success, warning, error, info, neutral | | | Phase 1 |
| TASK-172 | Create `components/ui/Toast.tsx` or integrate react-native-toast-message with custom styling | | | Phase 1 |
| TASK-173 | Create `components/ui/Dialog.tsx` for confirmation modals with title, message, confirm/cancel actions | | | Phase 1 |
| TASK-174 | Create `components/ui/LoadingSpinner.tsx` and LoadingOverlay for full-screen loading | | | Phase 1 |
| TASK-175 | Create `components/ui/Skeleton.tsx` for loading placeholders with shimmer animation | | | Phase 1 |
| TASK-176 | Create `components/ui/EmptyState.tsx` for empty lists with icon, title, description, action button | | | Phase 1 |
| TASK-177 | Create `components/ui/ErrorState.tsx` for error displays with icon, message, retry button | | | Phase 1 |
| TASK-178 | Create `components/ui/Divider.tsx` for section separation with optional label | | | Phase 1 |
| TASK-179 | Create theme configuration in `constants/theme.ts` with colors, spacing, typography, shadows | | | Phase 1 |
| TASK-180 | Ensure all components support dark mode (if implementing theme support) | | | TASK-179 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/components/ui/Button.tsx` | Create | Button with variants |
| `mobile/components/ui/Input.tsx` | Create | Text input with states |
| `mobile/components/ui/Card.tsx` | Create | Card container |
| `mobile/components/ui/Badge.tsx` | Create | Status badge |
| `mobile/components/ui/Toast.tsx` | Create | Toast notifications |
| `mobile/components/ui/Dialog.tsx` | Create | Confirmation dialog |
| `mobile/components/ui/LoadingSpinner.tsx` | Create | Loading indicator |
| `mobile/components/ui/Skeleton.tsx` | Create | Loading placeholder |
| `mobile/components/ui/EmptyState.tsx` | Create | Empty state display |
| `mobile/components/ui/ErrorState.tsx` | Create | Error state display |
| `mobile/components/ui/Divider.tsx` | Create | Section divider |
| `mobile/constants/theme.ts` | Create | Design tokens |
| `mobile/hooks/useTheme.ts` | Create | Theme hook |
| `mobile/components/ui/index.ts` | Create | Barrel export |

---

## 4. Acceptance Criteria

- [ ] All UI components follow consistent design
- [ ] Button variants work correctly
- [ ] Input shows all states (focused, error, disabled)
- [ ] Badges display with correct colors
- [ ] Toast notifications appear correctly
- [ ] Dialog shows with proper overlay
- [ ] Loading states display with animation
- [ ] Skeleton has shimmer effect
- [ ] Empty/Error states are reusable
- [ ] Theme tokens used consistently
- [ ] Dark mode works (if implemented)

---

## 5. Technical Notes

### Theme Configuration

```typescript
// constants/theme.ts
export const colors = {
  primary: {
    50: '#f0fdf4',
    100: '#dcfce7',
    500: '#22c55e',
    600: '#16a34a',
    700: '#15803d',
  },
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
  red: {
    500: '#ef4444',
    600: '#dc2626',
  },
  yellow: {
    500: '#eab308',
    600: '#ca8a04',
  },
  blue: {
    500: '#3b82f6',
    600: '#2563eb',
  },
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  '2xl': 32,
};

export const typography = {
  fontFamily: {
    regular: 'System',
    medium: 'System',
    semibold: 'System',
    bold: 'System',
  },
  fontSize: {
    xs: 12,
    sm: 14,
    base: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 30,
  },
};

export const shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 6,
    elevation: 3,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.15,
    shadowRadius: 15,
    elevation: 5,
  },
};

export const borderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999,
};
```

### Button Component

```typescript
// components/ui/Button.tsx
import { Pressable, Text, ActivityIndicator, StyleSheet, ViewStyle, TextStyle } from 'react-native';
import { colors, spacing, borderRadius, typography } from '@/constants/theme';

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'outline' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: ButtonVariant;
  size?: ButtonSize;
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  fullWidth?: boolean;
}

export function Button({
  title,
  onPress,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  icon,
  fullWidth = false,
}: ButtonProps) {
  const buttonStyles = [
    styles.base,
    styles[`variant_${variant}`],
    styles[`size_${size}`],
    fullWidth && styles.fullWidth,
    disabled && styles.disabled,
  ];

  const textStyles = [
    styles.text,
    styles[`text_${variant}`],
    styles[`textSize_${size}`],
  ];

  return (
    <Pressable
      style={({ pressed }) => [
        ...buttonStyles,
        pressed && styles.pressed,
      ]}
      onPress={onPress}
      disabled={disabled || loading}
      accessibilityRole="button"
      accessibilityState={{ disabled: disabled || loading }}
    >
      {loading ? (
        <ActivityIndicator color={variant === 'primary' ? 'white' : colors.primary[500]} />
      ) : (
        <>
          {icon}
          <Text style={textStyles}>{title}</Text>
        </>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: borderRadius.md,
  },
  variant_primary: {
    backgroundColor: colors.primary[500],
  },
  variant_secondary: {
    backgroundColor: colors.gray[200],
  },
  variant_danger: {
    backgroundColor: colors.red[500],
  },
  variant_outline: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: colors.primary[500],
  },
  variant_ghost: {
    backgroundColor: 'transparent',
  },
  size_sm: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
  },
  size_md: {
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
  },
  size_lg: {
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.xl,
  },
  fullWidth: {
    width: '100%',
  },
  disabled: {
    opacity: 0.5,
  },
  pressed: {
    opacity: 0.8,
  },
  text: {
    fontWeight: '600',
  },
  text_primary: {
    color: 'white',
  },
  text_secondary: {
    color: colors.gray[700],
  },
  text_danger: {
    color: 'white',
  },
  text_outline: {
    color: colors.primary[500],
  },
  text_ghost: {
    color: colors.primary[500],
  },
  textSize_sm: {
    fontSize: typography.fontSize.sm,
  },
  textSize_md: {
    fontSize: typography.fontSize.base,
  },
  textSize_lg: {
    fontSize: typography.fontSize.lg,
  },
});
```

### Skeleton Component with Shimmer

```typescript
// components/ui/Skeleton.tsx
import { useEffect, useRef } from 'react';
import { View, Animated, StyleSheet, ViewStyle } from 'react-native';
import { colors, borderRadius } from '@/constants/theme';

interface SkeletonProps {
  width: number | string;
  height: number;
  borderRadius?: number;
  style?: ViewStyle;
}

export function Skeleton({
  width,
  height,
  borderRadius: radius = borderRadius.md,
  style,
}: SkeletonProps) {
  const shimmerAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(shimmerAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(shimmerAnim, {
          toValue: 0,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, []);

  const opacity = shimmerAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0.3, 0.7],
  });

  return (
    <Animated.View
      style={[
        styles.skeleton,
        { width, height, borderRadius: radius, opacity },
        style,
      ]}
    />
  );
}

const styles = StyleSheet.create({
  skeleton: {
    backgroundColor: colors.gray[200],
  },
});
```

### Barrel Export

```typescript
// components/ui/index.ts
export { Button } from './Button';
export { Input } from './Input';
export { Card } from './Card';
export { Badge } from './Badge';
export { Toast } from './Toast';
export { Dialog } from './Dialog';
export { LoadingSpinner } from './LoadingSpinner';
export { Skeleton } from './Skeleton';
export { EmptyState } from './EmptyState';
export { ErrorState } from './ErrorState';
export { Divider } from './Divider';
```

---

## 6. Success Criteria

✅ Phase 15 is complete when:

- All UI components are implemented
- Components follow consistent design tokens
- All variants and states work correctly
- Components are accessible
- Components support dark mode (if applicable)
- Barrel export allows easy imports
