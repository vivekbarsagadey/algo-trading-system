---
goal: Implement testing infrastructure and write tests
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, testing, jest, detox, e2e, unit-tests]
---

# Phase 19: Testing

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement comprehensive testing infrastructure including unit tests, component tests, and end-to-end tests with proper mocking and CI integration.

---

## 1. Requirements & Constraints

- Jest for unit and component testing
- Detox for E2E testing (optional)
- Minimum 70% code coverage target

---

## 2. Implementation Tasks

### GOAL-019: Implement testing infrastructure and write tests

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-205 | Configure Jest for React Native testing: jest.config.js with react-native preset, transform, moduleNameMapper | | | Phase 1 |
| TASK-206 | Install @testing-library/react-native for component testing: `npm install -D @testing-library/react-native` | | | TASK-205 |
| TASK-207 | Create test utilities in `__tests__/utils/`: mock providers, render helpers, test data factories | | | TASK-206 |
| TASK-208 | Write unit tests for authStore: login, logout, checkAuth, state transitions | | | Phase 17 |
| TASK-209 | Write unit tests for strategyStore: CRUD operations, filters, selectors | | | Phase 17 |
| TASK-210 | Write component tests for LoginForm: validation, submission, error display | | | Phase 2 |
| TASK-211 | Write component tests for StrategyForm: all 5 inputs, validation, submission | | | Phase 7 |
| TASK-212 | Write component tests for StrategyCard: display, press handling, status badge | | | Phase 6 |
| TASK-213 | Configure Detox for E2E testing (optional): detox.config.js for iOS and Android | | | TASK-205 |
| TASK-214 | Write E2E test for login flow: open app, enter credentials, submit, verify dashboard | | | TASK-213 |
| TASK-215 | Write E2E test for strategy creation flow: navigate, fill form, submit, verify in list | | | TASK-213 |
| TASK-216 | Write E2E test for broker connection flow: navigate, select broker, enter credentials, validate | | | TASK-213 |
| TASK-217 | Set up CI pipeline with test execution: GitHub Actions workflow for running tests | | | TASK-205 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/jest.config.js` | Create | Jest configuration |
| `mobile/jest.setup.js` | Create | Jest setup and mocks |
| `mobile/__tests__/utils/testUtils.tsx` | Create | Test render helpers |
| `mobile/__tests__/utils/mocks.ts` | Create | Mock implementations |
| `mobile/__tests__/utils/factories.ts` | Create | Test data factories |
| `mobile/__tests__/stores/authStore.test.ts` | Create | Auth store tests |
| `mobile/__tests__/stores/strategyStore.test.ts` | Create | Strategy store tests |
| `mobile/__tests__/components/LoginForm.test.tsx` | Create | Login form tests |
| `mobile/__tests__/components/StrategyForm.test.tsx` | Create | Strategy form tests |
| `mobile/__tests__/components/StrategyCard.test.tsx` | Create | Strategy card tests |
| `mobile/e2e/login.test.ts` | Create | E2E login test |
| `mobile/e2e/createStrategy.test.ts` | Create | E2E strategy test |
| `mobile/.github/workflows/test.yml` | Create | CI workflow |

---

## 4. Acceptance Criteria

- [ ] Jest configured and running
- [ ] Test utilities created and working
- [ ] Auth store tests pass
- [ ] Strategy store tests pass
- [ ] LoginForm component tests pass
- [ ] StrategyForm component tests pass
- [ ] StrategyCard component tests pass
- [ ] E2E tests run successfully (if configured)
- [ ] CI pipeline runs tests on push

---

## 5. Technical Notes

### Jest Configuration

```javascript
// jest.config.js
module.exports = {
  preset: 'jest-expo',
  transformIgnorePatterns: [
    'node_modules/(?!((jest-)?react-native|@react-native(-community)?)|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|@unimodules/.*|unimodules|sentry-expo|native-base|react-native-svg)',
  ],
  setupFilesAfterEnv: ['./jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  collectCoverageFrom: [
    'app/**/*.{ts,tsx}',
    'components/**/*.{ts,tsx}',
    'store/**/*.{ts,tsx}',
    'hooks/**/*.{ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },
};
```

### Jest Setup

```javascript
// jest.setup.js
import '@testing-library/jest-native/extend-expect';

// Mock expo-secure-store
jest.mock('expo-secure-store', () => ({
  setItemAsync: jest.fn(),
  getItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}));

// Mock expo-router
jest.mock('expo-router', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn(),
  }),
  useLocalSearchParams: () => ({}),
  Link: 'Link',
}));

// Mock react-native-toast-message
jest.mock('react-native-toast-message', () => ({
  show: jest.fn(),
  hide: jest.fn(),
}));

// Silence warnings during tests
jest.spyOn(console, 'warn').mockImplementation(() => {});
```

### Test Utilities

```typescript
// __tests__/utils/testUtils.tsx
import React from 'react';
import { render, RenderOptions } from '@testing-library/react-native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

interface AllTheProvidersProps {
  children: React.ReactNode;
}

const AllTheProviders: React.FC<AllTheProvidersProps> = ({ children }) => {
  const queryClient = createTestQueryClient();
  
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

export * from '@testing-library/react-native';
export { customRender as render };
```

### Test Data Factories

```typescript
// __tests__/utils/factories.ts
import { Strategy, User } from '@/types';

export function createMockUser(overrides?: Partial<User>): User {
  return {
    id: 'usr_123',
    email: 'test@example.com',
    name: 'Test User',
    role: 'User',
    created_at: '2024-01-01T00:00:00Z',
    ...overrides,
  };
}

export function createMockStrategy(overrides?: Partial<Strategy>): Strategy {
  return {
    id: 'str_123',
    user_id: 'usr_123',
    symbol: 'RELIANCE',
    buy_time: '09:30',
    sell_time: '15:00',
    stop_loss: 2500,
    quantity: 10,
    status: 'STOPPED',
    position: 'NONE',
    last_action: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    ...overrides,
  };
}
```

### Auth Store Tests

```typescript
// __tests__/stores/authStore.test.ts
import { act, renderHook } from '@testing-library/react-native';
import { useAuthStore } from '@/store/authStore';
import * as SecureStore from 'expo-secure-store';
import * as authApi from '@/api/auth';

jest.mock('@/api/auth');

describe('authStore', () => {
  beforeEach(() => {
    // Reset store state
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  it('should login successfully', async () => {
    const mockUser = { id: 'usr_123', email: 'test@example.com', name: 'Test' };
    (authApi.login as jest.Mock).mockResolvedValue({
      user: mockUser,
      access_token: 'token123',
      refresh_token: 'refresh123',
    });

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).toEqual(mockUser);
    expect(SecureStore.setItemAsync).toHaveBeenCalled();
  });

  it('should logout and clear state', async () => {
    // Set initial authenticated state
    useAuthStore.setState({
      user: { id: 'usr_123', email: 'test@example.com', name: 'Test' },
      token: 'token123',
      isAuthenticated: true,
    });

    const { result } = renderHook(() => useAuthStore());

    await act(async () => {
      await result.current.logout();
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
    expect(SecureStore.deleteItemAsync).toHaveBeenCalled();
  });
});
```

### Component Test Example

```typescript
// __tests__/components/LoginForm.test.tsx
import { render, screen, fireEvent, waitFor } from '../utils/testUtils';
import { LoginForm } from '@/components/auth/LoginForm';

describe('LoginForm', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  it('should render all form fields', () => {
    render(<LoginForm onSubmit={mockOnSubmit} isLoading={false} />);

    expect(screen.getByPlaceholderText(/email/i)).toBeTruthy();
    expect(screen.getByPlaceholderText(/password/i)).toBeTruthy();
    expect(screen.getByRole('button', { name: /login/i })).toBeTruthy();
  });

  it('should show validation errors for empty fields', async () => {
    render(<LoginForm onSubmit={mockOnSubmit} isLoading={false} />);

    fireEvent.press(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeTruthy();
    });
  });

  it('should call onSubmit with valid data', async () => {
    render(<LoginForm onSubmit={mockOnSubmit} isLoading={false} />);

    fireEvent.changeText(screen.getByPlaceholderText(/email/i), 'test@example.com');
    fireEvent.changeText(screen.getByPlaceholderText(/password/i), 'password123');
    fireEvent.press(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });
  });
});
```

---

## 6. Success Criteria

✅ Phase 19 is complete when:

- Jest configured and running
- Test utilities and mocks created
- Store tests achieve 80%+ coverage
- Component tests cover key interactions
- E2E tests cover critical flows (if configured)
- CI pipeline runs tests automatically
- Code coverage meets 70% threshold
