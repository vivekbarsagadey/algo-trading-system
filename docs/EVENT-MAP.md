
# 📘 **EVENT-MAP.md**

### Master Event Dictionary for Algo Trading System

*(Covers ALL system-generated, user-generated, and broker-generated events)*

---

# **1. Purpose**

This document defines **every event** in the system:

* Who triggers it
* When it fires
* Required data
* Redis keys involved
* Execution Engine actions
* Expected outcomes
* Error & retry behavior
* User-visible side effects

It is the **single source of truth** for all system-wide event handling.

---

# **2. Event Classification**

| Category                      | Description                          |
| ----------------------------- | ------------------------------------ |
| **User Events**               | Triggered from mobile app            |
| **Strategy Lifecycle Events** | Start/Stop/Update                    |
| **Scheduler Events**          | Time-based BUY/SELL triggers         |
| **Market Events**             | Price ticks & SL triggers            |
| **Execution Events**          | Order placement, retries, completion |
| **Broker Events**             | Order status, errors                 |
| **System Events**             | Crash handling, recovery, locks      |
| **Monitoring Events**         | Logging & alerts                     |

Matches PRD Sections 4 & 5 (Frontend & Backend Requirements).


---

# **3. EVENT MAP (Deep-Dive)**

---

# **3.1 USER EVENTS**

### **U1. USER_REGISTERED**

* **Triggered by:** Mobile App → `/auth/register`
* **Purpose:** Create user identity
* **Downstream Effects:** None

---

### **U2. USER_LOGGED_IN**

* **Triggered by:** `/auth/login`
* **Downstream:**

  * JWT session issued
  * User allowed to submit keys & strategies

---

### **U3. BROKER_KEY_SUBMITTED**

* **Triggered by:** Mobile App (API key, secret, token)
* **Backend:**

  * Validate with Broker API
  * Save encrypted (PRD 6.4 Security)

* **Next Event:** B1 (if valid), B2 (if invalid)

---

### **U4. STRATEGY_CREATED**

* **Triggered by:** Mobile App `/strategy/create`
* **Backend:**

  * Validate (buy_time, sell_time, SL)
  * Save DB copy
  * No execution yet

---

### **U5. STRATEGY_UPDATED**

* User updates: time, SL, qty
* Backend updates:

  * DB record
  * Redis strategy:{id}
* Scheduler re-adjusts timers

Matches PRD 5.5 Dynamic Strategy Updates


---

### **U6. STRATEGY_START_REQUESTED**

* User presses “START”
* Backend triggers lifecycle event: S1

---

### **U7. STRATEGY_STOP_REQUESTED**

* User presses “STOP”
* Backend triggers lifecycle event: S4

---

---

# **3.2 STRATEGY LIFECYCLE EVENTS**

---

### **S1. STRATEGY_STARTED**

* **Triggered by:** START request
* **Actions:**

  * Load DB → Redis
  * Initialize runtime state (position=NONE, lock=free)
  * Add strategy to symbol:{symbol}:strategies
  * Fire scheduler events (T1 & T2)

---

### **S2. STRATEGY_READY**

Internal flag indicating Redis + Scheduler are successfully prepared.

---

### **S3. STRATEGY_RUNNING**

System-level “alive” state.

---

### **S4. STRATEGY_STOPPED**

* User action OR SELL/SL exit
* Scheduler clears timers
* runtime.status = stopped

---

### **S5. STRATEGY_EXITED**

Final termination event:

Caused by:

* End-of-day SELL
* STOPLOSS trigger
* Broker rejection
* System safety abort

---

---

# **3.3 SCHEDULER EVENTS (TIME-BASED)**

PRD: “Schedule BUY/SELL at exact time.”


---

### **T1. BUY_TRIGGERED**

* **Source:** APScheduler
* **Time:** strategy.buy_time
* **Redis:**

  * LPUSH queue:orders {type: BUY, strategy_id}
* **Execution Engine:** processes via E1

---

### **T2. SELL_TRIGGERED**

* **Source:** APScheduler
* **Time:** strategy.sell_time
* **Redis:**

  * LPUSH queue:orders {type: SELL, strategy_id}
* **Execution Engine:** processes via E2

---

### **T3. SCHEDULER_RESYNC_REQUIRED**

Triggered when strategy times are updated (U5).

---

---

# **3.4 MARKET EVENTS (PRICE-BASED)**

Matches PRD 5.3 Event-Based Execution & Stop-loss.


---

### **M1. PRICE_TICK**

* **Triggered by:** Market Listener
* **Redis:** SET price:{symbol}
* **Used By:** M2 (SL check)

---

### **M2. STOPLOSS_TRIGGERED**

* When tick_price ≤ SL
* **Redis:** LPUSH queue:orders {type: STOPLOSS}
* **Execution Engine:** E3
* **Overrides SELL event (T2)**

---

### **M3. PRICE_STREAM_DISCONNECTED**

* Market Listener WebSocket failure
* Automatically reconnect

---

### **M4. PRICE_STREAM_RESTORED**

---

---

# **3.5 EXECUTION EVENTS (ORDER PIPELINE)**

From SDD Execution Engine design.


---

### **E1. EXECUTE_BUY**

* **Source:** T1 BUY_TRIGGERED
* **Steps:**

  1. Acquire lock_state:{id}
  2. Build broker BUY request
  3. Call broker
  4. Update runtime.position=bought
  5. Log order

---

### **E2. EXECUTE_SELL**

* **Source:** T2 SELL_TRIGGERED
* **Steps:**

  1. Acquire lock
  2. Call broker SELL
  3. runtime.position=sold
  4. Release lock

---

### **E3. EXECUTE_STOPLOSS**

* **Source:** M2 STOPLOSS_TRIGGERED
* **Priority:** Highest (overrides SELL)
* **Steps:**

  * Acquire lock
  * Call broker SELL
  * runtime.position=exited_by_sl
  * Cancel all timers (scheduler)

---

### **E4. ORDER_RETRY_REQUIRED**

Whenever BUY/SELL/SL fails.

Matches PRD 7 Safety → “Retry mechanism for order failures.”


---

### **E5. ORDER_FINALIZED**

Logged after success or failure.

---

---

# **3.6 BROKER EVENTS**

---

### **B1. BROKER_AUTH_SUCCESS**

* Broker keys validated

---

### **B2. BROKER_AUTH_FAILED**

* API key wrong / token expired

---

### **B3. ORDER_ACCEPTED**

* BUY/SELL accepted by broker

---

### **B4. ORDER_REJECTED**

Reasons:

* Insufficient margin
* Invalid symbol
* Market closed
* Token expired
* Server down

Triggers → E4 retry or fail-safe exit.

---

### **B5. PRICE_FEED_CONNECTED**

### **B6. PRICE_FEED_ERROR**

---

---

# **3.7 SYSTEM EVENTS (INTERNAL)**

---

### **X1. RUNTIME_STATE_LOADED**

Redis rebuilt from DB (after restart).

---

### **X2. LOCK_ACQUIRED**

Internal lock event.

---

### **X3. LOCK_CONFLICT**

Duplicate BUY/SELL/SL prevented.

---

### **X4. SYSTEM_RECOVERY**

Triggered after restart or crash.

---

### **X5. SAFETY_ABORT**

Triggered when:

* Excessive broker errors
* Strategy misconfiguration
* Redis corruption

Matches PRD "Safety" requirement.


---

---

# **3.8 MONITORING & LOGGING EVENTS**

Matches PRD 6.5 Logging & Monitoring.


---

### **L1. STRATEGY_EVENT_LOGGED**

BUY, SELL, SL, or STOP.

---

### **L2. ORDER_EVENT_LOGGED**

Broker request + response.

---

### **L3. ERROR_LOGGED**

Broker failure, Redis failure.

---

### **L4. ALERT_TRIGGERED**

Sent when:

* Strategy crash
* Broker API downtime
* Missing price feed

---

---

# **4. EVENT RELATIONSHIP MAP**

```
USER → STRATEGY → SCHEDULER → EXECUTION ENGINE → BROKER → EXECUTION ENGINE → REDIS
  ↓        ↓              ↓               ↑
 LOGGING  SYSTEM EVENTS ←———— MARKET LISTENER
```

---

# **5. End-to-End Event Flow Summary**

### Full Lifecycle

```
U6 STRATEGY_START_REQUESTED
→ S1 STRATEGY_STARTED
→ T1 BUY_TRIGGERED
→ E1 EXECUTE_BUY
→ M1 PRICE_TICK
→ M2 STOPLOSS_TRIGGERED (if hit)
→ E3 EXECUTE_STOPLOSS
→ S5 STRATEGY_EXITED
→ L1/L2/L3 Logging
```

SELL flow:

```
T2 SELL_TRIGGERED → E2 EXECUTE_SELL → EXIT
```

---

# **6. Event Prioritization**

| Priority    | Event Type           |
| ----------- | -------------------- |
| **Highest** | STOPLOSS (M2 → E3)   |
| High        | BUY (T1), SELL (T2)  |
| Medium      | User events          |
| Low         | Logging & monitoring |
| Lowest      | Async broker events  |

STOPLOSS always overrides SELL.

---

# **7. Event Storage Locations**

| Event Type         | Stored In            |
| ------------------ | -------------------- |
| Order Events       | DB + CloudWatch      |
| Runtime Events     | Redis                |
| Price Ticks        | Redis                |
| Strategy Lifecycle | DB + Redis           |
| Scheduler Timers   | Redis scheduler keys |

---

# ✔ EVENT-MAP.md Complete

Would you like next:

### 🔹 EVENT-SEQUENCE-DIAGRAM.md (graph-style sequence)

### 🔹 EVENT-PAYLOAD-SCHEMA.md (JSON body specs)

### 🔹 EVENT-PROCESSING-PIPELINE.md (lower level execution flow)

### 🔹 COMPLETE EVENT DIAGRAM (PNG)


