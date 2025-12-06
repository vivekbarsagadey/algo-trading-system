# 📘 **BROKER-INTEGRATION-SEQUENCE.md**

### End-to-End Flow Between Backend ↔ Broker API (Buy, Sell, Stop-Loss, Authentication)

---

# **1. Purpose**

This document describes the **full integration lifecycle** between our system and the broker (e.g., Zerodha), including:

* API Key Validation
* Token Validation
* Buy & Sell Order Placement
* Stop-Loss Trigger Flow
* Order Status Polling (if broker requires it)
* Price WebSocket Streams
* Error handling
* Retry logic
* Redis runtime synchronization

Broker integration is part of **PRD 5.1 Functional Requirement #6**:
✔ *“Support Buy/Sell, Fetch price, Fetch order status, Validate API tokens.”*


And is defined in **SRS 3.2, 3.4, 3.5**.


---

# **2. High-Level Integration Architecture**

```
Mobile App
   |
   v
FastAPI Backend
   |
   ├── BrokerConnector (REST)
   ├── MarketListener (WebSocket)
   └── ExecutionEngine
          |
          └── Broker API (BUY/SELL/Fetch Status)
```

---

# **3. Redis Keys Involved**

From Document Pack Part 5 (Redis Schema)


| Key                        | Purpose                                         |
| -------------------------- | ----------------------------------------------- |
| strategy:{id}              | Strategy static data                            |
| runtime:{id}               | Live trading state (position, last order, lock) |
| symbol:{symbol}:strategies | List of strategies using same symbol            |
| queue:orders               | BUY/SELL tasks for Execution Engine             |
| lock_state                 | Ensures no duplicate BUY/SELL                   |

---

# **4. Broker Integration – End-to-End Sequence Diagram**

Below is a single combined UML flow for entire broker integration:

```
@startuml

actor User
participant MobileApp
participant Backend
participant BrokerConnector
database DB
database Redis
participant ExecutionEngine
participant MarketListener
participant BrokerAPI

== API Key Validation ==

User -> MobileApp: Enter API key + secret + token
MobileApp -> Backend: POST /broker/connect
Backend -> BrokerConnector: Validate Credentials
BrokerConnector -> BrokerAPI: Validate token + key
BrokerAPI --> BrokerConnector: Valid/Invalid
alt valid
    BrokerConnector -> DB: Save encrypted keys
    Backend --> MobileApp: Success
else invalid
    Backend --> MobileApp: Invalid Credentials
end

== Price Streaming (WebSocket) ==

MarketListener -> BrokerAPI: Subscribe(Symbol)
BrokerAPI --> MarketListener: Tick(price)
MarketListener -> Redis: Update last_price
MarketListener -> Redis: If price <= stop_loss → PUSH STOPLOSS event

== BUY Order Execution ==

ExecutionEngine -> Redis: Pop BUY event from queue:orders
ExecutionEngine -> Redis: Acquire lock(runtime.lock_state)
ExecutionEngine -> BrokerConnector: Place BUY Order
BrokerConnector -> BrokerAPI: BUY(symbol, qty)
BrokerAPI --> BrokerConnector: order_id
BrokerConnector --> ExecutionEngine: order_id
ExecutionEngine -> Redis: Update runtime(position=bought, last_buy_order=order_id)
ExecutionEngine -> DB: Log BUY
ExecutionEngine -> Redis: Release lock

== SELL Order Execution ==

ExecutionEngine -> Redis: Pop SELL event
ExecutionEngine -> Redis: Acquire lock
ExecutionEngine -> BrokerConnector: Place SELL Order
BrokerConnector -> BrokerAPI: SELL(symbol, qty)
BrokerAPI --> BrokerConnector: order_id
ExecutionEngine -> Redis: Update runtime(position=sold, last_sell_order=order_id)
ExecutionEngine -> DB: Log SELL
ExecutionEngine -> Redis: Release lock

== STOPLOSS Order Execution ==

MarketListener --> Redis: Push STOPLOSS event
ExecutionEngine -> Redis: Pop STOPLOSS event
ExecutionEngine -> Redis: Acquire lock
ExecutionEngine -> BrokerConnector: SELL (SL Exit)
BrokerConnector -> BrokerAPI: SELL
BrokerAPI --> BrokerConnector: order_id
ExecutionEngine -> Redis: Update runtime(position=exited_by_sl)
ExecutionEngine -> DB: Log STOPLOSS execution
ExecutionEngine -> Redis: Release lock

@enduml
```

---

# **5. Detailed Sequence Flows**

---

# **5.1 API Key & Token Validation Flow**

(Required by PRD – Broker Setup)

(SRS Section 3.2 Broker Setup)


### Steps:

1. User enters **API Key, Secret, Access Token**.
2. Mobile → Backend `/broker/connect`.
3. Backend calls broker endpoint:

   ```
   GET /session/token/validate
   ```
4. If valid → encrypt keys → store in DB.
5. Set `user:{id}.broker_connected = true` in Redis.

### Failure Scenarios:

| Case             | Backend Response                      |
| ---------------- | ------------------------------------- |
| Invalid token    | 401 – “Invalid access token”          |
| Expired token    | 401 – “Token expired, please refresh” |
| Wrong secret key | 403 – “Credentials mismatch”          |

---

# **5.2 BUY Order Sequence**

Required by **PRD 5.1 Time-Based Execution**


Described in **SRS 3.4 Execution Engine**


### Trigger:

Scheduler pushes BUY task → Redis queue.

### Steps:

1. ExecutionEngine pops `BUY` event.
2. Locks strategy runtime to prevent duplicates.
3. Builds order packet:

```
{
  "symbol": "INFY",
  "quantity": 10,
  "transaction_type": "BUY",
  "order_type": "MARKET"
}
```

4. BrokerConnector → BrokerAPI `/orders/place`.
5. Broker returns order_id.
6. Update Redis runtime:

```
runtime:{
   position: "bought",
   last_buy_order: <order_id>
}
```

7. Insert BUY log into DB.

### BUY Error Handling:

| Error                | System Behavior              |
| -------------------- | ---------------------------- |
| Network issue        | Retry 3 times (PRD Safety)   |
| Broker rejects order | Mark runtime as “buy_failed” |
| Duplicate BUY call   | Rejected due to Redis lock   |

---

# **5.3 SELL Order Sequence**

Identical structure to BUY.

Triggered by:

* Time-based SELL (scheduler)
* Manual STOP (if position open)

### Steps:

1. ExecutionEngine pops SELL event.
2. Acquire runtime lock.
3. Send SELL order.
4. Update runtime + logs.

### Key Rule:

✔ SELL is allowed **only if BUY was executed** (runtime.position == bought)

---

# **5.4 STOP-LOSS Sequence**

Required by PRD – *Immediate stop-loss execution*.


And SRS – *Monitor live price, trigger SL instantly.*


### Trigger Flow:

1. MarketListener gets tick via Broker WebSocket.
2. Compares tick price to runtime.stop_loss.
3. If price ≤ SL → pushes STOPLOSS event to Redis queue.

### Execution:

1. ExecutionEngine consumes STOPLOSS event.
2. Acquires lock.
3. BrokerConnector places SELL order.
4. Update runtime → `exited_by_sl`.
5. Cancel BUY/SELL timers for this strategy.

### Why this is critical?

✔ STOP-LOSS must override SELL schedule.
✔ SL execution must be <5ms after receiving the tick.
✔ SL must run even if SELL timer hasn't fired yet.

---

# **5.5 Order Status Polling (If Broker Requires It)**

Not mandatory in MVP (per PRD), but included for reliability.

Flow:

1. After placing order → ExecutionEngine calls
   `/orders/status?order_id=xyz`
2. Update runtime:

   * filled
   * partially_filled
   * rejected
3. Logs written.

---

# **5.6 Price Subscription (WebSocket) Flow**

Matches **SDD Market Listener component**.


### Steps:

```
MarketListener -> BrokerAPI: subscribe(symbol)
BrokerAPI -> MarketListener: tick stream
MarketListener -> Redis: update runtime.last_price
MarketListener -> Redis: if tick <= SL -> push STOPLOSS event
```

### Responsibility:

| Component       | Role                             |
| --------------- | -------------------------------- |
| MarketListener  | Receives live ticks              |
| Redis           | Stores current price and SL info |
| ExecutionEngine | Performs final SL SELL           |

---

# **5.7 Retry Logic for Broker Failures**

Required by PRD Safety Requirements.


### Retry Rules:

| Scenario             | Action                        |
| -------------------- | ----------------------------- |
| BUY/SELL API timeout | Retry 3 times                 |
| Order rejection      | Abort strategy                |
| Broker downtime      | Pause strategy & alert        |
| Duplicate event      | Redis lock prevents execution |

---

# **6. Failure & Recovery Scenarios**

---

## **6.1 If Broker API is Down**

1. ExecutionEngine detects failure.
2. Logs error.
3. Retries up to 3 times.
4. Marks runtime: `broker_unreachable`.
5. Notifies backend.

---

## **6.2 Backend Crash Recovery**

Matches PRD non-functional requirement: Reliability.


### Steps:

1. On restart → Strategy Manager reloads all Redis keys.
2. Scheduler re-registers BUY/SELL triggers.
3. MarketListener reconnects WebSocket.
4. ExecutionEngine resumes pending orders.

---

## **6.3 WebSocket Disconnect**

1. MarketListener receives disconnect event.
2. Attempts reconnect every 2 seconds.
3. No SL decisions made until price stream restored.

---

# **7. End-to-End Summary Table**

| Action        | MarketListener | ExecutionEngine | BrokerConnector | Redis              | DB   |
| ------------- | -------------- | --------------- | --------------- | ------------------ | ---- |
| Validate keys | ❌              | ❌               | ✅               | ❌                  | ✅    |
| BUY           | ❌              | Executes        | Places order    | Updates state      | Logs |
| SELL          | ❌              | Executes        | Places order    | Updates state      | Logs |
| STOPLOSS      | Detects price  | Executes        | Places order    | Updates state      | Logs |
| Price feed    | Receives ticks | ❌               | ❌               | Updates last_price | ❌    |

---

# ✔ BROKER-INTEGRATION-SEQUENCE.md is complete.

Would you like me to generate:

### 📌 broker-integration-diagram.png

### 📌 redis-broker-flow.md

### 📌 execution-engine-integration.md

### 📌 broker-failure-test-cases.md

