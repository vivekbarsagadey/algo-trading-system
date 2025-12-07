# 📘 Product Requirements Document (PRD)

## Algo Trading System – High-Speed, Multi-Tenant Automated Trading Platform

**Version:** 1.0  
**Last Updated:** December 2024  
**Status:** Active

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Goals](#2-business-goals)
3. [User Needs](#3-user-needs)
4. [Core Features](#4-core-features)
5. [Success Metrics](#5-success-metrics)
6. [Constraints](#6-constraints)

---

## 1. Executive Summary

The Algo Trading System is a **comprehensive automated trading platform** with dual interfaces designed for retail traders who want simple, time-based trading automation without the complexity of traditional algorithmic trading tools.

The system enables users to:
- Define simple trading strategies with buy time, sell time, stop-loss, and quantity
- Connect their broker accounts securely
- Execute trades automatically with high-speed, fail-safe execution
- Monitor strategy status in real-time
- Access platform via mobile app OR admin web application

The system provides:
- **Mobile App (React Native)**: Primary interface for retail traders on-the-go
- **Admin Web Application (Next.js 16)**: Comprehensive web interface for users, admins, and brokers with role-based access control

**Target Market:** Retail traders in India seeking automated execution for intraday and positional strategies.

**Technology Stack:** 
- **Frontend**: React Native (Mobile), Next.js 16 (Admin Web App)
- **Backend**: FastAPI (Python 3.11+), Redis (In-memory execution), PostgreSQL (Persistence)
- **Infrastructure**: AWS (ECS/EKS, RDS, ElastiCache)
- **Authentication**: JWT with role-based access control (Admin, User, Broker)

---

## 2. Business Goals

### 2.1 Primary Business Objectives

| Goal | Description | Target |
|------|-------------|--------|
| **BG-1: Market Entry** | Establish presence in the retail algo trading market in India | Launch MVP within 3 months |
| **BG-2: User Acquisition** | Attract retail traders seeking simple automation | 1,000 active users in first 6 months |
| **BG-3: Revenue Generation** | Build sustainable subscription-based revenue model | Positive unit economics by Month 9 |
| **BG-4: Platform Reliability** | Establish trust through consistent, reliable execution | 99% uptime, <1% order failure rate |

### 2.2 Strategic Goals

| Goal | Description | Success Indicator |
|------|-------------|-------------------|
| **SG-1: Simplicity Leadership** | Be the simplest algo trading app for retail users | App flow completion in <60 seconds |
| **SG-2: Safety First** | Mandatory stop-loss and fail-safe mechanisms | Zero cases of runaway losses |
| **SG-3: Multi-Broker Support** | Support major Indian brokers | 4+ broker integrations (Zerodha, Dhan, Fyers, Angel One) |
| **SG-4: Scalability** | Handle high concurrent load during market hours | 500+ simultaneous active strategies |

### 2.3 Business Value Proposition

```
For retail traders who want automated trading execution,
the Algo Trading System is a mobile application
that provides simple, time-based trading automation.

Unlike complex algo trading platforms,
our product requires only 5 inputs (symbol, buy time, sell time, stop-loss, quantity)
and executes with high-speed, fail-safe reliability.
```

---

## 3. User Needs

### 3.1 Target User Personas

#### Persona 1: System Administrator (Primary)

| Attribute | Description |
|-----------|-------------|
| **Profile** | Platform admin managing all users and system health |
| **Technical Skill** | High – understands system architecture and trading concepts |
| **Goal** | Monitor platform health, manage users, resolve issues |
| **Pain Points** | Need comprehensive view of all users, strategies, and system metrics |
| **Motivation** | "I need full control and visibility to ensure platform reliability" |
| **Access Level** | Admin Web Application with full privileges |

#### Persona 2: Beginner Trader (Primary)

| Attribute | Description |
|-----------|-------------|
| **Profile** | New to trading, wants to automate simple strategies |
| **Technical Skill** | Low – doesn't understand charts or complex indicators |
| **Goal** | Remove emotional trading decisions |
| **Pain Points** | Overwhelmed by complex trading tools, misses entry/exit times |
| **Motivation** | "I just want to buy at 9:30 AM and sell at 3:15 PM with a stop-loss" |
| **Access Level** | Mobile App OR Web Application (User role) |

#### Persona 3: Part-Time Trader (Secondary)

| Attribute | Description |
|-----------|-------------|
| **Profile** | Has a day job, can't watch markets continuously |
| **Technical Skill** | Medium – understands basic trading concepts |
| **Goal** | Execute predetermined strategies while working |
| **Pain Points** | Can't monitor positions during work hours |
| **Motivation** | "I know what I want to trade, I just can't execute it manually" |
| **Access Level** | Mobile App OR Web Application (User role) |

#### Persona 4: Disciplined Trader (Secondary)

| Attribute | Description |
|-----------|-------------|
| **Profile** | Experienced trader who wants strict execution discipline |
| **Technical Skill** | High – understands trading but wants automation |
| **Goal** | Eliminate emotional decision-making |
| **Pain Points** | Often holds losing positions too long, exits winning trades too early |
| **Motivation** | "I need a system that forces me to stick to my plan" |

### 3.2 User Needs Matrix

| Need ID | User Need | Priority | Persona(s) |
|---------|-----------|----------|------------|
| **UN-1** | Register and login quickly with minimal friction | High | All |
| **UN-2** | Connect broker account securely | High | All |
| **UN-3** | Create strategy with minimal inputs (symbol, times, SL, qty) | High | All |
| **UN-4** | Start/Stop strategy with single tap | High | All |
| **UN-5** | See real-time strategy status | High | All |
| **UN-6** | Automatic execution at exact specified times | Critical | All |
| **UN-7** | Mandatory stop-loss protection | Critical | All |
| **UN-8** | Immediate stop-loss execution when price breaches | Critical | All |
| **UN-9** | Reliable execution even when app is closed | High | Persona 2 |
| **UN-10** | Clear feedback on executed actions (BUY/SELL/SL Hit) | High | All |
| **UN-11** | No complex charts or technical indicators | High | Persona 1 |
| **UN-12** | Secure storage of broker credentials | Critical | All |

### 3.3 User Journey Summary

```
Download App → Register/Login → Connect Broker → Create Strategy → Start Strategy → Monitor → Exit
     ↓              ↓                 ↓               ↓               ↓            ↓        ↓
  30 sec         30 sec            2 min          1 min           1 tap      Passive    Auto
```

**Total Time to First Strategy:** Under 5 minutes

---

## 4. Core Features

### 4.1 Authentication & Onboarding

| Feature ID | Feature | Description | Priority |
|------------|---------|-------------|----------|
| **F-1.1** | User Registration | Email/password registration with validation | P0 |
| **F-1.2** | User Login | JWT-based authentication | P0 |
| **F-1.3** | Password Reset | Email-based password recovery | P1 |
| **F-1.4** | Session Management | Automatic token refresh, secure logout | P1 |

### 4.2 Broker Integration

| Feature ID | Feature | Description | Priority |
|------------|---------|-------------|----------|
| **F-2.1** | Broker Credentials Input | API Key, Secret Key, Access Token entry | P0 |
| **F-2.2** | Credential Validation | Real-time validation with broker API | P0 |
| **F-2.3** | Secure Storage | AES-256 encrypted storage of credentials | P0 |
| **F-2.4** | Multi-Broker Support | Support for Zerodha, Dhan, Fyers, Angel One | P1 |
| **F-2.5** | Token Refresh Notification | Alert when access token expires | P1 |

### 4.3 Strategy Management

| Feature ID | Feature | Description | Priority |
|------------|---------|-------------|----------|
| **F-3.1** | Strategy Creation | Define symbol, buy time, sell time, stop-loss, quantity | P0 |
| **F-3.2** | Mandatory Stop-Loss | Reject strategies without stop-loss | P0 |
| **F-3.3** | Strategy Validation | Validate times, quantity, symbol before save | P0 |
| **F-3.4** | Strategy Start | Activate strategy for execution | P0 |
| **F-3.5** | Strategy Stop | Deactivate strategy immediately | P0 |
| **F-3.6** | Strategy Status | Real-time status (Running/Stopped/Completed) | P0 |
| **F-3.7** | Dynamic Updates | Update SL, times, quantity while running | P1 |
| **F-3.8** | Multiple Strategies | Run multiple strategies simultaneously | P1 |

### 4.4 Execution Engine

| Feature ID | Feature | Description | Priority |
|------------|---------|-------------|----------|
| **F-4.1** | Time-Based BUY | Execute BUY order at exact buy_time | P0 |
| **F-4.2** | Time-Based SELL | Execute SELL order at exact sell_time | P0 |
| **F-4.3** | Stop-Loss Trigger | Execute SELL immediately when price ≤ stop_loss | P0 |
| **F-4.4** | Order Retry | Retry failed orders up to 3 times | P0 |
| **F-4.5** | Duplicate Prevention | Redis locking to prevent double execution | P0 |
| **F-4.6** | Order Logging | Log all order attempts and responses | P0 |
| **F-4.7** | Fail-Safe Shutdown | Auto-stop on critical errors | P0 |

### 4.5 Real-Time Monitoring

| Feature ID | Feature | Description | Priority |
|------------|---------|-------------|----------|
| **F-5.1** | Price Feed | Real-time price updates via WebSocket | P0 |
| **F-5.2** | Status Polling | 5-second status updates to mobile app | P0 |
| **F-5.3** | Last Action Display | Show last executed action (BUY/SELL/SL Hit) | P0 |
| **F-5.4** | Position Status | Show current position (None/Bought/Sold) | P0 |

### 4.6 Admin Web Application (Next.js 16)

The Admin Web Application provides a comprehensive web interface built with Next.js 16, featuring role-based access control and serving as an alternative to the mobile app for users while providing powerful administrative capabilities.

#### 4.6.1 Role-Based Access Control

| Role | Permissions | Access Scope |
|------|-------------|--------------|
| **Admin** | Full system access, user management, system monitoring | All features |
| **User** | Strategy management, broker integration, monitoring | Own data only |
| **Broker** | View strategies using their API, monitor integration health | Broker-specific data |

#### 4.6.2 Admin Features

| Feature ID | Feature | Description | Priority |
|------------|---------|-------------|----------|
| **F-6.1** | User Management Dashboard | View, create, edit, delete users | P0 |
| **F-6.2** | Role Assignment | Assign/modify user roles (Admin/User/Broker) | P0 |
| **F-6.3** | System Health Monitor | Real-time metrics: uptime, latency, order stats | P0 |
| **F-6.4** | Strategy Overview | View all strategies across all users | P0 |
| **F-6.5** | Execution Logs | Comprehensive logging of all order executions | P0 |
| **F-6.6** | Error Tracking | Monitor and debug system errors | P0 |
| **F-6.7** | Analytics Dashboard | Platform-wide usage analytics and charts | P1 |
| **F-6.8** | User Impersonation | View system as specific user (for support) | P1 |
| **F-6.9** | Configuration Management | Manage system-wide settings | P1 |

#### 4.6.3 User Features (Web Alternative to Mobile)

| Feature ID | Feature | Description | Priority |
|------------|---------|-------------|----------|
| **F-6.10** | Web Authentication | JWT-based login with NextAuth.js | P0 |
| **F-6.11** | Strategy Builder | Web-based strategy creation interface | P0 |
| **F-6.12** | Broker Connection | Manage broker credentials via web | P0 |
| **F-6.13** | Strategy Control | Start/stop strategies from web dashboard | P0 |
| **F-6.14** | Real-time Updates | Live strategy status with Server Components | P0 |
| **F-6.15** | Trade History | View past executions and performance | P1 |
| **F-6.16** | Playground | Test strategies with simulated data | P1 |

#### 4.6.4 Technical Implementation

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | Next.js 16 (App Router) | React-based web framework |
| **Authentication** | NextAuth.js v5 + JWT | Session management |
| **UI Library** | Shadcn/ui + Tailwind CSS | Modern component library |
| **State Management** | React Server Components + Zustand | Optimal performance |
| **API Integration** | Server Actions + Route Handlers | Backend communication |
| **Real-time** | Server-Sent Events (SSE) | Live updates |
| **Charts** | Recharts | Analytics visualization |
| **Forms** | React Hook Form + Zod | Validation |

#### 4.6.5 Security Features

| Feature | Implementation | Priority |
|---------|----------------|----------|
| Proxy Middleware | Route protection based on role | P0 |
| CORS Configuration | Secure API access | P0 |
| CSRF Protection | Token-based protection | P0 |
| Rate Limiting | Per-user/IP rate limits | P0 |
| Session Management | Secure cookie handling | P0 |
| Input Sanitization | XSS prevention | P0 |
| SQL Injection Protection | Parameterized queries | P0 |

#### 4.6.6 User Interface Features

| Feature | Description | Priority |
|---------|-------------|----------|
| Responsive Design | Mobile, tablet, desktop support | P0 |
| Dark Mode | Theme switching capability | P1 |
| Keyboard Shortcuts | Power user navigation | P1 |
| Accessibility (WCAG 2.1) | Screen reader support, ARIA labels | P1 |
| Internationalization | Multi-language support (future) | P2 |

### 4.7 Feature Priority Matrix

| Priority | Count | Description |
|----------|-------|-------------|
| **P0 (Must Have)** | 42 | Critical for MVP launch (includes admin web app) |
| **P1 (Should Have)** | 14 | Important for complete experience |
| **P2 (Nice to Have)** | 1 | Future enhancements |

---

## 5. Success Metrics

### 5.1 Key Performance Indicators (KPIs)

#### User-Centric Metrics

| Metric ID | Metric | Target | Measurement Method |
|-----------|--------|--------|-------------------|
| **M-U1** | Time to First Strategy | < 5 minutes | Analytics: Registration → Strategy Start |
| **M-U2** | Strategy Creation Success Rate | > 95% | (Strategies created) / (Attempts) |
| **M-U3** | Daily Active Users (DAU) | 200+ by Month 6 | Unique logins per day |
| **M-U4** | User Retention (D30) | > 40% | Users active after 30 days |
| **M-U5** | App Store Rating | ≥ 4.0 stars | App Store / Play Store |

#### Technical Metrics

| Metric ID | Metric | Target | Measurement Method |
|-----------|--------|--------|-------------------|
| **M-T1** | Order Execution Latency | < 300 ms | Time from trigger to broker API call |
| **M-T2** | Stop-Loss Trigger Latency | < 5 ms | Time from price breach to SL event |
| **M-T3** | Redis Operation Latency | < 1 ms | Redis CRUD operations |
| **M-T4** | Order Success Rate | > 99% | (Successful orders) / (Total orders) |
| **M-T5** | System Uptime | > 99% | (Uptime minutes) / (Total minutes) |

#### Business Metrics

| Metric ID | Metric | Target | Measurement Method |
|-----------|--------|--------|-------------------|
| **M-B1** | Monthly Active Strategies | 500+ by Month 6 | Strategies started per month |
| **M-B2** | Concurrent Active Strategies | 500+ | Peak simultaneous running strategies |
| **M-B3** | Order Volume | 1,000+ orders/day | Daily order count |
| **M-B4** | Customer Acquisition Cost (CAC) | < ₹500 | Marketing spend / New users |
| **M-B5** | Net Promoter Score (NPS) | > 40 | User surveys |

### 5.2 Safety Metrics

| Metric ID | Metric | Target | Measurement Method |
|-----------|--------|--------|-------------------|
| **M-S1** | Stop-Loss Compliance | 100% | Strategies with mandatory SL |
| **M-S2** | Failed Stop-Loss Executions | 0 | SL triggers that failed to execute |
| **M-S3** | Duplicate Order Prevention | 100% | No duplicate BUY/SELL orders |
| **M-S4** | Cross-Tenant Data Leakage | 0 incidents | Security audit results |

### 5.3 Success Criteria for MVP Launch

| Criteria | Requirement | Status |
|----------|-------------|--------|
| All P0 features implemented | 22/22 features | Required |
| Order execution latency < 300 ms | Load test verified | Required |
| 99% uptime during market hours | Monitoring verified | Required |
| Zero stop-loss failures | Integration test verified | Required |
| Security audit passed | External audit | Required |
| 50 beta users onboarded | Beta testing complete | Required |

---

## 6. Constraints

### 6.1 Technical Constraints

| Constraint ID | Constraint | Impact | Mitigation |
|---------------|------------|--------|------------|
| **TC-1** | Broker API Rate Limits | Limited order frequency | Queue management, rate limiting |
| **TC-2** | Broker API Availability | System depends on broker uptime | Retry logic, failover handling |
| **TC-3** | Access Token Expiry | Daily token refresh required | User notification, manual refresh (MVP) |
| **TC-4** | Market Hours Only | Execution only during trading hours | Clear UI messaging |
| **TC-5** | Single Order Type (Market) | MVP supports only MARKET orders | Future: LIMIT orders |
| **TC-6** | Mobile Network Dependency | Requires internet for status updates | Backend executes independently |

### 6.2 Business Constraints

| Constraint ID | Constraint | Impact | Mitigation |
|---------------|------------|--------|------------|
| **BC-1** | Regulatory Compliance | Must comply with SEBI guidelines | Legal review before launch |
| **BC-2** | Broker Partnerships | Need broker API access | Start with public APIs (Zerodha Kite) |
| **BC-3** | Limited Development Resources | Small team | Prioritize P0 features only for MVP |
| **BC-4** | Time to Market | Competitive pressure | 3-month MVP timeline |

### 6.3 Security Constraints

| Constraint ID | Constraint | Impact | Mitigation |
|---------------|------------|--------|------------|
| **SC-1** | Credential Security | Broker keys are highly sensitive | AES-256 encryption, AWS Secrets Manager |
| **SC-2** | Multi-Tenant Isolation | User data must never leak | Per-user Redis namespaces, DB isolation |
| **SC-3** | HTTPS Required | All communication must be encrypted | TLS 1.2+ enforced |
| **SC-4** | JWT Security | Session tokens must be secure | Short expiry, refresh tokens |

### 6.4 Safety Constraints

| Constraint ID | Constraint | Impact | Mitigation |
|---------------|------------|--------|------------|
| **SAF-1** | Mandatory Stop-Loss | Every strategy must have SL | Backend validation, UI enforcement |
| **SAF-2** | Order Retry Limit | Max 3 retries per order | Fail-safe shutdown after 3 failures |
| **SAF-3** | Duplicate Prevention | No double BUY/SELL | Redis locking mechanism |
| **SAF-4** | Position Tracking | Accurate position state required | Redis runtime state, order logging |

### 6.5 Performance Constraints

| Constraint ID | Constraint | Requirement |
|---------------|------------|-------------|
| **PC-1** | Order Execution Latency | < 300 ms from trigger to broker API |
| **PC-2** | Stop-Loss Reaction Time | < 5 ms from price breach to event |
| **PC-3** | Redis Operations | < 1 ms read/write |
| **PC-4** | Concurrent Strategies | Support 500+ simultaneous strategies |
| **PC-5** | API Response Time | < 500 ms for all REST endpoints |

### 6.6 Scalability Constraints

| Constraint ID | Constraint | Requirement |
|---------------|------------|-------------|
| **SCC-1** | Stateless Backend | All state in Redis/PostgreSQL |
| **SCC-2** | Horizontal Scaling | ECS/EKS container scaling |
| **SCC-3** | Database Connections | Connection pooling required |
| **SCC-4** | Redis Clustering | Single Redis instance for MVP, cluster-ready |

### 6.7 Availability Constraints

| Constraint ID | Constraint | Requirement |
|---------------|------------|-------------|
| **AC-1** | System Uptime | 99% during market hours (9:15 AM - 3:30 PM IST) |
| **AC-2** | Auto-Recovery | Containers auto-restart on crash |
| **AC-3** | Strategy Recovery | Strategies resume after backend restart |
| **AC-4** | Data Durability | Zero data loss on failure |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Strategy** | A trading automation configuration (symbol, buy time, sell time, SL, quantity) |
| **Stop-Loss (SL)** | Price level at which position is automatically exited to limit losses |
| **Broker API** | Third-party trading platform API (Zerodha, Dhan, etc.) |
| **Access Token** | Daily authentication token for broker API |
| **Execution Engine** | Backend service that places orders via broker API |
| **Redis Runtime** | In-memory storage for active strategy state |
| **Multi-Tenant** | Multiple users sharing infrastructure with complete isolation |

---

## Appendix B: Related Documents

| Document | Purpose |
|----------|---------|
| [SRS.MD](SRS.MD) | Software Requirements Specification |
| [HLD.MD](HLD.MD) | High-Level Design |
| [LLD.MD](LLD.MD) | Low-Level Design |
| [API-SCHEMA.md](API-SCHEMA.md) | API Endpoint Specifications |
| [SCHEMA.md](SCHEMA.md) | Database & Redis Schema |
| [FEATURE-TRACEABILITY-MATRIX.md](FEATURE-TRACEABILITY-MATRIX.md) | Requirement Traceability |
| [QA-EXECUTION-MATRIX.md](QA-EXECUTION-MATRIX.md) | Test Cases |

---

**Document Owner:** Product Team  
**Approved By:** [Pending]  
**Next Review:** [TBD]
