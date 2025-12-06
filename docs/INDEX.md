# 📚 Algo Trading System Documentation Index

**High-Speed, Multi-Tenant Automated Trading Platform**

---

## 🎯 Purpose of This Documentation

This documentation serves as the **single source of truth** for the Algo Trading System. It provides comprehensive technical specifications, architectural designs, and implementation guides for:

- **Product Owners** – Understanding system capabilities and requirements
- **Backend Developers** – FastAPI, Redis, PostgreSQL implementation details
- **Mobile Developers** – React Native/Expo app specifications
- **QA Engineers** – Test cases, validation matrices, and quality assurance
- **DevOps Engineers** – Deployment, infrastructure, and monitoring
- **Architects** – System design, state machines, and integration flows
- **New Team Members** – Onboarding and understanding the complete system

---

## 📋 Document Categories

| Category | Purpose |
|----------|---------|
| 🏛️ **Core Architecture** | System design, requirements, and high-level structure |
| 🔧 **Technical Specifications** | Detailed implementation guides and schemas |
| 🔄 **Workflows & Sequences** | End-to-end flows, event processing, and state transitions |
| 🔌 **Integrations** | Broker APIs, external services, and connectors |
| ⚠️ **Failure & Recovery** | Error handling, retry logic, and safety mechanisms |
| ✅ **Quality Assurance** | Test cases, validation matrices, and traceability |

---

## 🏛️ Core Architecture Documents

### [SRS.MD](SRS.MD) – Software Requirements Specification
> **What**: Complete functional and non-functional requirements for the system.
>
> **Why You Need This**: Defines what the system must do, who the users are, and what constraints apply. Essential for understanding the product scope.
>
> **Key Contents**:
> - User types (retail traders, beginners)
> - Functional requirements (auth, broker, strategies)
> - Non-functional requirements (performance, security, availability)
> - System constraints and dependencies

---

### [HLD.MD](HLD.MD) – High-Level Design
> **What**: System architecture overview with component diagrams.
>
> **Why You Need This**: Provides a bird's-eye view of how all system components connect and interact.
>
> **Key Contents**:
> - Architecture diagram (Mobile → Backend → Redis → Broker → DB)
> - Component responsibilities
> - Technology stack decisions
> - Data flow overview

---

### [LLD.MD](LLD.MD) – Low-Level Design
> **What**: Detailed implementation design for each microservice.
>
> **Why You Need This**: Developer-ready specifications with class diagrams, function signatures, and database schemas.
>
> **Key Contents**:
> - Service-by-service breakdown
> - Directory structures
> - Class and function details
> - Redis key patterns
> - Error handling design

---

### [FOLDER-STRUCTURE.md](FOLDER-STRUCTURE.md) – Project Layout
> **What**: Canonical folder structure for backend, mobile, and infrastructure.
>
> **Why You Need This**: Ensures consistent project organization across all developers.
>
> **Key Contents**:
> - Backend folder layout
> - Mobile app structure
> - Infrastructure configuration
> - Documentation organization

---

## 🔧 Technical Specifications

### [BACKEND-SPEC.md](BACKEND-SPEC.md) – Backend Architecture
> **What**: Complete backend specification with FastAPI, Redis, and worker architecture.
>
> **Why You Need This**: Primary reference for backend developers implementing services.
>
> **Key Contents**:
> - Technology stack details
> - API layer design
> - Service layer patterns
> - Worker architecture
> - Redis runtime configuration

---

### [FRONTEND-SPEC.md](FRONTEND-SPEC.md) – Mobile App Specification
> **What**: React Native/Expo app design and screen specifications.
>
> **Why You Need This**: Complete guide for mobile developers building the trading app.
>
> **Key Contents**:
> - Screen-by-screen specifications
> - Component library
> - State management (Zustand)
> - API integration patterns
> - Navigation structure

---

### [API-SCHEMA.md](API-SCHEMA.md) – REST API Specification
> **What**: Complete API endpoint definitions with request/response schemas.
>
> **Why You Need This**: Defines the contract between frontend and backend.
>
> **Key Contents**:
> - Authentication endpoints
> - Broker endpoints
> - Strategy endpoints
> - Request/response schemas
> - Error codes

---

### [API-DOCUMENTATION.md](API-DOCUMENTATION.md) – Database & Redis Schema
> **What**: Unified database and Redis schema definitions.
>
> **Why You Need This**: Single source of truth for all data structures.
>
> **Key Contents**:
> - PostgreSQL table schemas
> - Redis key patterns
> - Data relationships
> - Indexes and constraints

---

### [SCHEMA.md](SCHEMA.md) – Master Schema Definition
> **What**: Complete schema for DB, Redis, event pipeline, and API contracts.
>
> **Why You Need This**: Comprehensive reference for all data structures in the system.
>
> **Key Contents**:
> - Database tables (users, strategies, broker_keys, order_logs)
> - Redis data structures
> - Event schemas
> - API contract definitions

---

### [BROKER-ORDER-SCHEMA.md](BROKER-ORDER-SCHEMA.md) – Order Schema
> **What**: Canonical format for BUY/SELL/STOPLOSS orders across brokers.
>
> **Why You Need This**: Standardizes order handling regardless of which broker is used.
>
> **Key Contents**:
> - Internal order format
> - Broker-specific mappings
> - Order validation rules
> - Response handling

---

## 🔄 Workflows & Sequences

### [WORKFLOW-SCHEMA.md](WORKFLOW-SCHEMA.md) – End-to-End Workflows
> **What**: Complete operational workflows from user registration to trade execution.
>
> **Why You Need This**: Understand the exact sequence of operations for every user action.
>
> **Key Contents**:
> - User onboarding workflow
> - Broker setup workflow
> - Strategy creation and activation
> - BUY/SELL/STOPLOSS execution
> - Recovery workflows

---

### [FULL-SEQUENCE-DOCUMENT.md](FULL-SEQUENCE-DOCUMENT.md) – Complete Sequence Flows
> **What**: All sequence diagrams covering every system interaction.
>
> **Why You Need This**: Visual representation of component interactions for architects and developers.
>
> **Key Contents**:
> - User onboarding sequence
> - Strategy lifecycle sequences
> - Execution engine sequences
> - Multi-tenant isolation sequences

---

### [END-TO-END-SEQUENCE-DIAGRAM.md](END-TO-END-SEQUENCE-DIAGRAM.md) – Master Sequence
> **What**: Single unified diagram showing the complete system flow.
>
> **Why You Need This**: The most important diagram for architecture validation and onboarding.
>
> **Key Contents**:
> - Complete flow: User → Mobile → Backend → Redis → Broker → DB
> - All component interactions
> - Error paths included

---

### [PIPELINE-FLOW.md](PIPELINE-FLOW.md) – Execution Pipelines
> **What**: Detailed pipeline descriptions for strategy execution.
>
> **Why You Need This**: Understand how data flows through the system at each stage.
>
> **Key Contents**:
> - Strategy ingestion pipeline
> - Time-trigger pipeline
> - Price-trigger pipeline
> - Execution pipeline
> - Error & retry pipelines

---

### [EVENT-PROCESSING-PIPELINE.md](EVENT-PROCESSING-PIPELINE.md) – Event Processing
> **What**: How events flow, transform, and execute across the system.
>
> **Why You Need This**: Critical for implementing event-driven components.
>
> **Key Contents**:
> - Event flow paths
> - Transformation rules
> - Handler specifications
> - Pipeline stages

---

### [EVENT-MAP.md](EVENT-MAP.md) – Master Event Dictionary
> **What**: Complete catalog of all system events.
>
> **Why You Need This**: Single source of truth for event handling.
>
> **Key Contents**:
> - Event triggers and sources
> - Required data for each event
> - Redis keys involved
> - Expected outcomes
> - Error handling

---

### [STATE-MACHINE.md](STATE-MACHINE.md) – Strategy State Machine
> **What**: State transitions for strategy execution.
>
> **Why You Need This**: Ensures predictable behavior and safe transitions.
>
> **Key Contents**:
> - State definitions (created → ready → running → bought → sold)
> - Transition triggers
> - Guard conditions
> - Failure states

---

### [SYSTEM-STATE-MACHINE.md](SYSTEM-STATE-MACHINE.md) – Complete Lifecycle States
> **What**: Comprehensive state machine for the entire strategy lifecycle.
>
> **Why You Need This**: Governs both backend runtime (Redis) and UI state (Mobile).
>
> **Key Contents**:
> - All possible states
> - State transition matrix
> - Multi-tenant correctness
> - Recovery state handling

---

### [MOBILE-FLOW-SEQUENCE.md](MOBILE-FLOW-SEQUENCE.md) – Mobile UX Flows
> **What**: Screen-by-screen user flow with API calls and state changes.
>
> **Why You Need This**: Essential for frontend developers and UX designers.
>
> **Key Contents**:
> - Screen navigation flows
> - API call sequences
> - State management
> - Error handling in UI

---

### [USER-JOURNEY.md](USER-JOURNEY.md) – End-to-End User Experience
> **What**: Complete user journey from discovery to trade execution.
>
> **Why You Need This**: Human-level perspective for product and UX decisions.
>
> **Key Contents**:
> - User personas
> - Journey stages (discover → onboard → trade → monitor)
> - Emotional states and expectations
> - Pain points and solutions

---

## 🔌 Integration Documents

### [BROKER-INTEGRATION-SEQUENCE.md](BROKER-INTEGRATION-SEQUENCE.md) – Broker API Integration
> **What**: Complete integration lifecycle with broker APIs (Zerodha, Dhan, etc.).
>
> **Why You Need This**: Implement broker connections correctly with all edge cases.
>
> **Key Contents**:
> - API key validation flow
> - Token management
> - Order placement sequences
> - WebSocket price feeds
> - Retry logic

---

### [EXECUTION-ENGINE-INTEGRATION.MD](EXECUTION-ENGINE-INTEGRATION.MD) – Engine Integration
> **What**: How the Execution Engine integrates with other components.
>
> **Why You Need This**: Understand the core runtime component's connections.
>
> **Key Contents**:
> - Redis integration
> - Broker API calls
> - Scheduler coordination
> - Market listener sync

---

### [EXECUTION-ENGINE-PROCESSING.md](EXECUTION-ENGINE-PROCESSING.md) – Engine Processing Logic
> **What**: Internal processing model for all order types.
>
> **Why You Need This**: Implement the core execution logic correctly.
>
> **Key Contents**:
> - BUY/SELL/STOPLOSS processing
> - Retry and abort logic
> - Locking mechanisms
> - Runtime state updates

---

## ⚠️ Failure & Recovery Documents

### [FAILURE-SEQUENCE-DOC.md](FAILURE-SEQUENCE-DOC.md) – Failure Sequences
> **What**: Detailed failure scenarios with recovery logic.
>
> **Why You Need This**: Ensure the system handles failures gracefully.
>
> **Key Contents**:
> - All failure points mapped
> - Recovery sequences
> - Redis state updates during failure
> - Final state guarantees

---

### [BROKER-FAILURE-TEST-CASES.MD](BROKER-FAILURE-TEST-CASES.MD) – Broker Failure Tests
> **What**: Complete test suite for broker integration failures.
>
> **Why You Need This**: Validate all failure scenarios before production.
>
> **Key Contents**:
> - API downtime scenarios
> - Token expiry handling
> - Partial fills
> - Network failures
> - Recovery tests

---

## ✅ Quality Assurance Documents

### [QA-EXECUTION-MATRIX.md](QA-EXECUTION-MATRIX.md) – QA Coverage Matrix
> **What**: Complete QA test matrix covering all requirements.
>
> **Why You Need This**: Ensure every requirement has corresponding test cases.
>
> **Key Contents**:
> - Test case IDs
> - Requirement mapping
> - Expected outcomes
> - Pass criteria

---

### [FEATURE-TRACEABILITY-MATRIX.md](FEATURE-TRACEABILITY-MATRIX.md) – Requirement Traceability
> **What**: Maps PRD requirements to SRS, features, APIs, and tests.
>
> **Why You Need This**: Guarantees full compliance and zero missing functionality.
>
> **Key Contents**:
> - PRD → SRS → Feature → API → Test mapping
> - Complete coverage verification
> - Gap analysis

---

### [SYSTEM-CAPABILITIES-MATRIX.md](SYSTEM-CAPABILITIES-MATRIX.md) – Capability Mapping
> **What**: Maps system capabilities to components and requirements.
>
> **Why You Need This**: Single source of truth from Product → Engineering → Runtime.
>
> **Key Contents**:
> - Capability definitions
> - Feature implementations
> - Component responsibilities
> - Constraint mappings

---

## 🗺️ Quick Navigation by Role

### For Backend Developers
1. Start with [LLD.MD](LLD.MD) for implementation details
2. Reference [BACKEND-SPEC.md](BACKEND-SPEC.md) for architecture
3. Use [API-SCHEMA.md](API-SCHEMA.md) for endpoint contracts
4. Follow [EXECUTION-ENGINE-PROCESSING.md](EXECUTION-ENGINE-PROCESSING.md) for core logic

### For Mobile Developers
1. Start with [FRONTEND-SPEC.md](FRONTEND-SPEC.md) for app design
2. Reference [MOBILE-FLOW-SEQUENCE.md](MOBILE-FLOW-SEQUENCE.md) for UX flows
3. Use [API-SCHEMA.md](API-SCHEMA.md) for API integration
4. Follow [USER-JOURNEY.md](USER-JOURNEY.md) for user experience

### For QA Engineers
1. Start with [QA-EXECUTION-MATRIX.md](QA-EXECUTION-MATRIX.md) for test cases
2. Reference [FEATURE-TRACEABILITY-MATRIX.md](FEATURE-TRACEABILITY-MATRIX.md) for coverage
3. Use [BROKER-FAILURE-TEST-CASES.MD](BROKER-FAILURE-TEST-CASES.MD) for edge cases
4. Follow [FAILURE-SEQUENCE-DOC.md](FAILURE-SEQUENCE-DOC.md) for recovery tests

### For Architects
1. Start with [HLD.MD](HLD.MD) for system overview
3. Reference [END-TO-END-SEQUENCE-DIAGRAM.md](END-TO-END-SEQUENCE-DIAGRAM.md) for complete flow
3. Use [STATE-MACHINE.md](STATE-MACHINE.md) for state management
4. Follow [SYSTEM-CAPABILITIES-MATRIX.md](SYSTEM-CAPABILITIES-MATRIX.md) for capability mapping

### For New Team Members
1. Start with [SRS.MD](SRS.MD) to understand requirements
2. Reference [HLD.MD](HLD.MD) for architecture overview
3. Read [USER-JOURNEY.md](USER-JOURNEY.md) for user perspective
4. Explore [FOLDER-STRUCTURE.md](FOLDER-STRUCTURE.md) for project layout

---

## 📊 Document Statistics

| Metric | Count |
|--------|-------|
| Total Documents | 28 |
| Core Architecture | 4 |
| Technical Specifications | 5 |
| Workflows & Sequences | 10 |
| Integrations | 3 |
| Failure & Recovery | 2 |
| Quality Assurance | 3 |

---

## 🔄 Document Dependencies

```
SRS.MD (Requirements)
    │
    ├── HLD.MD (High-Level Design)
    │       │
    │       └── LLD.MD (Low-Level Design)
    │               │
    │               ├── BACKEND-SPEC.md
    │               ├── FRONTEND-SPEC.md
    │               └── API-SCHEMA.md
    │
    ├── WORKFLOW-SCHEMA.md (Workflows)
    │       │
    │       ├── FULL-SEQUENCE-DOCUMENT.md
    │       ├── PIPELINE-FLOW.md
    │       └── STATE-MACHINE.md
    │
    └── FEATURE-TRACEABILITY-MATRIX.md (Testing)
            │
            └── QA-EXECUTION-MATRIX.md
```

---

## 📝 Document Maintenance

| Action | Frequency | Owner |
|--------|-----------|-------|
| Review SRS/HLD | Per major release | Product + Engineering Lead |
| Update API Schema | Per API change | Backend Team |
| Update Test Matrix | Per feature | QA Team |
| Review State Machine | Per workflow change | Architecture Team |

---

**Last Updated**: December 2024  
**Maintained by**: Algo Trading System Engineering Team
