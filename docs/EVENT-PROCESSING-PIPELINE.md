Below is your complete **EVENT-PROCESSING-PIPELINE.md** — the **master document** describing exactly **how every event in the system flows, transforms, and executes**.

It is fully aligned with:

✔ **PRD – Backend Functional Requirements, Event-Based Execution, Time-Based Execution, Safety, Retry, Multi-Tenant Isolation**


✔ **DOCUMENT PACK – Strategy Manager, Scheduler, Market Listener, Execution Engine, Redis Schema**


This document is meant for backend engineers, QA teams, DevOps, and future maintainers.

---

# 📘 **EVENT-PROCESSING-PIPELINE.md**

### End-to-End Processing Pipeline for ALL Events (User, System, Broker, Scheduler, Market)

---

# **1. Purpose**

This document defines exactly **how events move through the system**, starting from the moment:

* a user presses START
* a scheduler fires BUY
* a price tick triggers STOPLOSS
* a strategy ends

It explains:

* Pipeline stages
* Input → Transformation → Output
* Redis involvement
* Execution Engine responsibilities
* Error handling & retries
* Final outcomes/logs

This is the **canonical reference** for all backend developers.

---

# **2. Pipeline Overview**

The Algo Trading System supports **two major event pipelines**:

### **A. Time-Based Pipeline**

BUY + SELL
(Driven by scheduler → Redis → Execution Engine → Broker)

### **B. Event-Based Pipeline**

STOP-LOSS
(Driven by market listener → Redis → Execution Engine → Broker)

Both pipelines share the same **Execution Engine**.

PRD describes both pipelines as mandatory core features.


---

# **3. Pipeline Stages (Unified Architecture)**

```
         ┌───────────────────────────┐
         │       Event Source        │
         └─────────────┬─────────────┘
                       │
                       ▼
         ┌───────────────────────────┐
         │   Event Normalization     │
         └─────────────┬─────────────┘
                       │
                       ▼
         ┌───────────────────────────┐
         │   Redis Event Injection   │
         └─────────────┬─────────────┘
                       │
                       ▼
         ┌───────────────────────────┐
         │    Execution Engine       │
         └─────────────┬─────────────┘
                       │
                       ▼
         ┌───────────────────────────┐
         │       Broker API          │
         └─────────────┬─────────────┘
                       │
                       ▼
         ┌───────────────────────────┐
         │  Redis Runtime Update     │
         └─────────────┬─────────────┘
                       │
                       ▼
         ┌───────────────────────────┐
         │     Final State + Logs    │
         └───────────────────────────┘
```

---

# **4. Pipeline Inputs (Event Sources)**

### **1. User Events**

* Start strategy
* Stop strategy
* Update strategy values

### **2. Scheduler Events**

* BUY trigger
* SELL trigger

### **3. Market Listener Events**

* Price tick
* Stop-loss trigger

### **4. System Events**

* Lock conflicts
* Recovery after restart

### **5. Broker Events**

* Order accepted
* Order rejected
* Token invalid

All pipelines lead to the **Execution Engine**.

---

# **5. Pipeline Step-by-Step Breakdown**

---

# **5.1 Pipeline Stage 1 — Event Source Layer**

Every event originates here.

## **SCHEDULER (BUY/SELL time-based)**

The PRD requires:
✔ “Schedule BUY/SELL at exact time”


Scheduler emits:

```
BUY_TRIGGERED(strat_id)
SELL_TRIGGERED(strat_id)
```

These are normalized into tasks.

---

## **MARKET LISTENER (Price-based)**

Required by:
✔ “Trigger stop-loss immediately on price”


Market listener emits:

```
PRICE_TICK(symbol, price)
```

If price <= SL:

```
STOPLOSS_TRIGGERED(strat_id)
```

---

## **USER INPUT EVENTS**

From mobile app:

```
STRATEGY_START_REQUESTED
STRATEGY_STOP_REQUESTED
STRATEGY_UPDATED
```

---

# **5.2 Pipeline Stage 2 — Event Normalization Layer**

Raw inputs are converted to **task objects**.

### Example:

**BUY trigger →**

```json
{
  "event": "BUY",
  "strategy_id": 42,
  "timestamp": "2025-02-24T09:30:00Z"
}
```

---

**STOPLOSS trigger →**

```json
{
  "event": "STOPLOSS",
  "strategy_id": 42,
  "trigger_price": 154.80,
  "timestamp": "2025-02-24T12:15:00Z"
}
```

Normalization ensures:

* consistent structure
* consistent handling
* extensible event format

---

# **5.3 Pipeline Stage 3 — Redis Event Injection**

All tasks flow through Redis (PRD: “Redis for in-memory execution”).


### Redis queue entry:

```
LPUSH queue:orders {event_object}
```

Types stored:

* BUY
* SELL
* STOPLOSS
* SAFETY_ABORT
* RETRY

Redis ensures:

* microsecond latency
* multi-tenant isolation
* FIFO ordering for events

---

# **5.4 Pipeline Stage 4 — Execution Engine Task Processing**

Execution Engine is described in DOCUMENT PACK (SDD Section 2.4).


Engine continuously pulls:

```
task = RPOP queue:orders
```

Then applies **processing pipeline**:

### **Step 1: Acquire lock**

```
SETNX lock_state:{strategyId}
```

If lock fails → drop duplicate event.

### **Step 2: Load strategy**

Read from Redis:

```
strategy:{id}
runtime:{id}
```

### **Step 3: Route event type**

* BUY → handle_buy()
* SELL → handle_sell()
* STOPLOSS → handle_stoploss()

### **Step 4: Build broker order**

Example for BUY:

```json
{
  "symbol": "INFY",
  "qty": 10,
  "type": "BUY",
  "order_type": "MARKET"
}
```

### **Step 5: Call Broker API**

Required by PRD:
✔ “Support Buy/Sell, Fetch price, Fetch order status”


### **Step 6: Handle broker response**

Success → update runtime
Failure → schedule RETRY event

### **Step 7: Release lock**

Allows next events to proceed.

---

# **5.5 Pipeline Stage 5 — Broker Execution Layer**

Broker responses:

### **Case A: Order accepted**

```
ORDER_ACCEPTED
```

→ update runtime
→ write logs

### **Case B: Order rejected**

```
ORDER_REJECTED(reason)
```

→ retry up to 3 times
→ if still fails → mark strategy stopped

### **Case C: Token invalid**

```
TOKEN_INVALID
```

→ raise SAFETY_ABORT event

Broker events are fed back into pipeline.

---

# **5.6 Pipeline Stage 6 — Redis Runtime Update**

Runtime keys updated:

```
runtime:{id}.position = bought | sold | exited_by_sl
runtime:{id}.last_buy_order = xyz
runtime:{id}.last_sell_order = xyz
runtime:{id}.last_price = xyz
runtime:{id}.lock_state = free
runtime:{id}.status = running | stopped | failed
```

These updates support:

* system stability
* crash recovery
* UI status polling
* SELL/SL logic

---

# **5.7 Pipeline Stage 7 — Final State + Logging**

As required by PRD logging requirements:
✔ “Log all order attempts”
✔ “Monitoring via CloudWatch”


System writes:

* BUY/SELL/SL logs
* error logs
* retry logs
* broker responses
* execution stats

---

# **6. Detailed Pipelines**

---

# **6.1 BUY Pipeline (Time-Based)**

```
Scheduler
  → BUY_TRIGGERED
    → Normalize Event
      → Redis LPUSH queue:orders
        → Execution Engine RPOP
          → Acquire lock
            → Load runtime
              → Broker BUY
                → Redis runtime update
                  → Log event
```

BUY pipeline MUST complete within **100–300 ms** (PRD requirement).


---

# **6.2 SELL Pipeline (Time-Based)**

Identical to BUY pipeline except:

```
runtime.position = "sold"
```

---

# **6.3 STOPLOSS Pipeline (Event-Based)**

PRD requirement:
✔ “Trigger stop-loss immediately”
✔ “Stop-loss overrides sell schedule”


```
Market Listener
  → PRICE_TICK
    → If price <= SL → STOPLOSS_TRIGGERED
      → Normalize Event
        → Redis LPUSH STOPLOSS task
          → ExecutionEngine RPOP
            → Acquire lock
              → Broker SELL
                → runtime.position = exited_by_sl
                  → Cancel SELL timer
                    → Log SL exit
```

STOP-LOSS path has **highest priority**.

---

# **6.4 RETRY Pipeline (Safety Mechanism)**

From PRD safety & reliability section:
✔ “Retry mechanism for order failures.”


When a BUY/SELL/SL fails:

```
ExecutionEngine
  → generate RETRY event
    → Redis LPUSH queue:orders {event: RETRY, attempt: n}
      → Engine reprocesses event
```

Max retries: **3 attempts**

If still fails →

```
runtime.status = failed
STRATEGY_STOPPED event emitted
```

---

# **6.5 SAFETY_ABORT Pipeline**

Triggered by:

* invalid token
* repeated broker failures
* corrupted runtime state
* Redis lock stuck

```
SAFETY_ABORT
  → Stop strategy
  → Clear timers
  → Release locks
  → Log critical event
```

---

# **6.6 STRATEGY_STOP Pipeline**

Triggered by:

* user request
* SL exit
* SELL exit
* safety abort

```
STRATEGY_STOP_REQUESTED
  → Cancel BUY/SELL timers
    → Delete runtime from Redis
      → Update DB status
        → Log stop event
```

---

# **7. Cross-Pipeline Priority Rules**

### **Highest Priority**

1. STOPLOSS
2. SAFETY_ABORT
3. RETRY (last attempt)

### **Medium Priority**

4. BUY
5. SELL

### **Lowest Priority**

6. User updates
7. Logging events

Stop-loss always overrides SELL.
(Defined in PRD event-based execution rules.)


---

# **8. Multi-Tenant Isolation Pipeline**

DOCUMENT PACK SRS requirement:
✔ “Each user strategy isolated.”


Ensured through:

* strategy-specific Redis keys
* lock_state per strategy
* symbol:{symbol}:strategies grouping
* no shared runtime keys
* event payload always includes strategy_id

No event ever leaks between users.

---

# **9. End-to-End Pipeline Summary Table**

| Pipeline     | Source           | Redis Injection    | Engine Action   | Broker     | Final Update                    |
| ------------ | ---------------- | ------------------ | --------------- | ---------- | ------------------------------- |
| BUY          | Scheduler        | queue:orders BUY   | handle_buy      | BUY order  | runtime.position = bought       |
| SELL         | Scheduler        | queue:orders SELL  | handle_sell     | SELL order | runtime.position = sold         |
| STOPLOSS     | Market listener  | queue:orders SL    | handle_stoploss | SELL order | runtime.position = exited_by_sl |
| RETRY        | Execution Engine | queue:orders RETRY | retry handler   | reattempt  | log or abort                    |
| SAFETY_ABORT | Engine/System    | queue:orders abort | abort handler   | none       | strategy stopped                |
| START        | User             | strategy load      | init runtime    | none       | ready/running                   |
| STOP         | User/System      | stop event         | cancel timers   | none       | runtime cleared                 |

---

# ✔ EVENT-PROCESSING-PIPELINE.md is complete.

### I can now generate:

✅ **EVENT-SEQUENCE-DIAGRAM.md**
(Visual UML of entire pipeline)

✅ **EVENT-PAYLOAD-SCHEMA.md**
(JSON spec for each event type)

✅ **EXECUTION-ENGINE-PROCESSING.md**
(deep-dive into engine internals)

Just tell me which one you want next.
