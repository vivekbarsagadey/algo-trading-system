# 📘 Scope Document

## Algo Trading System

**Version:** 1.0  
**Last Updated:** December 2024  
**Status:** Approved

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Scope](#2-project-scope)
3. [In-Scope Features](#3-in-scope-features)
4. [Out-of-Scope Features](#4-out-of-scope-features)
5. [Assumptions](#5-assumptions)
6. [Dependencies](#6-dependencies)
7. [Constraints](#7-constraints)
8. [Deliverables](#8-deliverables)
9. [Milestones](#9-milestones)
10. [Scope Change Process](#10-scope-change-process)

---

## 1. Executive Summary

### 1.1 Project Overview

The **Algo Trading System** is a mobile-first automated trading platform designed for retail traders in India. The system enables users to define simple time-based trading strategies and execute them automatically through integrated broker APIs.

### 1.2 Project Vision

```
Empower retail traders with simple, reliable, and safe automated trading 
that requires minimal technical knowledge and provides maximum execution discipline.
```

### 1.3 Scope Statement

This document defines the boundaries of the Algo Trading System MVP (Minimum Viable Product). It clearly identifies what is included and excluded from the project scope to ensure alignment among all stakeholders.

---

## 2. Project Scope

### 2.1 Product Scope

| Dimension | Scope |
|-----------|-------|
| **Platform** | Mobile application (iOS & Android via React Native/Expo) |
| **Backend** | Cloud-hosted API services (FastAPI on AWS) |
| **Market** | Indian equity markets (NSE, BSE) |
| **Users** | Retail traders in India |
| **Brokers** | Indian discount brokers with API access |

### 2.2 Project Boundaries

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           IN SCOPE                                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Mobile App    │  Backend API   │  Execution Engine  │  Broker   │    │
│  │  (React Native)│  (FastAPI)     │  (Redis + Celery)  │  Integration│   │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          OUT OF SCOPE                                    │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Web App  │  Desktop App  │  Options Trading  │  F&O Segment     │    │
│  │  Backtesting  │  Signal Generation  │  Social Trading  │  Copy   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Target Users

| User Segment | Description | MVP Priority |
|--------------|-------------|--------------|
| **Beginner Traders** | New to trading, want simple automation | Primary |
| **Part-Time Traders** | Have day jobs, can't watch markets | Primary |
| **Disciplined Traders** | Want strict execution without emotions | Secondary |

---

## 3. In-Scope Features

### 3.1 MVP Features (Phase 1)

#### 3.1.1 User Authentication

| Feature ID | Feature | Description | Priority |
|------------|---------|-------------|----------|
| MVP-AUTH-01 | User Registration | Email/password registration | P0 |
| MVP-AUTH-02 | User Login | JWT-based authentication | P0 |
| MVP-AUTH-03 | Session Management | Token refresh, secure logout | P0 |

#### 3.1.2 Broker Integration

| Feature ID | Feature | Description | Priority |
|------------|---------|-------------|----------|
| MVP-BRK-01 | Zerodha Integration | Connect Zerodha via Kite API | P0 |
| MVP-BRK-02 | Credential Storage | AES-256 encrypted storage | P0 |
| MVP-BRK-03 | Credential Validation | Real-time validation with broker | P0 |
| MVP-BRK-04 | Dhan Integration | Connect Dhan broker | P1 |
| MVP-BRK-05 | Angel One Integration | Connect Angel One broker | P1 |
| MVP-BRK-06 | Fyers Integration | Connect Fyers broker | P1 |

#### 3.1.3 Strategy Management

| Feature ID | Feature | Description | Priority |
|------------|---------|-------------|----------|
| MVP-STR-01 | Create Strategy | Define symbol, times, SL, quantity | P0 |
| MVP-STR-02 | Mandatory Stop-Loss | Require SL for all strategies | P0 |
| MVP-STR-03 | Start Strategy | Activate strategy for execution | P0 |
| MVP-STR-04 | Stop Strategy | Deactivate strategy immediately | P0 |
| MVP-STR-05 | View Status | Real-time strategy status display | P0 |
| MVP-STR-06 | Update Strategy | Modify SL, times while running | P1 |
| MVP-STR-07 | Multiple Strategies | Run multiple strategies simultaneously | P1 |

#### 3.1.4 Execution Engine

| Feature ID | Feature | Description | Priority |
|------------|---------|-------------|----------|
| MVP-EXE-01 | Time-Based BUY | Execute BUY at exact buy_time | P0 |
| MVP-EXE-02 | Time-Based SELL | Execute SELL at exact sell_time | P0 |
| MVP-EXE-03 | Stop-Loss Trigger | Auto-exit when price ≤ stop_loss | P0 |
| MVP-EXE-04 | Order Retry | Retry failed orders (max 3 attempts) | P0 |
| MVP-EXE-05 | Duplicate Prevention | Redis locking for order safety | P0 |
| MVP-EXE-06 | Order Logging | Log all order attempts and results | P0 |

#### 3.1.5 Real-Time Monitoring

| Feature ID | Feature | Description | Priority |
|------------|---------|-------------|----------|
| MVP-MON-01 | Price Feed | Real-time price via WebSocket | P0 |
| MVP-MON-02 | Status Polling | 5-second status updates to app | P0 |
| MVP-MON-03 | Last Action Display | Show BUY/SELL/SL Hit status | P0 |

### 3.2 MVP Feature Summary

| Category | P0 Features | P1 Features | Total |
|----------|-------------|-------------|-------|
| Authentication | 3 | 0 | 3 |
| Broker Integration | 3 | 3 | 6 |
| Strategy Management | 5 | 2 | 7 |
| Execution Engine | 6 | 0 | 6 |
| Monitoring | 3 | 0 | 3 |
| **Total** | **20** | **5** | **25** |

---

## 4. Out-of-Scope Features

### 4.1 Explicitly Excluded from MVP

| Category | Feature | Reason for Exclusion | Future Phase |
|----------|---------|---------------------|--------------|
| **Platform** | Web Application | Focus on mobile-first | Phase 2 |
| **Platform** | Desktop Application | Limited user demand | Phase 3+ |
| **Trading** | Options Trading | Complexity, regulatory | Phase 3+ |
| **Trading** | Futures Trading | Complexity, higher risk | Phase 3+ |
| **Trading** | Limit Orders | MARKET orders only for MVP | Phase 2 |
| **Trading** | Bracket Orders | Complexity | Phase 2 |
| **Trading** | Cover Orders | Complexity | Phase 2 |
| **Analysis** | Backtesting | Development effort | Phase 2 |
| **Analysis** | Technical Indicators | Complexity for users | Phase 2 |
| **Analysis** | Chart Integration | External dependency | Phase 2 |
| **Social** | Copy Trading | Legal/regulatory concerns | Phase 3+ |
| **Social** | Strategy Marketplace | Business model complexity | Phase 3+ |
| **Social** | Community Features | Not core to MVP | Phase 3+ |
| **Notifications** | Push Notifications | Can use polling for MVP | Phase 2 |
| **Notifications** | SMS Alerts | Cost, complexity | Phase 2 |
| **Notifications** | Email Alerts | Lower priority | Phase 2 |
| **Portfolio** | Portfolio Tracking | Broker provides this | Phase 2 |
| **Portfolio** | P&L Analytics | Broker provides this | Phase 2 |
| **Portfolio** | Tax Reports | Broker provides this | Phase 3+ |
| **Integration** | International Brokers | India focus for MVP | Phase 3+ |
| **Integration** | Crypto Exchanges | Regulatory uncertainty | TBD |

### 4.2 Technical Exclusions

| Component | Exclusion | Reason |
|-----------|-----------|--------|
| **OAuth Login** | No Google/Apple login | Simpler auth for MVP |
| **Biometric Auth** | No fingerprint/Face ID | Phase 2 feature |
| **Offline Mode** | No offline strategy creation | Backend-dependent |
| **Multi-Language** | English only | India English primary |
| **Dark Mode** | Light mode only | UI complexity |

### 4.3 Non-Functional Exclusions

| Area | Exclusion | MVP Alternative |
|------|-----------|-----------------|
| **Auto Token Refresh** | Manual token refresh required | User notification |
| **Multi-Region** | Single AWS region (Mumbai) | Scale later |
| **DR Site** | No disaster recovery site | AWS availability zones |
| **Real-Time Analytics** | No real-time dashboards | CloudWatch logs |

---

## 5. Assumptions

### 5.1 Business Assumptions

| ID | Assumption | Risk if Invalid |
|----|------------|-----------------|
| BA-01 | Retail traders want simple automation | Low user adoption |
| BA-02 | Users will provide valid broker credentials | Integration failures |
| BA-03 | Users have existing broker accounts | Onboarding friction |
| BA-04 | Subscription model is acceptable | Revenue challenges |
| BA-05 | SEBI regulations allow this service | Legal/compliance issues |

### 5.2 Technical Assumptions

| ID | Assumption | Risk if Invalid |
|----|------------|-----------------|
| TA-01 | Broker APIs are stable and available | Execution failures |
| TA-02 | Redis provides sub-millisecond latency | SL trigger delays |
| TA-03 | AWS Mumbai region is sufficient | Latency issues |
| TA-04 | WebSocket feeds are reliable | Missed price updates |
| TA-05 | React Native works for both iOS/Android | Platform-specific bugs |

### 5.3 User Assumptions

| ID | Assumption | Risk if Invalid |
|----|------------|-----------------|
| UA-01 | Users understand basic trading concepts | Support burden |
| UA-02 | Users can obtain broker API credentials | Onboarding drop-off |
| UA-03 | Users have reliable internet during trading | Missed status updates |
| UA-04 | Users will refresh access tokens daily | Execution failures |

---

## 6. Dependencies

### 6.1 External Dependencies

| ID | Dependency | Type | Impact if Unavailable |
|----|------------|------|----------------------|
| ED-01 | Zerodha Kite API | Critical | Cannot execute trades |
| ED-02 | Dhan API | Important | Reduced broker options |
| ED-03 | Angel One API | Important | Reduced broker options |
| ED-04 | Fyers API | Important | Reduced broker options |
| ED-05 | AWS Services | Critical | Complete system outage |
| ED-06 | Apple App Store | Critical | Cannot distribute iOS app |
| ED-07 | Google Play Store | Critical | Cannot distribute Android app |

### 6.2 Internal Dependencies

| ID | Dependency | Depends On | Impact |
|----|------------|------------|--------|
| ID-01 | Strategy Execution | Broker Integration | Cannot trade without broker |
| ID-02 | Stop-Loss Trigger | Price Feed | Cannot monitor prices |
| ID-03 | Order Placement | User Authentication | Cannot identify user |
| ID-04 | Status Display | Redis Runtime | Cannot show live status |

### 6.3 Team Dependencies

| ID | Dependency | Team/Role | Impact |
|----|------------|-----------|--------|
| TD-01 | Backend Development | Backend Engineer | Core API development |
| TD-02 | Mobile Development | Mobile Developer | App development |
| TD-03 | DevOps Setup | DevOps Engineer | Infrastructure |
| TD-04 | Security Review | Security Analyst | Compliance |
| TD-05 | Legal Review | Legal Counsel | Regulatory approval |

---

## 7. Constraints

### 7.1 Time Constraints

| Constraint | Description |
|------------|-------------|
| MVP Launch | 3 months from project start |
| Beta Testing | 2 weeks before launch |
| Market Hours | System must be ready by 9:15 AM IST daily |

### 7.2 Budget Constraints

| Category | Constraint |
|----------|------------|
| Infrastructure | AWS Free Tier + minimal paid services |
| Development | Small team (2-3 developers) |
| Marketing | Limited initial marketing budget |

### 7.3 Technical Constraints

| Constraint | Description | Mitigation |
|------------|-------------|------------|
| Broker Rate Limits | Limited API calls per second | Queue management |
| Token Expiry | Daily access token refresh | User notification |
| Market Hours | Trading 9:15 AM - 3:30 PM IST | Clear UI messaging |
| Order Types | MARKET orders only (MVP) | Future: LIMIT orders |

### 7.4 Regulatory Constraints

| Constraint | Description |
|------------|-------------|
| SEBI Guidelines | Must comply with trading regulations |
| Data Localization | User data stored in India (AWS Mumbai) |
| Broker Agreements | Must follow broker API terms of service |

---

## 8. Deliverables

### 8.1 Software Deliverables

| ID | Deliverable | Description | Format |
|----|-------------|-------------|--------|
| SD-01 | Mobile App (iOS) | React Native app for iPhone | .ipa (App Store) |
| SD-02 | Mobile App (Android) | React Native app for Android | .apk (Play Store) |
| SD-03 | Backend API | FastAPI REST API | Docker containers |
| SD-04 | Execution Engine | Celery workers + Redis | Docker containers |
| SD-05 | Database | PostgreSQL schema + migrations | SQL scripts |

### 8.2 Documentation Deliverables

| ID | Deliverable | Description | Status |
|----|-------------|-------------|--------|
| DD-01 | SRS Document | Software Requirements Specification | ✅ Complete |
| DD-02 | HLD Document | High-Level Design | ✅ Complete |
| DD-03 | LLD Document | Low-Level Design | ✅ Complete |
| DD-04 | API Documentation | REST API specifications | ✅ Complete |
| DD-05 | PRD Document | Product Requirements Document | ✅ Complete |
| DD-06 | Use Cases Document | Use cases and user stories | ✅ Complete |
| DD-07 | Scope Document | This document | ✅ Complete |
| DD-08 | User Guide | End-user documentation | 🔄 In Progress |
| DD-09 | Deployment Guide | Infrastructure setup guide | 🔄 In Progress |

### 8.3 Testing Deliverables

| ID | Deliverable | Description |
|----|-------------|-------------|
| TD-01 | Test Plan | QA test strategy document |
| TD-02 | Test Cases | Comprehensive test case suite |
| TD-03 | Unit Tests | Code-level tests (>80% coverage) |
| TD-04 | Integration Tests | API and component tests |
| TD-05 | E2E Tests | User flow tests |
| TD-06 | Load Test Results | Performance test reports |

---

## 9. Milestones

### 9.1 Project Timeline

```
Week 1-2    Week 3-4    Week 5-6    Week 7-8    Week 9-10   Week 11-12
   │           │           │           │           │           │
   ▼           ▼           ▼           ▼           ▼           ▼
┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐
│ M1   │   │ M2   │   │ M3   │   │ M4   │   │ M5   │   │ M6   │
│Setup │   │Auth  │   │Broker│   │Engine│   │Mobile│   │Launch│
│      │   │API   │   │Integ │   │      │   │App   │   │      │
└──────┘   └──────┘   └──────┘   └──────┘   └──────┘   └──────┘
```

### 9.2 Milestone Details

| Milestone | Name | Duration | Key Deliverables |
|-----------|------|----------|------------------|
| **M1** | Project Setup | Week 1-2 | Infrastructure, CI/CD, Dev environment |
| **M2** | Authentication API | Week 3-4 | User registration, login, JWT |
| **M3** | Broker Integration | Week 5-6 | Zerodha connection, credential storage |
| **M4** | Execution Engine | Week 7-8 | Time-based execution, stop-loss |
| **M5** | Mobile App | Week 9-10 | React Native app, all screens |
| **M6** | Launch | Week 11-12 | Beta testing, App Store submission |

### 9.3 Milestone Acceptance Criteria

#### M1: Project Setup ✅
- [ ] AWS infrastructure provisioned
- [ ] CI/CD pipeline operational
- [ ] Development environment documented
- [ ] Database schema deployed

#### M2: Authentication API
- [ ] User registration endpoint working
- [ ] User login endpoint working
- [ ] JWT token generation working
- [ ] Token refresh working
- [ ] Unit tests passing (>80%)

#### M3: Broker Integration
- [ ] Zerodha API connected
- [ ] Credential encryption working
- [ ] Credential validation working
- [ ] Integration tests passing

#### M4: Execution Engine
- [ ] Time-based BUY working
- [ ] Time-based SELL working
- [ ] Stop-loss trigger working (<5ms)
- [ ] Order retry working
- [ ] Duplicate prevention working
- [ ] Load test passed (500 strategies)

#### M5: Mobile App
- [ ] All screens implemented
- [ ] Strategy creation flow working
- [ ] Status polling working
- [ ] iOS build successful
- [ ] Android build successful

#### M6: Launch
- [ ] Beta testing complete (50 users)
- [ ] Critical bugs fixed
- [ ] App Store approval received
- [ ] Play Store approval received
- [ ] Production deployment complete

---

## 10. Scope Change Process

### 10.1 Change Request Process

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Submit    │────▶│   Review    │────▶│   Approve   │────▶│  Implement  │
│   Request   │     │   Impact    │     │   / Reject  │     │   Change    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### 10.2 Change Request Template

| Field | Description |
|-------|-------------|
| **Request ID** | CR-XXXX |
| **Requester** | Name and role |
| **Date** | Submission date |
| **Category** | Feature / Bug / Enhancement |
| **Priority** | Critical / High / Medium / Low |
| **Description** | Detailed description of change |
| **Justification** | Business reason for change |
| **Impact** | Timeline, cost, resource impact |
| **Decision** | Approved / Rejected / Deferred |
| **Decision Date** | Date of decision |
| **Decision Maker** | Approving authority |

### 10.3 Change Categories

| Category | Approval Authority | Turnaround |
|----------|-------------------|------------|
| Critical Bug | Tech Lead | Same day |
| Feature Change | Product Owner | 2 days |
| Scope Addition | Project Sponsor | 5 days |
| Architecture Change | CTO | 7 days |

### 10.4 Scope Change Log

| CR ID | Date | Description | Status | Impact |
|-------|------|-------------|--------|--------|
| CR-0001 | - | Initial scope baseline | Approved | - |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **MVP** | Minimum Viable Product - initial release scope |
| **P0** | Priority 0 - Must have for MVP |
| **P1** | Priority 1 - Important but can defer |
| **Stop-Loss (SL)** | Price level for automatic exit to limit losses |
| **Broker API** | Third-party trading platform interface |
| **Access Token** | Daily authentication credential for broker |

---

## Appendix B: Related Documents

| Document | Purpose |
|----------|---------|
| [PRD.md](PRD.md) | Product Requirements Document |
| [SRS.MD](SRS.MD) | Software Requirements Specification |
| [HLD.MD](HLD.MD) | High-Level Design |
| [LLD.MD](LLD.MD) | Low-Level Design |
| [USE-CASES-AND-USER-STORIES.md](USE-CASES-AND-USER-STORIES.md) | Use Cases & User Stories |
| [FEATURE-TRACEABILITY-MATRIX.md](FEATURE-TRACEABILITY-MATRIX.md) | Requirement Traceability |

---

## Appendix C: Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Project Sponsor | | | |
| Product Owner | | | |
| Tech Lead | | | |
| QA Lead | | | |

---

**Document Owner:** Project Management  
**Last Updated:** December 2024  
**Next Review:** Before each milestone
