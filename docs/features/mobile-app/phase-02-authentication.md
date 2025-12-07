---
goal: Implement secure authentication with JWT storage and biometric support
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, authentication, jwt, biometric, security]
---

# Phase 2: Authentication Flow

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement secure authentication flow with login, registration, logout, JWT token storage in SecureStore, biometric authentication support, and session timeout handling.

---

## 1. Requirements & Constraints

- **SEC-001**: JWT tokens stored in SecureStore (encrypted storage)
- **SEC-002**: Biometric authentication for app access (optional)
- **SEC-003**: Session timeout after 30 minutes
- **SEC-005**: No sensitive data in AsyncStorage
- **UXR-004**: Clear visual feedback for all actions
- **UXR-006**: Loading states for all network operations

---

## 2. Implementation Tasks

### GOAL-002: Implement secure authentication with JWT storage and biometric support

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-015 | Create `api/auth.ts` with `login(email, password)`, `register(email, password, name)`, `logout()`, `refreshToken()` functions using Axios | | | Phase 1 |
| TASK-016 | Create `store/authStore.ts` with Zustand: `user`, `token`, `isAuthenticated`, `isLoading`, `login()`, `logout()`, `setUser()` | | | TASK-015 |
| TASK-017 | Implement SecureStore wrapper in `utils/secureStorage.ts`: `setToken()`, `getToken()`, `removeToken()`, `setRefreshToken()`, `getRefreshToken()` | | | Phase 1 |
| TASK-018 | Create `app/(auth)/login.tsx` login screen with email input, password input, login button, register link, forgot password link | | | TASK-016 |
| TASK-019 | Create `components/auth/LoginForm.tsx` with react-hook-form, Zod schema: email (valid email), password (min 8 chars) | | | TASK-018 |
| TASK-020 | Create `app/(auth)/register.tsx` registration screen with name, email, password, confirm password fields | | | TASK-016 |
| TASK-021 | Create `components/auth/RegisterForm.tsx` with Zod validation: name (required), email (valid), password (min 8, 1 uppercase, 1 number), confirmPassword (match) | | | TASK-020 |
| TASK-022 | Implement auto-login on app start: check SecureStore for token, validate with backend, update authStore if valid | | | TASK-017 |
| TASK-023 | Create logout functionality: clear SecureStore tokens, reset authStore, navigate to login screen | | | TASK-017 |
| TASK-024 | Install biometric: `expo install expo-local-authentication` | | | Phase 1 |
| TASK-025 | Create biometric unlock in `utils/biometric.ts`: `isBiometricAvailable()`, `authenticateWithBiometric()`, use Face ID/Touch ID/Fingerprint | | | TASK-024 |
| TASK-026 | Implement session timeout: track last activity timestamp, logout after 30 minutes inactivity, use AppState listener | | | TASK-016 |
| TASK-027 | Create `app/(auth)/forgot-password.tsx` with email input, send reset link button, success message | | | Phase 1 |
| TASK-028 | Add loading states: show spinner during API calls, disable buttons, show error toasts on failure | | | TASK-019, TASK-021 |
| TASK-029 | Create auth layout `app/(auth)/_layout.tsx` with Stack navigator, shared header style, keyboard avoiding view | | | Phase 1 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/api/auth.ts` | Create | Auth API functions: login, register, logout, refreshToken |
| `mobile/store/authStore.ts` | Create | Zustand store for auth state management |
| `mobile/utils/secureStorage.ts` | Create | SecureStore wrapper for JWT token persistence |
| `mobile/utils/biometric.ts` | Create | Biometric authentication utilities |
| `mobile/app/(auth)/_layout.tsx` | Create | Auth screens stack layout |
| `mobile/app/(auth)/login.tsx` | Create | Login screen |
| `mobile/app/(auth)/register.tsx` | Create | Registration screen |
| `mobile/app/(auth)/forgot-password.tsx` | Create | Password reset request screen |
| `mobile/components/auth/LoginForm.tsx` | Create | Login form with validation |
| `mobile/components/auth/RegisterForm.tsx` | Create | Registration form with validation |
| `mobile/types/auth.ts` | Create | Auth-related TypeScript types |

---

## 4. Acceptance Criteria

- [ ] User can login with email and password
- [ ] Invalid credentials show error message
- [ ] User can register with name, email, password
- [ ] Registration validation shows inline errors
- [ ] JWT token is stored securely in SecureStore (not AsyncStorage)
- [ ] App auto-logs in if valid token exists
- [ ] Logout clears all stored tokens and redirects to login
- [ ] Biometric authentication works on supported devices
- [ ] Session times out after 30 minutes of inactivity
- [ ] Loading states shown during API calls
- [ ] Forgot password sends reset link

---

## 5. Technical Notes

### SecureStore Usage

```typescript
// utils/secureStorage.ts
import * as SecureStore from 'expo-secure-store';

const TOKEN_KEY = 'jwt_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

export const setToken = async (token: string) => {
  await SecureStore.setItemAsync(TOKEN_KEY, token);
};

export const getToken = async (): Promise<string | null> => {
  return await SecureStore.getItemAsync(TOKEN_KEY);
};

export const removeToken = async () => {
  await SecureStore.deleteItemAsync(TOKEN_KEY);
};
```

### Zustand Auth Store

```typescript
// store/authStore.ts
import { create } from 'zustand';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  // ... implementation
}));
```

### Biometric Authentication

```typescript
// utils/biometric.ts
import * as LocalAuthentication from 'expo-local-authentication';

export const isBiometricAvailable = async (): Promise<boolean> => {
  const compatible = await LocalAuthentication.hasHardwareAsync();
  const enrolled = await LocalAuthentication.isEnrolledAsync();
  return compatible && enrolled;
};

export const authenticateWithBiometric = async (): Promise<boolean> => {
  const result = await LocalAuthentication.authenticateAsync({
    promptMessage: 'Authenticate to access Algo Trading',
    fallbackLabel: 'Use Password',
  });
  return result.success;
};
```

### Zod Login Schema

```typescript
import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

export type LoginFormData = z.infer<typeof loginSchema>;
```

---

## 6. Success Criteria

✅ Phase 2 is complete when:

- Login and registration flows work end-to-end
- JWT tokens are securely stored in SecureStore
- Auto-login works on app restart
- Biometric authentication is available on supported devices
- Session timeout triggers after 30 minutes
- All forms have proper validation and error handling
- Loading states provide feedback during API calls
