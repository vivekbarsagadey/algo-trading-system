---
goal: Implement push notification handling for order events
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, notifications, push, expo-notifications, alerts]
---

# Phase 12: Push Notifications

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement push notification handling for order execution events, stop-loss triggers, and strategy errors with proper permission handling and deep linking navigation.

---

## 1. Requirements & Constraints

- **REQ-004**: Push notification support for order events
- **REQ-006**: Deep linking for notification navigation
- **UXR-004**: Clear visual feedback for all actions

---

## 2. Implementation Tasks

### GOAL-012: Implement push notification handling for order events

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-140 | Install expo-notifications: `expo install expo-notifications expo-device expo-constants` | | | Phase 1 |
| TASK-141 | Configure notification permissions request on app first launch or from settings | | | TASK-140 |
| TASK-142 | Create `utils/notifications.ts` with `registerForPushNotifications()`, `handleNotificationReceived()`, `handleNotificationResponse()` | | | TASK-140 |
| TASK-143 | Register device push token with backend: POST /users/devices with expo_push_token | | | TASK-142 |
| TASK-144 | Handle foreground notifications: show in-app alert/toast when notification received while app is open | | | TASK-142 |
| TASK-145 | Handle background notification tap: navigate to relevant screen based on notification data | | | TASK-142 |
| TASK-146 | Navigate to strategy detail on ORDER_EXECUTED notification tap: extract strategy_id from data | | | TASK-145 |
| TASK-147 | Create notification payload types: ORDER_EXECUTED, SL_TRIGGERED, STRATEGY_ERROR, TOKEN_EXPIRY | | | TASK-142 |
| TASK-148 | Add notification badge: update app icon badge count for unread notifications | | | TASK-142 |
| TASK-149 | Create notification center screen (optional): list of past notifications with read/unread status | | | TASK-142 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/utils/notifications.ts` | Create | Push notification utilities |
| `mobile/app/_layout.tsx` | Modify | Add notification listeners |
| `mobile/api/devices.ts` | Create | Device registration API |
| `mobile/types/notification.ts` | Create | Notification type definitions |
| `mobile/components/notifications/InAppNotification.tsx` | Create | Foreground notification toast |
| `mobile/app/(tabs)/notifications.tsx` | Create | Notification center screen (optional) |
| `mobile/app.json` | Modify | Add notification configuration |

---

## 4. Acceptance Criteria

- [ ] Push notification permission requested appropriately
- [ ] Device token registered with backend
- [ ] Foreground notifications show in-app alert
- [ ] Background notification tap navigates correctly
- [ ] ORDER_EXECUTED notification opens strategy detail
- [ ] SL_TRIGGERED notification opens strategy detail
- [ ] Notification badge updates correctly
- [ ] Notifications respect user preferences

---

## 5. Technical Notes

### Notification Setup

```typescript
// utils/notifications.ts
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';
import { Platform } from 'react-native';
import { router } from 'expo-router';
import { registerDeviceToken } from '@/api/devices';

// Configure notification behavior
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export async function registerForPushNotifications(): Promise<string | null> {
  if (!Device.isDevice) {
    console.log('Push notifications only work on physical devices');
    return null;
  }

  // Check existing permissions
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  // Request permissions if not granted
  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    console.log('Push notification permission denied');
    return null;
  }

  // Get push token
  const projectId = Constants.expoConfig?.extra?.eas?.projectId;
  const token = await Notifications.getExpoPushTokenAsync({ projectId });

  // Register with backend
  await registerDeviceToken(token.data);

  // Android-specific channel setup
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('orders', {
      name: 'Order Updates',
      importance: Notifications.AndroidImportance.HIGH,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#22c55e',
    });
  }

  return token.data;
}

export function handleNotificationResponse(response: Notifications.NotificationResponse) {
  const data = response.notification.request.content.data;
  
  switch (data.type) {
    case 'ORDER_EXECUTED':
    case 'SL_TRIGGERED':
    case 'STRATEGY_ERROR':
      if (data.strategy_id) {
        router.push(`/strategies/${data.strategy_id}`);
      }
      break;
    case 'TOKEN_EXPIRY':
      router.push('/broker');
      break;
    default:
      router.push('/');
  }
}
```

### Root Layout Integration

```typescript
// app/_layout.tsx
import * as Notifications from 'expo-notifications';
import { useEffect, useRef } from 'react';
import { 
  registerForPushNotifications, 
  handleNotificationResponse 
} from '@/utils/notifications';

export default function RootLayout() {
  const notificationListener = useRef<Notifications.Subscription>();
  const responseListener = useRef<Notifications.Subscription>();

  useEffect(() => {
    // Register for push notifications
    registerForPushNotifications();

    // Foreground notification listener
    notificationListener.current = Notifications.addNotificationReceivedListener(
      (notification) => {
        // Show in-app notification
        showInAppNotification(notification);
      }
    );

    // Notification response listener (tap)
    responseListener.current = Notifications.addNotificationResponseReceivedListener(
      handleNotificationResponse
    );

    return () => {
      if (notificationListener.current) {
        Notifications.removeNotificationSubscription(notificationListener.current);
      }
      if (responseListener.current) {
        Notifications.removeNotificationSubscription(responseListener.current);
      }
    };
  }, []);

  // ... rest of layout
}
```

### Notification Types

```typescript
// types/notification.ts
export type NotificationType = 
  | 'ORDER_EXECUTED'
  | 'SL_TRIGGERED'
  | 'STRATEGY_ERROR'
  | 'TOKEN_EXPIRY';

export interface NotificationData {
  type: NotificationType;
  strategy_id?: string;
  order_type?: 'BUY' | 'SELL';
  symbol?: string;
  price?: number;
  message?: string;
}

export interface AppNotification {
  id: string;
  type: NotificationType;
  title: string;
  body: string;
  data: NotificationData;
  read: boolean;
  created_at: string;
}
```

### App Configuration for Notifications

```json
// app.json (partial)
{
  "expo": {
    "plugins": [
      [
        "expo-notifications",
        {
          "icon": "./assets/notification-icon.png",
          "color": "#22c55e",
          "sounds": ["./assets/notification-sound.wav"]
        }
      ]
    ],
    "android": {
      "useNextNotificationsApi": true
    }
  }
}
```

---

## 6. Success Criteria

✅ Phase 12 is complete when:

- Push notification permissions handled correctly
- Device token registered with backend
- Foreground notifications show in-app
- Background taps navigate to correct screen
- All notification types handled properly
- Badge count updates correctly
- User preferences respected
