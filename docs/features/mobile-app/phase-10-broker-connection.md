---
goal: Implement broker connection and management screens
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Mobile Engineering Team
status: Planned
tags: [mobile, broker, connection, credentials, validation]
---

# Phase 10: Broker Connection

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement broker connection and management screens including broker selection, credentials form, connection validation, status display, and token refresh handling.

---

## 1. Requirements & Constraints

- **SEC-001**: JWT tokens stored in SecureStore (encrypted storage)
- **SEC-005**: No sensitive data in AsyncStorage
- **UXR-004**: Clear visual feedback for all actions

---

## 2. Implementation Tasks

### GOAL-010: Implement broker connection and management screens

| Task | Description | Completed | Date | Dependencies |
|------|-------------|-----------|------|--------------|
| TASK-111 | Create `app/(tabs)/broker/index.tsx` broker management screen with conditional rendering based on connection status | | | Phase 3, Phase 4 |
| TASK-112 | Display connected broker status: broker name, connection health indicator (green/yellow/red), last validated time | | | TASK-111 |
| TASK-113 | Create "No Broker Connected" state: illustration, explanation text, "Connect Broker" CTA button | | | TASK-111 |
| TASK-114 | Create `app/(tabs)/broker/connect.tsx` broker connection screen with step-by-step flow | | | TASK-111 |
| TASK-115 | Create `components/broker/BrokerSelector.tsx`: 2x2 grid of broker options - Zerodha, Dhan, Fyers, Angel One | | | TASK-114 |
| TASK-116 | Display broker logos (stored locally), broker names, tap to select with visual feedback | | | TASK-115 |
| TASK-117 | Create `components/broker/CredentialsForm.tsx` with dynamic fields based on selected broker (API key, secret, access token) | | | TASK-114 |
| TASK-118 | Add "Test Connection" button: validates credentials with backend without saving | | | TASK-117 |
| TASK-119 | Implement credential validation API call: show loading spinner, display success/failure result | | | TASK-118 |
| TASK-120 | Show validation result: green checkmark "Connection successful" or red X with error message | | | TASK-119 |
| TASK-121 | Save credentials only after successful validation: call connect API, store connection status | | | TASK-119 |
| TASK-122 | Create `components/broker/BrokerStatus.tsx`: card showing connected broker, health status, token expiry warning | | | TASK-111 |
| TASK-123 | Add token expiry warning: show banner when token expires within 24 hours, "Refresh Token" prompt | | | TASK-122 |
| TASK-124 | Create disconnect broker functionality: confirmation dialog, call disconnect API, clear local state | | | TASK-111 |
| TASK-125 | Add help/documentation links per broker: open external URL with instructions for getting API credentials | | | TASK-114 |

---

## 3. Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `mobile/app/(tabs)/broker/index.tsx` | Create | Broker management screen |
| `mobile/app/(tabs)/broker/_layout.tsx` | Create | Broker stack navigator |
| `mobile/app/(tabs)/broker/connect.tsx` | Create | Broker connection flow |
| `mobile/components/broker/BrokerSelector.tsx` | Create | Broker selection grid |
| `mobile/components/broker/BrokerCard.tsx` | Create | Individual broker option card |
| `mobile/components/broker/CredentialsForm.tsx` | Create | Dynamic credentials form |
| `mobile/components/broker/BrokerStatus.tsx` | Create | Connected broker status card |
| `mobile/components/broker/TokenExpiryWarning.tsx` | Create | Token expiry warning banner |
| `mobile/components/broker/NoBrokerState.tsx` | Create | Empty state for no connection |
| `mobile/store/brokerStore.ts` | Create | Broker connection state |
| `mobile/assets/images/brokers/` | Create | Broker logo images |
| `mobile/constants/brokers.ts` | Create | Broker configuration constants |

---

## 4. Acceptance Criteria

- [ ] Broker screen shows connected status or empty state
- [ ] Broker selector displays all 4 brokers
- [ ] Selecting broker shows appropriate credentials form
- [ ] Test Connection validates without saving
- [ ] Validation feedback shows success/failure
- [ ] Credentials saved only after validation
- [ ] Connected status shows broker and health
- [ ] Token expiry warning appears appropriately
- [ ] Disconnect works with confirmation
- [ ] Help links open documentation

---

## 5. Technical Notes

### Broker Configuration Constants

```typescript
// constants/brokers.ts
export const BROKERS = {
  zerodha: {
    id: 'zerodha',
    name: 'Zerodha',
    logo: require('@/assets/images/brokers/zerodha.png'),
    helpUrl: 'https://kite.trade/docs/connect/v3/',
    fields: [
      { name: 'api_key', label: 'API Key', type: 'text' },
      { name: 'api_secret', label: 'API Secret', type: 'password' },
      { name: 'access_token', label: 'Access Token', type: 'password' },
    ],
  },
  dhan: {
    id: 'dhan',
    name: 'Dhan',
    logo: require('@/assets/images/brokers/dhan.png'),
    helpUrl: 'https://dhanhq.co/docs/',
    fields: [
      { name: 'client_id', label: 'Client ID', type: 'text' },
      { name: 'access_token', label: 'Access Token', type: 'password' },
    ],
  },
  fyers: {
    id: 'fyers',
    name: 'Fyers',
    logo: require('@/assets/images/brokers/fyers.png'),
    helpUrl: 'https://myapi.fyers.in/docs/',
    fields: [
      { name: 'app_id', label: 'App ID', type: 'text' },
      { name: 'access_token', label: 'Access Token', type: 'password' },
    ],
  },
  angel_one: {
    id: 'angel_one',
    name: 'Angel One',
    logo: require('@/assets/images/brokers/angel-one.png'),
    helpUrl: 'https://smartapi.angelone.in/docs',
    fields: [
      { name: 'api_key', label: 'API Key', type: 'text' },
      { name: 'client_id', label: 'Client ID', type: 'text' },
      { name: 'password', label: 'Password', type: 'password' },
      { name: 'totp_secret', label: 'TOTP Secret', type: 'password' },
    ],
  },
};
```

### Broker Selector Grid

```typescript
// components/broker/BrokerSelector.tsx
import { BROKERS } from '@/constants/brokers';

export function BrokerSelector({ onSelect, selected }) {
  return (
    <View style={styles.grid}>
      {Object.values(BROKERS).map((broker) => (
        <BrokerCard
          key={broker.id}
          broker={broker}
          selected={selected === broker.id}
          onPress={() => onSelect(broker.id)}
        />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    padding: 16,
  },
});
```

### Connection Flow Screen

```typescript
// app/(tabs)/broker/connect.tsx
export default function ConnectBrokerScreen() {
  const [step, setStep] = useState<'select' | 'credentials'>('select');
  const [selectedBroker, setSelectedBroker] = useState<string | null>(null);
  const [validationResult, setValidationResult] = useState<'success' | 'error' | null>(null);

  const connectMutation = useConnectBroker();
  const validateMutation = useValidateBroker();

  const handleBrokerSelect = (brokerId: string) => {
    setSelectedBroker(brokerId);
    setStep('credentials');
  };

  const handleTestConnection = async (credentials) => {
    try {
      await validateMutation.mutateAsync({
        broker_type: selectedBroker,
        ...credentials,
      });
      setValidationResult('success');
    } catch (error) {
      setValidationResult('error');
    }
  };

  const handleConnect = async (credentials) => {
    await connectMutation.mutateAsync({
      broker_type: selectedBroker,
      ...credentials,
    });
    router.replace('/(tabs)/broker');
  };

  return (
    <View style={styles.container}>
      {step === 'select' && (
        <BrokerSelector onSelect={handleBrokerSelect} />
      )}
      {step === 'credentials' && selectedBroker && (
        <CredentialsForm
          broker={BROKERS[selectedBroker]}
          onTestConnection={handleTestConnection}
          onConnect={handleConnect}
          validationResult={validationResult}
          isValidating={validateMutation.isPending}
          isConnecting={connectMutation.isPending}
        />
      )}
    </View>
  );
}
```

---

## 6. Success Criteria

✅ Phase 10 is complete when:

- Broker management screen shows correct state
- All 4 brokers displayed in selector
- Dynamic credentials form works per broker
- Test Connection validates credentials
- Connect only works after validation
- Connected status displays correctly
- Token expiry warnings appear
- Disconnect works with confirmation
- Help links work for each broker
