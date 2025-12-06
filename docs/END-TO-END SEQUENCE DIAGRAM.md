Below is your complete **END-TO-END SEQUENCE DIAGRAM.md**, integrating **ALL flows** from the moment a user opens the app → to trade execution → to strategy shutdown → to recovery flow.

This is the **master sequence diagram** representing the entire system behavior.

It is fully aligned with:

✔ PRD ()
✔ DOCUMENT PACK (SRS, SDD, Redis Schema, API Contract, etc.) ()
✔ All previously created documents (SRS, HLD, LLD, Workflow, Pipeline, State Machine, Traceability, QA Matrix)

If you want a **PNG version**, I can generate it.

---

# 📘 **END-TO-END SEQUENCE DIAGRAM.md**

### Complete System Execution: User → Mobile → Backend → Redis → Scheduler → Market Listener → Execution Engine → Broker → Database

---

# **0. Purpose**

This document provides a **complete, unified sequence diagram** showing **every component** interacting together as a single flow.

This is the most important diagram for:

* Architecture validation
* Engineering onboarding
* QA end-to-end testing
* Compliance & audit proofs

---

# **1. End-to-End Sequence Diagram (Full Flow in One Block)**

Below is the entire sequence from **App Launch → Registration → Broker Setup → Strategy Execution → BUY/SELL/SL → Stop → Shutdown → Recovery**.

---

# **2. Unified Text Sequence Diagram (PlantUML Style)**

```
@startuml

actor User
participant MobileApp
participant Backend
participant AuthService
participant BrokerConnector
participant StrategyService
participant StrategyManager
participant Scheduler
participant MarketListener
participant ExecutionEngine
database Redis
database DB
participant BrokerAPI

== App Launch ==

User -> MobileApp: Open App
MobileApp -> MobileApp: Check SecureStore for JWT
MobileApp -> Backend: GET /auth/validate (if JWT exists)
Backend -> AuthService: Validate Token
AuthService --> Backend: Valid / Invalid
Backend --> MobileApp: Response

== Registration/Login ==

User -> MobileApp: Enter email/password
MobileApp -> Backend: POST /auth/login or /auth/register
Backend -> AuthService: Authenticate
AuthService -> DB: Query/Insert user
DB --> AuthService: OK
AuthService --> Backend: JWT
Backend --> MobileApp: JWT token saved

== Broker API Setup ==

User -> MobileApp: Enter API Key, Secret, Token
MobileApp -> Backend: POST /broker/connect
Backend -> BrokerConnector: Validate credentials
BrokerConnector -> BrokerAPI: Check validity
BrokerAPI --> BrokerConnector: Valid
BrokerConnector -> DB: Save encrypted keys
DB --> BrokerConnector: OK
Backend --> MobileApp: Broker connected

== Strategy Creation ==

User -> MobileApp: Enter BuyTime, SellTime, SL, Qty, Symbol
MobileApp -> Backend: POST /strategy/create
Backend -> StrategyService: Validate inputs
StrategyService -> DB: Insert strategy
DB --> StrategyService: strategy_id
Backend --> MobileApp: strategy_id

== Strategy Start ==

User -> MobileApp: Tap START
MobileApp -> Backend: POST /strategy/start
Backend -> StrategyManager: Load strategy
StrategyManager -> DB: Fetch strategy
DB --> StrategyManager: Strategy data
StrategyManager -> Redis: Create strategy:{id}
StrategyManager -> Redis: Create runtime:{id}
StrategyManager -> Redis: Add id to symbol:{symbol}:strategies
StrategyManager -> Scheduler: Register BUY job
StrategyManager -> Scheduler: Register SELL job
Backend --> MobileApp: Strategy running

== BUY Execution ==

Scheduler -> Backend: BUY trigger at buy_time
Backend -> Redis: Push BUY event to queue:orders
ExecutionEngine -> Redis: Pop BUY event
ExecutionEngine -> Redis: Acquire runtime lock
ExecutionEngine -> BrokerConnector: Place BUY order
BrokerConnector -> BrokerAPI: BUY
BrokerAPI --> BrokerConnector: order_id
ExecutionEngine -> Redis: Update runtime (position=bought)
ExecutionEngine -> DB: Insert BUY log
ExecutionEngine -> Redis: Release lock
Backend --> MobileApp: Last action = BUY (via polling)

== STOPLOSS Execution (Price-Based) ==

MarketListener -> BrokerAPI: Subscribed to price feed
BrokerAPI --> MarketListener: Tick(price)
MarketListener -> Redis: Read stop_loss
alt price <= SL
    MarketListener -> Redis: Push STOPLOSS event
    ExecutionEngine -> Redis: Pop STOPLOSS event
    ExecutionEngine -> Redis: Acquire lock
    ExecutionEngine -> BrokerConnector: Place SELL
    BrokerConnector -> BrokerAPI: SELL
    BrokerAPI --> BrokerConnector: order_id
    ExecutionEngine -> Redis: Update runtime(position=exited_by_sl)
    ExecutionEngine -> DB: Insert SL log
    ExecutionEngine -> Redis: Release lock
    Scheduler -> Scheduler: Cancel BUY & SELL jobs
    Backend --> MobileApp: STOP-LOSS Triggered
end

== SELL Execution (Time-Based) ==

Scheduler -> Backend: SELL trigger at sell_time
Backend -> Redis: Push SELL event
ExecutionEngine -> Redis: Pop SELL event
ExecutionEngine -> Redis: Acquire lock
ExecutionEngine -> BrokerConnector: Place SELL
BrokerConnector -> BrokerAPI: SELL request
BrokerAPI --> BrokerConnector: order_id
ExecutionEngine -> Redis: Update runtime(position=sold)
ExecutionEngine -> DB: Insert SELL log
ExecutionEngine -> Redis: Release lock
Backend --> MobileApp: Last action = SELL

== Manual STOP ==

User -> MobileApp: Tap STOP
MobileApp -> Backend: POST /strategy/stop
Backend -> StrategyManager: Stop strategy
StrategyManager -> Scheduler: Cancel BUY/SELL
StrategyManager -> Redis: Delete strategy:{id}
StrategyManager -> Redis: Delete runtime:{id}
StrategyManager -> Redis: Remove id from symbol:{symbol}:strategies
StrategyManager -> DB: Update status=stopped
Backend --> MobileApp: STOPPED

== Backend Crash/Restart Recovery ==

Backend -> Redis: Read active strategy keys
alt Keys missing due to crash
    Backend -> DB: Read active strategies
    StrategyManager -> Redis: Recreate strategy:{id}
    Scheduler -> Scheduler: Recreate BUY/SELL jobs
    MarketListener -> Redis: Re-subscribe symbol strategies
end
Backend --> Logs: Recovery complete

@enduml
```

---

# **3. Detailed Narrative of End-to-End Flow**

The following narrative matches PRD Section 8 User Flow () and SRS Functional Requirements ().

---

## **3.1 App Launch → Authentication**

1. User opens the mobile app.
2. App checks stored JWT.
3. If expired → asks to login again.
4. Login/Registration handled via Auth Service + DB.

PRD Reference: User authentication flow


---

## **3.2 Broker API Key Setup**

1. User enters API Key, Secret, Token.
2. Backend validates via BrokerConnector → Broker API.
3. If valid → stored encrypted in DB.

PRD Reference: Broker Setup


---

## **3.3 Strategy Creation**

1. User enters buy time, sell time, stop-loss, quantity, symbol.
2. Backend validates rules (stop-loss mandatory).
3. Strategy saved to DB.

PRD Reference: Strategy Creation Requirements


---

## **3.4 Strategy Start**

1. User taps START.
2. Backend loads strategy into Redis:

   * strategy:{id}
   * runtime:{id}
   * symbol:{symbol}:strategies
3. BUY/SELL timers scheduled.
4. Market Listener is aware of strategy.

Matches SRS “Strategy Manager + Redis Runtime”


---

## **3.5 BUY Sequence**

Triggered at BUY time (**exact execution required**).

1. Scheduler emits BUY event.
2. Backend pushes event to Redis queue.
3. Execution Engine pulls event.
4. BUY order sent to broker.
5. Runtime updated.

PRD: “Execute BUY at exact time”


---

## **3.6 STOPLOSS Sequence**

Triggered by price feed:

1. MarketListener receives real-time tick.
2. Compares tick with stop_loss.
3. If price <= SL → generate STOPLOSS event.
4. Execution Engine immediately sells.
5. Strategy moved to STOPPED state.

PRD: “Stop-loss must trigger immediately”


---

## **3.7 SELL Sequence**

Triggered at sell_time:

1. Scheduler fires SELL event.
2. Execution Engine executes SELL.
3. Runtime updates to SOLD.
4. Strategy stops.

---

## **3.8 Manual STOP**

1. User taps STOP.
2. Scheduler jobs removed.
3. Redis keys deleted.
4. Strategy status updated.

---

## **3.9 Recovery Sequence (Crash Recovery)**

Backend restart scenario:

1. Backend checks Redis.
2. Missing keys → reconstruct from DB.
3. Scheduler re-registers jobs.
4. Market Listener re-subscribes strategies.

PRD: Reliability / Availability requirements

SRS 4.4 Availability


---

# **4. Component-Level Interaction Summary**

| Component        | Responsibility              |
| ---------------- | --------------------------- |
| Mobile App       | User UI, API calls          |
| FastAPI Backend  | Central orchestration       |
| Strategy Manager | Redis management            |
| Scheduler        | BUY/SELL time triggers      |
| Market Listener  | SL triggers via price feed  |
| Execution Engine | Processes orders            |
| Broker Connector | Communicates with exchanges |
| Redis            | Runtime state               |
| DB               | Persistent storage          |

Matches SDD architecture overview


---

# **5. End-to-End Guarantees**

Based on PRD + SRS:

✔ BUY executed at exact time (PRD 5.1)
✔ SELL executed at exact time (PRD 5.1)
✔ STOPLOSS immediate, top priority (PRD 5.1)
✔ Strategy isolation across users (PRD 5.1)
✔ Runtime state always in Redis (PRD 7)
✔ High-speed order execution <300ms (PRD 6.1)
✔ Redis microsecond lookup (PRD 6.1)
✔ Auto recovery after backend crash (PRD 6.2)

---

# ✔ **END-TO-END SEQUENCE DIAGRAM.md is complete.**

I can now generate:

### 📌 END-TO-END SEQUENCE DIAGRAM (PNG)

### 📌 COMPONENT INTERACTION DIAGRAM

### 📌 CROSS-COMPONENT EVENT MAP

### 📌 SYSTEM DATA-LIFECYCLE DOCUMENT

### 📌 BROKER-INTEGRATION-SEQUENCE.md

### 📌 REDIS-RUNTIME-FLOW.md

