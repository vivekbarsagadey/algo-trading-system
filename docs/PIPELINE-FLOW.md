Below is your full **PIPELINE-FLOW.md** — the complete, production-ready pipeline flow document for the Algo Trading System.

This describes **every pipeline** in the system:

* Strategy ingestion pipeline
* Strategy runtime pipeline
* Time-trigger pipeline
* Price-trigger pipeline
* Execution pipeline
* Logging pipeline
* Multi-tenant flow separation pipeline
* Error & retry pipelines
* Cleanup pipelines
* User-facing sync pipelines

It is fully aligned with:
- Product Requirements Document
- Document Pack
- SRS, HLD, LLD, SCHEMA, Workflow Schema

This is **developer-level**, extremely detailed, and ready for implementation.

---

# 📘 **PIPELINE-FLOW.md**

### Algo Trading System – Complete Execution Pipelines

---

# **1. Overview**

This document explains every **data pipeline**, **processing pipeline**, **event flow**, and **execution workflow** in the Algo Trading System.

Each pipeline shows:

* Trigger
* Input → Transform → Output
* Producer & Consumer
* Redis interactions
* DB write points
* Error-handling segments
* Termination criteria

---

# **2. Pipeline Index**

| Pipeline Name                            | Purpose                            |
| ---------------------------------------- | ---------------------------------- |
| 1. User Onboarding Pipeline              | Register → Login → Token store     |
| 2. Broker Integration Pipeline           | Validate & save broker credentials |
| 3. Strategy Creation Pipeline            | Persist strategy                   |
| 4. Strategy Activation Pipeline          | Load into Redis & register jobs    |
| 5. Redis Runtime Initialization Pipeline | Setup runtime state                |
| 6. Time-Trigger BUY Pipeline             | Perform BUY at exact time          |
| 7. Time-Trigger SELL Pipeline            | Perform SELL at exact time         |
| 8. Price-Trigger STOPLOSS Pipeline       | Kill strategy when breached        |
| 9. Execution Engine Pipeline             | Order placement + logging          |
| 10. Status Sync Pipeline                 | Frontend polling                   |
| 11. Strategy Stop Pipeline               | Cleanup & rollback                 |
| 12. Retry & Failure Pipeline             | Broker/API failures                |
| 13. Multi-Tenant Isolation Pipeline      | Ensures separation                 |
| 14. Shutdown/Recovery Pipeline           | For crashes & reboots              |

---

# **3. Pipeline 1 – User Onboarding Pipeline**

### **Trigger**

User registers or logs in.

### **Flow**

```
Mobile App → /auth/register → DB → JWT → SecureStore
```

### **Pipeline Breakdown**

| Stage      | Description              |
| ---------- | ------------------------ |
| Input      | Email, password          |
| Validation | Format + password rules  |
| Transform  | Hash password            |
| Output     | DB insertion + JWT token |

### **Consumers**

* Mobile → stores JWT

---

# **4. Pipeline 2 – Broker Integration Pipeline**

(PRD Section 4.1 Broker Setup)


### **Trigger**

User enters:

* API key
* Secret key
* Access token

### **Flow**

```
Mobile → /broker/connect → Broker API → DB → OK
```

### **Transform**

* Encrypt credentials
* Validate via Zerodha
* Save to DB

### **Failure Path**

If invalid → return `BROKER_AUTH_FAILED`.

---

# **5. Pipeline 3 – Strategy Creation Pipeline**

### **Flow**

```
Mobile → /strategy/create → Validate → DB → Return strategy_id
```

### **Validation Rules**

* buy_time < sell_time
* stop_loss mandatory
* quantity > 0

### **Stored Output**

Row inserted into strategies table.

---

# **6. Pipeline 4 – Strategy Activation Pipeline**

(PRD: User presses START → system must load strategy into Redis)


### **Flow**

```
Mobile → /strategy/start
    → Strategy Manager
        → Fetch from DB
        → Write to Redis(strategy:{id})
        → Write to Redis(runtime:{id})
        → Add to Redis(symbol:{symbol}:strategies)
        → Scheduler registers BUY & SELL jobs
```

### **Output**

* Redis runtime created
* Scheduler timers active
* Strategy status = running

---

# **7. Pipeline 5 – Redis Runtime Initialization Pipeline**

### **Flow**

```
DB Strategy → Strategy Manager → Redis(strategy) + Redis(runtime)
```

### **Key Outputs**

#### Redis Key: strategy:{id}

Static strategy metadata.

#### Redis Key: runtime:{id}

Dynamic execution state.

---

# **8. Pipeline 6 – Time-Trigger BUY Pipeline**

(PRD Section 5.1 “Time-Based Execution”)


### **Trigger**

APScheduler reaches buy_time.

### **Flow**

```
Scheduler → Redis(queue:orders) → Execution Engine
```

### **Event Generated**

```
{
  event: "BUY",
  strategy_id: "...",
  timestamp: ...
}
```

### **Output**

* BUY event queued
* Execution Engine will handle order

---

# **9. Pipeline 7 – Time-Trigger SELL Pipeline**

### **Trigger**

APScheduler reaches sell_time.

### **Flow**

Same as BUY, but event = "SELL".

---

# **10. Pipeline 8 – Price-Trigger STOPLOSS Pipeline**

(PRD: STOPLOSS must execute immediately)


### **Trigger**

Market Listener receives a tick.

### **Flow**

```
Tick → Market Listener → SL Check
    → Push STOPLOSS into Redis queue
    → Execution Engine
```

### **Event Format**

```
{
  event: "STOPLOSS",
  strategy_id: "...",
  price: current_tick
}
```

### **Priority Rule**

STOPLOSS is highest priority.

---

# **11. Pipeline 9 – Execution Engine Pipeline**

This is the **core trading pipeline**.

### **Trigger**

Any event pushed into Redis queue (`BUY`, `SELL`, `STOPLOSS`).

### **Flow**

```
Execution Engine
    → dequeue event
    → acquire lock (runtime:{id}:lock)
    → place order via Broker API
    → update Redis runtime
    → write order_logs DB entry
    → release lock
```

### **Outputs**

* Real trade executed
* DB log stored
* Runtime updated

---

# **12. Pipeline 10 – Status Sync Pipeline (Mobile Polling)**

(PRD Section 4: “Basic Feedback”)


### **Trigger**

Mobile app polls every 5 seconds.

### **Flow**

```
Mobile → /strategy/status/{id} → Redis runtime → Mobile UI
```

### **Returned Fields**

```
status
position
last_action
last_price
```

---

# **13. Pipeline 11 – Strategy Stop Pipeline**

Triggered when:

* User presses STOP
* STOPLOSS executed
* Order failure after retries
* Symbol unavailable
* Runtime inconsistency

### **Flow**

```
API /strategy/stop
    → delete Redis keys
    → remove from symbol list
    → cancel scheduler jobs
    → update DB
```

### **Output**

Strategy halted in all layers.

---

# **14. Pipeline 12 – Retry & Failure Pipeline**

(PRD Section 5.1 Safety)


### **Triggers**

* Broker API timeout
* Order rejected
* Network issues
* Execution engine lock timeout

### **Flow**

```
Event failed
    → Retry 3 times
        → If still failing → STOP strategy
```

### **Output**

Strategy safely shut down to prevent financial risk.

---

# **15. Pipeline 13 – Multi-Tenant Isolation Pipeline**

(PRD: Multi-tenant isolation requirement)


### **Behavior**

Each strategy runs independently.

### **Isolation Points**

| Layer            | Isolation Method                                        |
| ---------------- | ------------------------------------------------------- |
| Redis            | strategy:{id}, runtime:{id}, symbol:{symbol}:strategies |
| DB               | user_id foreign keys                                    |
| Scheduler        | job IDs namespaced by strategy                          |
| Execution Engine | lock per strategy                                       |
| Market Listener  | symbol-level subscriber list                            |

### **Guarantee**

No user can affect another user’s strategy.

---

# **16. Pipeline 14 – Shutdown & Recovery Pipeline**

### **Trigger**

* Redis outage
* Process restart
* Backend deployment
* ECS/EKS restart

### **Recovery Flow**

```
On restart:
    → Reconnect Redis
    → Sync scheduler with Redis(strategy:{id})
    → Reattach listeners to symbol lists
    → Resume pending events
```

### **Fail-Safe Rules**

* If strategy runtime corrupted → STOP strategy
* Log critical event

---

# **17. Full System Pipeline (Human View)**

Combining all pipelines:

```
User registers → login → set broker keys
→ create strategy → start strategy
→ backend loads into Redis → scheduler active → price listener active
→ BUY or STOPLOSS or SELL event occurs
→ event pushed to Redis queue
→ execution engine consumes event
→ order placed → runtime updated → DB logged
→ strategy continues or stops
→ frontend polls for status
```

This perfectly matches PRD User Flow (Section 8):


---

# ✔ PIPELINE-FLOW.md COMPLETE

If you want next:

### ✅ EVENT-MAP.md (All events, producers, consumers, payload structures)

### ✅ STATE-MACHINE.md (Strategy lifecycle state diagram)

### ✅ ACTOR-FLOW.md (Breakdown per actor: User, Scheduler, Engine, Listener)

### ✅ COMPONENT-DIAGRAM.png

### ✅ FULL-SEQUENCE-DOCUMENT.md

