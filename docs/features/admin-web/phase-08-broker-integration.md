---
goal: Implement broker connection management interface
version: 1.0
date_created: 2025-12-07
last_updated: 2025-12-07
owner: Frontend Engineering Team
status: Planned
tags: [admin-web, nextjs, broker, integration, credentials]
---

# Phase 8: Broker Integration

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Implement broker connection management interface for connecting, managing, and monitoring broker accounts (Zerodha, Dhan, Fyers, Angel One).

---

## 1. Requirements & Constraints

### Technical Requirements

- **REQ-001**: Secure credential input with masked fields
- **REQ-002**: Connection validation before saving
- **REQ-003**: Health status indicators
- **REQ-004**: Token expiry warnings

### Security Requirements

- **SEC-001**: Credentials transmitted over HTTPS
- **SEC-002**: Credentials encrypted at rest (backend)
- **SEC-003**: Never display full credentials

### Supported Brokers

- **BRK-001**: Zerodha (Kite Connect)
- **BRK-002**: Dhan
- **BRK-003**: Fyers
- **BRK-004**: Angel One

---

## 2. Implementation Tasks

### GOAL-008: Implement broker connection management interface

| Task | Description | Completed | Date |
|------|-------------|-----------|------|
| TASK-093 | Create `app/(dashboard)/brokers/page.tsx` showing connected brokers | | |
| TASK-094 | Create `components/brokers/BrokerList.tsx` with connection status | | |
| TASK-095 | Create `app/(dashboard)/brokers/connect/page.tsx` for new broker connection | | |
| TASK-096 | Create `components/brokers/BrokerSelector.tsx` with Zerodha, Dhan, Fyers, Angel One options | | |
| TASK-097 | Create `components/brokers/BrokerCredentialsForm.tsx` with secure input fields | | |
| TASK-098 | Implement credential validation before saving (test connection) | | |
| TASK-099 | Show broker connection status with health indicator | | |
| TASK-100 | Add broker disconnection with confirmation | | |
| TASK-101 | Create token expiry warning component | | |
| TASK-102 | Implement broker help documentation modal per broker | | |
| TASK-103 | Add broker reconnection flow for expired tokens | | |

---

## 3. Dependencies

- **DEP-001**: Shadcn/ui Card, Form, Dialog components
- **DEP-002**: Backend broker API endpoints
- **DEP-003**: React Hook Form + Zod

---

## 4. Files

### Broker Pages

- **FILE-001**: `admin-web/app/(dashboard)/brokers/page.tsx` - Connected brokers list
- **FILE-002**: `admin-web/app/(dashboard)/brokers/connect/page.tsx` - Connect new broker
- **FILE-003**: `admin-web/app/(dashboard)/brokers/[id]/page.tsx` - Broker detail
- **FILE-004**: `admin-web/app/(dashboard)/brokers/loading.tsx` - Loading state

### Broker Components

- **FILE-005**: `admin-web/components/brokers/BrokerList.tsx` - Broker cards
- **FILE-006**: `admin-web/components/brokers/BrokerSelector.tsx` - Broker type selection
- **FILE-007**: `admin-web/components/brokers/BrokerCredentialsForm.tsx` - Credential form
- **FILE-008**: `admin-web/components/brokers/BrokerCard.tsx` - Individual broker card
- **FILE-009**: `admin-web/components/brokers/BrokerStatus.tsx` - Health indicator
- **FILE-010**: `admin-web/components/brokers/TokenExpiryWarning.tsx` - Expiry alert
- **FILE-011**: `admin-web/components/brokers/BrokerHelpModal.tsx` - Help documentation
- **FILE-012**: `admin-web/components/brokers/DisconnectDialog.tsx` - Disconnect confirm

### Types

- **FILE-013**: `admin-web/types/broker.ts` - Broker type definitions

---

## Broker Credential Fields

### Zerodha (Kite Connect)

| Field | Description |
|-------|-------------|
| api_key | Kite Connect API Key |
| api_secret | Kite Connect API Secret |
| access_token | Session access token |

### Dhan

| Field | Description |
|-------|-------------|
| client_id | Dhan Client ID |
| access_token | Dhan Access Token |

### Fyers

| Field | Description |
|-------|-------------|
| app_id | Fyers App ID |
| access_token | Fyers Access Token |

### Angel One

| Field | Description |
|-------|-------------|
| api_key | Angel One API Key |
| client_id | Angel One Client ID |
| password | Trading Password |
| totp_secret | TOTP Secret for 2FA |

---

## Success Criteria

✅ Phase 8 is complete when:

- [ ] Connected brokers list with status
- [ ] Broker selection interface
- [ ] Credential forms for all 4 brokers
- [ ] Connection validation (test before save)
- [ ] Health status indicators (Connected/Disconnected/Error)
- [ ] Token expiry warnings displayed
- [ ] Disconnect with confirmation
- [ ] Help documentation per broker
- [ ] Reconnection flow for expired tokens

---

## Next Phase

[Phase 9: Strategy Playground →](./phase-09-playground.md)
