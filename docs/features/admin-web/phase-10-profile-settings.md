---
goal: Implement user profile management and application settings
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [admin-web, nextjs, profile, settings, preferences]
---

# Phase 10: User Profile & Settings

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement user profile management including profile editing, password change, notification preferences, and application settings.

---

## 1. Requirements & Constraints

### Technical Requirements

- **REQ-001**: Profile update with form validation
- **REQ-002**: Password change with current password verification
- **REQ-003**: Theme preference persistence
- **REQ-004**: Session management interface

### Preferences

- **PRF-001**: Notification preferences (email, push)
- **PRF-002**: Timezone selection (default IST)
- **PRF-003**: Theme preference (Light/Dark/System)

### Constraints

- **CON-001**: Password must meet security requirements
- **CON-002**: Email change requires verification
- **CON-003**: Some settings require page reload

---

## 2. Implementation Tasks

### GOAL-010: Implement user profile management and application settings

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-115 | Create `app/(dashboard)/profile/page.tsx` for user profile | | |
| TASK-116 | Create `components/profile/ProfileForm.tsx` for name, email updates | | |
| TASK-117 | Create `app/(dashboard)/profile/security/page.tsx` for password change | | |
| TASK-118 | Create `components/profile/ChangePasswordForm.tsx` with validation | | |
| TASK-119 | Create `app/(dashboard)/settings/page.tsx` for app settings | | |
| TASK-120 | Implement notification preferences toggles | | |
| TASK-121 | Implement timezone selection (default IST) | | |
| TASK-122 | Add theme preference (Light/Dark/System) | | |
| TASK-123 | Create session management - view active sessions, logout all | | |
| TASK-124 | Add API key management for programmatic access (future) | | |

---

## 3. Dependencies

- **DEP-001**: React Hook Form + Zod
- **DEP-002**: next-themes for theme management
- **DEP-003**: date-fns-tz for timezone handling
- **DEP-004**: Backend profile API endpoints

---

## 4. Files

### Profile Pages

- **FILE-001**: `admin-web/app/(dashboard)/profile/page.tsx` - Profile overview
- **FILE-002**: `admin-web/app/(dashboard)/profile/edit/page.tsx` - Edit profile
- **FILE-003**: `admin-web/app/(dashboard)/profile/security/page.tsx` - Security settings
- **FILE-004**: `admin-web/app/(dashboard)/profile/sessions/page.tsx` - Active sessions

### Settings Pages

- **FILE-005**: `admin-web/app/(dashboard)/settings/page.tsx` - App settings
- **FILE-006**: `admin-web/app/(dashboard)/settings/notifications/page.tsx` - Notification prefs

### Profile Components

- **FILE-007**: `admin-web/components/profile/ProfileForm.tsx` - Profile edit form
- **FILE-008**: `admin-web/components/profile/ChangePasswordForm.tsx` - Password change
- **FILE-009**: `admin-web/components/profile/AvatarUpload.tsx` - Avatar upload
- **FILE-010**: `admin-web/components/profile/ProfileCard.tsx` - Profile display

### Settings Components

- **FILE-011**: `admin-web/components/settings/NotificationSettings.tsx` - Notification toggles
- **FILE-012**: `admin-web/components/settings/TimezoneSelect.tsx` - Timezone selector
- **FILE-013**: `admin-web/components/settings/ThemeSettings.tsx` - Theme selector
- **FILE-014**: `admin-web/components/settings/SessionList.tsx` - Active sessions
- **FILE-015**: `admin-web/components/settings/ApiKeyManager.tsx` - API keys (future)

---

## Settings Structure

```text
Profile
├── Overview (avatar, name, email, member since)
├── Edit Profile
│   ├── Name
│   ├── Email (with verification)
│   └── Avatar
└── Security
    ├── Change Password
    └── Active Sessions

Settings
├── Notifications
│   ├── Email Notifications (on/off)
│   ├── Order Executed
│   ├── Stop-Loss Triggered
│   └── Strategy Errors
├── Preferences
│   ├── Timezone (IST default)
│   └── Theme (Light/Dark/System)
└── API Keys (Future)
```

---

## Success Criteria

✅ Phase 10 is complete when:

- [ ] Profile page with user information
- [ ] Profile edit form with validation
- [ ] Password change with current password verification
- [ ] Notification preferences (email toggles)
- [ ] Timezone selection dropdown
- [ ] Theme preference (Light/Dark/System)
- [ ] Active sessions list
- [ ] Logout all sessions functionality
- [ ] Settings persistence across sessions

---

## Next Phase

[Phase 11: Admin - User Management →](./phase-11-admin-users.md)
