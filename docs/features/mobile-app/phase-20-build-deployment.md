---
goal: Configure build and deployment pipelines for iOS and Android
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, deployment, eas, build, app-store, play-store]
---

# Phase 20: Build & Deployment

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Configure EAS Build for iOS and Android builds, app store submission, OTA updates, and monitoring/analytics integration.

---

## 1. Requirements & Constraints

- **REQ-002**: Support iOS 14+ and Android API 24+
- EAS Build for cloud builds
- OTA updates for quick fixes
- Crash reporting for production

---

## 2. Implementation Tasks

### GOAL-020: Configure build and deployment pipelines for iOS and Android

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-218 | Configure EAS Build: run `eas build:configure`, create initial eas.json | | | Phase 1 |
| TASK-219 | Create development build profiles in eas.json: development, preview for internal testing | | | TASK-218 |
| TASK-220 | Create production build profiles: production for App Store/Play Store | | | TASK-218 |
| TASK-221 | Configure iOS app signing: create App ID in Apple Developer, generate certificates and provisioning profiles | | | TASK-218 |
| TASK-222 | Configure Android app signing: generate keystore, configure signing in eas.json | | | TASK-218 |
| TASK-223 | Set up EAS Submit for App Store and Play Store deployment | | | TASK-220 |
| TASK-224 | Configure OTA updates with EAS Update for quick bug fixes without store review | | | TASK-218 |
| TASK-225 | Create staging environment configuration: separate API URLs, bundle IDs | | | TASK-219 |
| TASK-226 | Write release documentation and changelog template | | | TASK-220 |
| TASK-227 | Set up crash reporting with Sentry: configure release tracking, source maps | | | TASK-220 |
| TASK-228 | Configure analytics with Mixpanel or Amplitude for user behavior tracking | | | TASK-220 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/eas.json` | Create | EAS Build configuration |
| `mobile/app.json` | Modify | Add production config |
| `mobile/app.config.ts` | Create | Dynamic app configuration |
| `mobile/credentials.json` | Create | EAS credentials config (gitignored) |
| `mobile/CHANGELOG.md` | Create | Release changelog |
| `mobile/docs/RELEASE.md` | Create | Release documentation |
| `mobile/.github/workflows/build.yml` | Create | CI/CD workflow |

---

## 4. Acceptance Criteria

- [ ] EAS Build configured successfully
- [ ] Development builds work on iOS and Android
- [ ] Production builds create signed apps
- [ ] iOS certificates and profiles configured
- [ ] Android keystore configured
- [ ] EAS Submit works for app stores
- [ ] OTA updates work correctly
- [ ] Staging environment separated from production
- [ ] Sentry crash reporting configured
- [ ] Analytics tracking implemented

---

## 5. Technical Notes

### EAS Configuration

```json
// eas.json
{
  "cli": {
    "version": ">= 5.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": {
        "resourceClass": "m1-medium"
      },
      "android": {
        "buildType": "apk"
      },
      "env": {
        "API_URL": "http://localhost:8000",
        "ENVIRONMENT": "development"
      }
    },
    "preview": {
      "distribution": "internal",
      "ios": {
        "resourceClass": "m1-medium"
      },
      "android": {
        "buildType": "apk"
      },
      "env": {
        "API_URL": "https://staging-api.algotrading.com",
        "ENVIRONMENT": "staging"
      }
    },
    "production": {
      "distribution": "store",
      "ios": {
        "resourceClass": "m1-medium"
      },
      "android": {
        "buildType": "app-bundle"
      },
      "env": {
        "API_URL": "https://api.algotrading.com",
        "ENVIRONMENT": "production"
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "developer@algotrading.com",
        "ascAppId": "1234567890",
        "appleTeamId": "XXXXXXXXXX"
      },
      "android": {
        "serviceAccountKeyPath": "./google-services.json",
        "track": "internal"
      }
    }
  }
}
```

### Dynamic App Configuration

```typescript
// app.config.ts
import { ExpoConfig, ConfigContext } from 'expo/config';

export default ({ config }: ConfigContext): ExpoConfig => {
  const environment = process.env.ENVIRONMENT || 'development';
  
  const envConfig = {
    development: {
      apiUrl: 'http://localhost:8000',
      bundleId: 'com.algotrading.mobile.dev',
      name: 'Algo Trading (Dev)',
    },
    staging: {
      apiUrl: 'https://staging-api.algotrading.com',
      bundleId: 'com.algotrading.mobile.staging',
      name: 'Algo Trading (Staging)',
    },
    production: {
      apiUrl: 'https://api.algotrading.com',
      bundleId: 'com.algotrading.mobile',
      name: 'Algo Trading',
    },
  }[environment];

  return {
    ...config,
    name: envConfig.name,
    slug: 'algo-trading-mobile',
    version: '1.0.0',
    orientation: 'portrait',
    icon: './assets/icon.png',
    userInterfaceStyle: 'automatic',
    splash: {
      image: './assets/splash.png',
      resizeMode: 'contain',
      backgroundColor: '#ffffff',
    },
    assetBundlePatterns: ['**/*'],
    ios: {
      supportsTablet: false,
      bundleIdentifier: envConfig.bundleId,
      buildNumber: '1',
      config: {
        usesNonExemptEncryption: false,
      },
    },
    android: {
      adaptiveIcon: {
        foregroundImage: './assets/adaptive-icon.png',
        backgroundColor: '#ffffff',
      },
      package: envConfig.bundleId.replace(/\./g, '_'),
      versionCode: 1,
    },
    extra: {
      apiUrl: envConfig.apiUrl,
      environment,
      eas: {
        projectId: 'your-project-id',
      },
    },
    updates: {
      url: 'https://u.expo.dev/your-project-id',
    },
    runtimeVersion: {
      policy: 'sdkVersion',
    },
    plugins: [
      'expo-router',
      'expo-secure-store',
      [
        '@sentry/react-native/expo',
        {
          organization: 'your-org',
          project: 'algo-trading-mobile',
        },
      ],
    ],
  };
};
```

### CI/CD Workflow

```yaml
# .github/workflows/build.yml
name: Build and Deploy

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci
      - run: npm test -- --coverage
      - uses: codecov/codecov-action@v3

  build-preview:
    needs: test
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: npm ci
      - run: eas build --platform all --profile preview --non-interactive

  build-production:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: npm ci
      - run: eas build --platform all --profile production --non-interactive
```

### Sentry Configuration

```typescript
// services/sentry.ts
import * as Sentry from '@sentry/react-native';
import Constants from 'expo-constants';

export function initializeSentry() {
  if (Constants.expoConfig?.extra?.environment !== 'development') {
    Sentry.init({
      dsn: 'YOUR_SENTRY_DSN',
      environment: Constants.expoConfig?.extra?.environment,
      release: `algo-trading-mobile@${Constants.expoConfig?.version}`,
      dist: Constants.expoConfig?.ios?.buildNumber || Constants.expoConfig?.android?.versionCode?.toString(),
      tracesSampleRate: 0.2,
      enableAutoSessionTracking: true,
      attachScreenshot: true,
    });
  }
}

export function captureException(error: Error, context?: Record<string, any>) {
  Sentry.captureException(error, { extra: context });
}

export function setUser(user: { id: string; email: string }) {
  Sentry.setUser(user);
}

export function clearUser() {
  Sentry.setUser(null);
}
```

### Release Documentation Template

```markdown
<!-- docs/RELEASE.md -->
# Release Process

## Version Numbering
- Major.Minor.Patch (e.g., 1.2.3)
- iOS: Use `buildNumber` for each build
- Android: Use `versionCode` (increment each build)

## Release Checklist

### Pre-Release
- [ ] All tests pass
- [ ] Code reviewed and approved
- [ ] Changelog updated
- [ ] Version numbers updated

### Build
- [ ] Run `eas build --platform all --profile production`
- [ ] Test production build on devices

### Submit
- [ ] Run `eas submit --platform ios`
- [ ] Run `eas submit --platform android`

### Post-Release
- [ ] Monitor Sentry for crashes
- [ ] Monitor analytics for issues
- [ ] Tag release in git
```

---

## 6. Success Criteria

✅ Phase 20 is complete when:

- EAS Build configured for all profiles
- Development builds work locally
- Production builds create signed apps
- App store submission configured
- OTA updates configured
- Staging environment separated
- Sentry crash reporting active
- Analytics tracking implemented
- CI/CD pipeline automated
- Release documentation complete
