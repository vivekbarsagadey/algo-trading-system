---
goal: Implement comprehensive error handling and user feedback
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, error-handling, feedback, toast, haptics]
---

# Phase 16: Error Handling & Feedback

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement comprehensive error handling with error boundaries, user-friendly error messages, toast notifications, haptic feedback, and retry mechanisms.

---

## 1. Requirements & Constraints

- **UXR-004**: Clear visual feedback for all actions
- **UXR-006**: Loading states for all network operations

---

## 2. Implementation Tasks

### GOAL-016: Implement comprehensive error handling and user feedback

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-181 | Create global error boundary component in `components/ErrorBoundary.tsx` to catch React errors | | | Phase 1 |
| TASK-182 | Create `app/+not-found.tsx` for 404/not found route handling with navigation back | | | Phase 3 |
| TASK-183 | Implement toast notification system: configure react-native-toast-message with custom styling | | | Phase 15 |
| TASK-184 | Create error code mapping in `utils/errorMessages.ts`: map API error codes to user-friendly messages | | | Phase 4 |
| TASK-185 | Add haptic feedback for button presses using expo-haptics: light impact on tap, success/error on result | | | Phase 1 |
| TASK-186 | Create retry mechanism in `components/common/RetryView.tsx`: "Something went wrong" with retry button | | | Phase 4 |
| TASK-187 | Show "Something went wrong" screen with illustration, message, retry button for fatal errors | | | TASK-186 |
| TASK-188 | Integrate error logging to Sentry: `expo install @sentry/react-native` and configure | | | Phase 1 |
| TASK-189 | Add form validation error display with inline error messages under each field | | | Phase 7 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/components/ErrorBoundary.tsx` | Create | React error boundary |
| `mobile/app/+not-found.tsx` | Create | 404 screen |
| `mobile/utils/errorMessages.ts` | Create | Error code to message mapping |
| `mobile/utils/haptics.ts` | Create | Haptic feedback utilities |
| `mobile/components/common/RetryView.tsx` | Create | Retry error view |
| `mobile/components/common/ErrorScreen.tsx` | Create | Full-screen error |
| `mobile/providers/ToastProvider.tsx` | Create | Toast configuration |
| `mobile/services/sentry.ts` | Create | Sentry configuration |
| `mobile/app/_layout.tsx` | Modify | Add error boundary and toast |

---

## 4. Acceptance Criteria

- [ ] Error boundary catches React errors
- [ ] 404 screen displays for unknown routes
- [ ] Toast notifications work for success/error
- [ ] API errors show user-friendly messages
- [ ] Haptic feedback works on buttons
- [ ] Retry mechanism works correctly
- [ ] Errors logged to Sentry
- [ ] Form validation shows inline errors

---

## 5. Technical Notes

### Error Boundary

```typescript
// components/ErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { ErrorScreen } from '@/components/common/ErrorScreen';
import * as Sentry from '@sentry/react-native';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    Sentry.captureException(error, { extra: { errorInfo } });
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <ErrorScreen
          title="Something went wrong"
          message="We're sorry, but something unexpected happened."
          onRetry={this.handleRetry}
        />
      );
    }

    return this.props.children;
  }
}
```

### Error Messages Mapping

```typescript
// utils/errorMessages.ts
const ERROR_MESSAGES: Record<string, string> = {
  // Auth errors
  AUTH_001: 'Invalid email or password',
  AUTH_002: 'Session expired. Please login again',
  AUTH_003: 'Account is disabled. Contact support',
  
  // Broker errors
  BRK_001: 'Failed to connect to broker',
  BRK_002: 'Invalid broker credentials',
  BRK_003: 'Broker session expired. Please reconnect',
  
  // Strategy errors
  STR_001: 'Strategy not found',
  STR_002: 'Invalid strategy parameters',
  STR_003: 'Strategy is already running',
  STR_004: 'Cannot delete a running strategy',
  
  // Execution errors
  EXE_001: 'Order execution failed',
  EXE_002: 'Insufficient funds',
  EXE_003: 'Market is closed',
  
  // Network errors
  NETWORK_ERROR: 'Network error. Check your connection',
  TIMEOUT_ERROR: 'Request timed out. Please try again',
  SERVER_ERROR: 'Server error. Please try again later',
  
  // Default
  UNKNOWN_ERROR: 'Something went wrong. Please try again',
};

export function getErrorMessage(code: string): string {
  return ERROR_MESSAGES[code] || ERROR_MESSAGES.UNKNOWN_ERROR;
}

export function parseApiError(error: any): { code: string; message: string } {
  if (error?.response?.data?.error_code) {
    const code = error.response.data.error_code;
    return { code, message: getErrorMessage(code) };
  }
  
  if (!error?.response) {
    return { code: 'NETWORK_ERROR', message: getErrorMessage('NETWORK_ERROR') };
  }
  
  if (error.code === 'ECONNABORTED') {
    return { code: 'TIMEOUT_ERROR', message: getErrorMessage('TIMEOUT_ERROR') };
  }
  
  return { code: 'UNKNOWN_ERROR', message: getErrorMessage('UNKNOWN_ERROR') };
}
```

### Haptic Feedback Utilities

```typescript
// utils/haptics.ts
import * as Haptics from 'expo-haptics';
import { Platform } from 'react-native';

export const haptics = {
  light: () => {
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
  },
  
  medium: () => {
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }
  },
  
  heavy: () => {
    if (Platform.OS !== 'web') {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
    }
  },
  
  success: () => {
    if (Platform.OS !== 'web') {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    }
  },
  
  error: () => {
    if (Platform.OS !== 'web') {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    }
  },
  
  warning: () => {
    if (Platform.OS !== 'web') {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
    }
  },
};
```

### Retry View Component

```typescript
// components/common/RetryView.tsx
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Button } from '@/components/ui/Button';
import { colors, spacing } from '@/constants/theme';

interface RetryViewProps {
  message?: string;
  onRetry: () => void;
  isRetrying?: boolean;
}

export function RetryView({
  message = 'Something went wrong',
  onRetry,
  isRetrying = false,
}: RetryViewProps) {
  return (
    <View style={styles.container}>
      <Ionicons name="alert-circle-outline" size={64} color={colors.gray[400]} />
      <Text style={styles.message}>{message}</Text>
      <Button
        title="Try Again"
        onPress={onRetry}
        loading={isRetrying}
        variant="primary"
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
  },
  message: {
    fontSize: 16,
    color: colors.gray[600],
    textAlign: 'center',
    marginVertical: spacing.lg,
  },
});
```

---

## 6. Success Criteria

✅ Phase 16 is complete when:

- Error boundary catches and displays errors
- 404 screen works for unknown routes
- Toast notifications display correctly
- API errors show friendly messages
- Haptic feedback works on interactions
- Retry mechanism functions correctly
- Errors logged to Sentry
- Form validation displays inline
