---
goal: Initialize Expo project with TypeScript and configure development environment
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, expo, typescript, setup, configuration]
---

# Phase 1: Project Setup & Configuration

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Initialize the React Native/Expo project with TypeScript, install core dependencies, and configure the development environment for iOS and Android.

---

## 1. Requirements & Constraints

- **REQ-001**: React Native with Expo managed workflow
- **REQ-002**: Support iOS 14+ and Android API 24+ (Android 7.0+)
- **CON-001**: Expo managed workflow limitations for native modules
- **PAT-001**: Expo Router for file-based navigation
- **PAT-002**: Zustand for state management
- **PAT-003**: React Hook Form for form handling

---

## 2. Implementation Tasks

### GOAL-001: Initialize Expo project with TypeScript and configure development environment

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-001 | Create Expo project: `npx create-expo-app@latest algo-trading-mobile --template expo-template-blank-typescript` | | | None |
| TASK-002 | Configure `app.json` with app name "Algo Trading", bundle ID `com.algotrading.mobile`, package name, version 1.0.0, splash screen, icons | | | TASK-001 |
| TASK-003 | Install navigation: `expo install expo-router react-native-screens react-native-safe-area-context react-native-gesture-handler` | | | TASK-001 |
| TASK-004 | Install core dependencies: `npm install zustand @tanstack/react-query axios` | | | TASK-001 |
| TASK-005 | Install form libraries: `npm install react-hook-form @hookform/resolvers zod` | | | TASK-001 |
| TASK-006 | Install secure storage: `expo install expo-secure-store` | | | TASK-001 |
| TASK-007 | Install UI components: `npm install react-native-paper react-native-vector-icons` | | | TASK-001 |
| TASK-008 | Install date/time picker: `expo install @react-native-community/datetimepicker` | | | TASK-001 |
| TASK-009 | Configure `tsconfig.json` with path aliases: `@/components/*`, `@/screens/*`, `@/store/*`, `@/api/*`, `@/hooks/*`, `@/utils/*`, `@/types/*` | | | TASK-001 |
| TASK-010 | Create `.env` file with `API_BASE_URL` and install `expo-constants` for environment variables | | | TASK-001 |
| TASK-011 | Set up ESLint config with `@typescript-eslint`, Prettier with `.prettierrc`, and integrate with VS Code | | | TASK-001 |
| TASK-012 | Create project folder structure: `app/`, `components/`, `api/`, `store/`, `hooks/`, `utils/`, `types/`, `constants/` | | | TASK-001 |
| TASK-013 | Configure app icons (1024x1024) and splash screen using `expo-splash-screen`, update `app.json` with asset paths | | | TASK-002 |
| TASK-014 | Set up iOS Simulator and Android Emulator, test `expo start` runs successfully on both platforms | | | TASK-003 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/app.json` | Create | Expo app configuration with name, slug, version, orientation, icons, splash, ios/android configs |
| `mobile/tsconfig.json` | Modify | Add path aliases for @/components, @/api, @/store, @/hooks, @/utils, @/types |
| `mobile/babel.config.js` | Modify | Add module-resolver plugin for path aliases |
| `mobile/package.json` | Modify | Add all dependencies and scripts |
| `mobile/.env` | Create | Environment variables: API_BASE_URL |
| `mobile/.eslintrc.js` | Create | ESLint configuration for TypeScript/React Native |
| `mobile/.prettierrc` | Create | Prettier configuration |
| `mobile/app/_layout.tsx` | Create | Root layout placeholder |
| `mobile/constants/theme.ts` | Create | Theme colors, spacing, typography constants |

---

## 4. Acceptance Criteria

- [ ] Expo project initializes without errors
- [ ] `expo start` launches Metro bundler successfully
- [ ] App runs on iOS Simulator (iOS 14+)
- [ ] App runs on Android Emulator (API 24+)
- [ ] Path aliases resolve correctly (test import from @/constants/theme)
- [ ] TypeScript strict mode enabled with no compilation errors
- [ ] ESLint and Prettier run without errors
- [ ] All dependencies installed and compatible

---

## 5. Technical Notes

### Expo Router Setup

Expo Router requires specific folder structure in `app/` directory:

```
app/
├── _layout.tsx          # Root layout
├── index.tsx            # Home screen (/)
├── (auth)/              # Auth group
│   ├── _layout.tsx
│   ├── login.tsx
│   └── register.tsx
└── (tabs)/              # Tab group
    ├── _layout.tsx
    ├── index.tsx        # Home tab
    ├── strategies/
    ├── broker/
    └── profile/
```

### Path Aliases Configuration

In `tsconfig.json`:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

In `babel.config.js`:

```javascript
module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      ['module-resolver', {
        root: ['.'],
        alias: { '@': '.' }
      }]
    ]
  };
};
```

---

## 6. Success Criteria

✅ Phase 1 is complete when:

- Expo project is initialized with TypeScript
- All core dependencies are installed
- Path aliases are configured and working
- Development environment runs on iOS and Android
- Code quality tools (ESLint, Prettier) are configured
- Folder structure follows Expo Router conventions
