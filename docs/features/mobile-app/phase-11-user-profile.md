---
goal: Implement user profile and settings screens
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, profile, settings, preferences, account]
---

# Phase 11: User Profile

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement user profile screen with account information, settings, password change, notification preferences, and logout functionality.

---

## 1. Requirements & Constraints

- **SEC-002**: Biometric authentication for app access (optional)
- **UXR-004**: Clear visual feedback for all actions

---

## 2. Implementation Tasks

### GOAL-011: Implement user profile and settings screens

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-126 | Create `app/(tabs)/profile/index.tsx` profile screen with user info, settings menu list | | | Phase 2, Phase 3 |
| TASK-127 | Display user email and name from authStore | | | TASK-126 |
| TASK-128 | Create `components/profile/ProfileCard.tsx`: avatar (initials-based), name, email, member since date | | | TASK-126 |
| TASK-129 | Create settings list with navigation items: Edit Profile, Change Password, Notifications, Security, Help, Logout | | | TASK-126 |
| TASK-130 | Create `app/(tabs)/profile/edit.tsx` for profile editing: name field (editable), email field (read-only) | | | TASK-126 |
| TASK-131 | Create `app/(tabs)/profile/change-password.tsx` for password change | | | TASK-126 |
| TASK-132 | Implement password change form: current password, new password, confirm password with validation | | | TASK-131 |
| TASK-133 | Create `app/(tabs)/profile/settings.tsx` for app settings | | | TASK-126 |
| TASK-134 | Add biometric authentication toggle: enable/disable Face ID/Touch ID for app unlock | | | TASK-133 |
| TASK-135 | Add notification preferences toggles: Order Executed, Stop-Loss Hit, Strategy Errors | | | TASK-133 |
| TASK-136 | Add dark mode toggle (if implementing theme support) | | | TASK-133 |
| TASK-137 | Create logout button with confirmation: "Are you sure you want to logout?" | | | TASK-126 |
| TASK-138 | Display app version and build number at bottom of settings | | | TASK-133 |
| TASK-139 | Add links section: Privacy Policy, Terms of Service, Support (opens external URLs) | | | TASK-126 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/app/(tabs)/profile/index.tsx` | Create | Profile main screen |
| `mobile/app/(tabs)/profile/_layout.tsx` | Create | Profile stack navigator |
| `mobile/app/(tabs)/profile/edit.tsx` | Create | Edit profile screen |
| `mobile/app/(tabs)/profile/change-password.tsx` | Create | Password change screen |
| `mobile/app/(tabs)/profile/settings.tsx` | Create | App settings screen |
| `mobile/components/profile/ProfileCard.tsx` | Create | User profile card with avatar |
| `mobile/components/profile/SettingsItem.tsx` | Create | Settings menu item component |
| `mobile/components/profile/SettingsSection.tsx` | Create | Settings section with header |
| `mobile/store/settingsStore.ts` | Create | User preferences state |
| `mobile/schemas/passwordSchema.ts` | Create | Password change validation |

---

## 4. Acceptance Criteria

- [ ] Profile screen displays user info
- [ ] Profile card shows avatar, name, email
- [ ] Settings menu navigates correctly
- [ ] Edit profile allows name change
- [ ] Email is read-only
- [ ] Password change validates correctly
- [ ] Biometric toggle works (on supported devices)
- [ ] Notification preferences save correctly
- [ ] Logout clears session and navigates to login
- [ ] App version displays correctly
- [ ] External links open in browser

---

## 5. Technical Notes

### Profile Screen Structure

```typescript
// app/(tabs)/profile/index.tsx
import { useAuthStore } from '@/store/authStore';
import { useRouter } from 'expo-router';

export default function ProfileScreen() {
  const { user, logout } = useAuthStore();
  const router = useRouter();

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Logout', 
          style: 'destructive', 
          onPress: async () => {
            await logout();
            router.replace('/login');
          }
        },
      ]
    );
  };

  return (
    <ScrollView style={styles.container}>
      <ProfileCard user={user} />
      
      <SettingsSection title="Account">
        <SettingsItem
          icon="person-outline"
          label="Edit Profile"
          onPress={() => router.push('/profile/edit')}
        />
        <SettingsItem
          icon="key-outline"
          label="Change Password"
          onPress={() => router.push('/profile/change-password')}
        />
      </SettingsSection>

      <SettingsSection title="Preferences">
        <SettingsItem
          icon="settings-outline"
          label="Settings"
          onPress={() => router.push('/profile/settings')}
        />
      </SettingsSection>

      <SettingsSection title="Support">
        <SettingsItem
          icon="document-text-outline"
          label="Privacy Policy"
          onPress={() => Linking.openURL('https://algotrading.com/privacy')}
        />
        <SettingsItem
          icon="document-outline"
          label="Terms of Service"
          onPress={() => Linking.openURL('https://algotrading.com/terms')}
        />
        <SettingsItem
          icon="help-circle-outline"
          label="Help & Support"
          onPress={() => Linking.openURL('https://algotrading.com/support')}
        />
      </SettingsSection>

      <SettingsItem
        icon="log-out-outline"
        label="Logout"
        onPress={handleLogout}
        destructive
      />

      <Text style={styles.version}>
        Version {Constants.expoConfig?.version} ({Constants.expoConfig?.extra?.buildNumber})
      </Text>
    </ScrollView>
  );
}
```

### Profile Card Component

```typescript
// components/profile/ProfileCard.tsx
function getInitials(name: string): string {
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export function ProfileCard({ user }) {
  const initials = getInitials(user?.name || 'User');
  
  return (
    <View style={styles.card}>
      <View style={styles.avatar}>
        <Text style={styles.initials}>{initials}</Text>
      </View>
      <Text style={styles.name}>{user?.name}</Text>
      <Text style={styles.email}>{user?.email}</Text>
      <Text style={styles.memberSince}>
        Member since {formatDate(user?.created_at)}
      </Text>
    </View>
  );
}
```

### Settings Store

```typescript
// store/settingsStore.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface SettingsState {
  biometricEnabled: boolean;
  notifications: {
    orderExecuted: boolean;
    stopLossHit: boolean;
    strategyErrors: boolean;
  };
  darkMode: boolean;
  setBiometricEnabled: (enabled: boolean) => void;
  setNotificationPref: (key: string, enabled: boolean) => void;
  setDarkMode: (enabled: boolean) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      biometricEnabled: false,
      notifications: {
        orderExecuted: true,
        stopLossHit: true,
        strategyErrors: true,
      },
      darkMode: false,
      setBiometricEnabled: (enabled) => set({ biometricEnabled: enabled }),
      setNotificationPref: (key, enabled) =>
        set((state) => ({
          notifications: { ...state.notifications, [key]: enabled },
        })),
      setDarkMode: (enabled) => set({ darkMode: enabled }),
    }),
    {
      name: 'settings-storage',
      storage: createJSONStorage(() => AsyncStorage),
    }
  )
);
```

---

## 6. Success Criteria

✅ Phase 11 is complete when:

- Profile screen displays user information
- Profile editing works correctly
- Password change validates and submits
- Biometric toggle functions on supported devices
- Notification preferences persist
- Logout clears all state and redirects
- App version displays correctly
- External links open properly
