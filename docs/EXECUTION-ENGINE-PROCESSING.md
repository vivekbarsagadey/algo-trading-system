# 📘 **EXECUTION-ENGINE-PROCESSING.md**

### Internal Processing Model for BUY, SELL, STOP-LOSS, RETRY, ABORT & Runtime Updates

---

# **0. Purpose**

The Execution Engine is the **core runtime component** described in the PRD and SRS:

* It consumes tasks from Redis
* Executes BUY/SELL/STOPLOSS
* Enforces safety, locking, and isolation
* Communicates with Broker API
* Updates Redis runtime state
* Logs all events
* Recovers gracefully from failures

PRD Requirements satisfied:
✔ Exact-time execution (BUY/SELL)
✔ Immediate price-based execution (STOPLOSS)
✔ Mandatory SL & safety controls
✔ Retry mechanism for broker failures
✔ Logging of all attempts
✔ Multi-tenant isolation


DOCUMENT PACK SRS Requirements satisfied:
✔ Execute time-based trades
✔ Execute stop-loss trades
✔ Log order events
✔ Maintain strategy runtime state in Redis


---

# **1. Execution Engine – High-Level Loop**

```
while True:
    task = Redis.RPOP(queue:orders)
    if task:
        process(task)
    sleep(1–5 ms)
```

### Why?

* Prevents heavy polling
* Ensures <1ms processing latency
* Supports 1000+ concurrent strategies (PRD scalability requirement)


---

# **2. Accepted Event Types**

| Event        | Source                  |
| ------------ | ----------------------- |
| BUY          | Scheduler               |
| SELL         | Scheduler               |
| STOPLOSS     | Market Listener         |
| RETRY        | Execution Engine        |
| SAFETY_ABORT | Execution Engine/System |
| FORCE_STOP   | User                    |

All events are **normalized** before entering the engine.
(Defined in EVENT-PROCESSING-PIPELINE)

---

# **3. Execution Engine Internal Pipeline (Core)**

```
1. Input Validation
2. Acquire Redis Lock
3. Load Strategy + Runtime
4. Evaluate Preconditions
5. Build Broker Request
6. Execute Broker Call
7. Handle Response (Success/Failure)
8. Update Runtime State
9. Release Lock
10. Write Logs
```

Each step is explained below.

---

# **4. Step-by-Step Internal Processing**

---

# **4.1 Step 1 — Input Validation**

Engine checks:

* event structure
* strategy_id exists
* strategy loaded in Redis
* broker keys valid

If any validation fails →
→ **SAFETY_ABORT** event is generated.

---

# **4.2 Step 2 — Acquire Redis Lock**

Uses:

```
SETNX lock_state:{strategyId} "locked"
```

If lock exists →
→ discard event (prevents duplicate BUY/SELL/SL).
(Safety requirement per PRD)


---

# **4.3 Step 3 — Load Strategy + Runtime**

Keys accessed:

* `strategy:{id}`
* `runtime:{id}`
* `symbol:{symbol}:strategies`
* `price:{symbol}` (for SL validation)

DOCUMENT PACK Redis schema reference


---

# **4.4 Step 4 — Evaluate Preconditions**

### BUY Preconditions:

```
runtime.position == NONE
current_time >= buy_time
```

### SELL Preconditions:

```
runtime.position == BOUGHT
current_time >= sell_time
```

### STOPLOSS Preconditions:

```
runtime.position == BOUGHT
tick_price <= stop_loss
```

If preconditions fail → ignore event (prevents illegal transitions).

---

# **4.5 Step 5 — Build Broker Request**

BUY example:

```json
{
  "symbol": "INFY",
  "quantity": 10,
  "transaction_type": "BUY",
  "order_type": "MARKET"
}
```

SELL example:

```json
{
  "symbol": "INFY",
  "quantity": 10,
  "transaction_type": "SELL",
  "order_type": "MARKET"
}
```

STOPLOSS uses SELL order.

PRD Broker Integration Requirement
✔ “Support Buy & Sell orders.”


---

# **4.6 Step 6 — Execute Broker API Call**

Engine calls:

```
BrokerConnector.place_order(order_payload)
```

Possible responses:

| Broker Result | Meaning            |
| ------------- | ------------------ |
| ACCEPTED      | Order placed       |
| REJECTED      | Error from broker  |
| TIMEOUT       | No response        |
| TOKEN_INVALID | Token expired      |
| SERVER_DOWN   | Broker unreachable |

---

# **4.7 Step 7 — Success/Failure Routing**

## **If SUCCESS:**

### BUY:

```
runtime.position = "bought"
runtime.last_buy_order = order_id
```

### SELL:

```
runtime.position = "sold"
runtime.last_sell_order = order_id
```

### STOPLOSS:

```
runtime.position = "exited_by_sl"
cancel all future timers
```

## **If FAILURE:**

PRD Requirement:
✔ “Retry mechanism for order failures.”


The engine:

```
If attempt < 3:
      Push RETRY event to Redis
Else:
      Push SAFETY_ABORT event
```

---

# **4.8 Step 8 — Update Runtime**

Redis updates:

```
runtime:{id}.position
runtime:{id}.last_order
runtime:{id}.updated_at
```

Runtime updates are atomic.

---

# **4.9 Step 9 — Release Lock**

```
DEL lock_state:{id}
```

Prevents deadlock & ensures next event can process.

---

# **4.10 Step 10 — Write Logs**

As required by PRD 6.5 Logging & Monitoring


Engine logs:

* event
* timestamp
* order payload
* broker response
* retries
* failures
* SL triggers
* BUY/SELL final state

Logs go to CloudWatch.

---

# **5. BUY, SELL, STOPLOSS Processing Flows**

---

# **5.1 BUY Flow**

```
Task Received → Acquire Lock → Validate Buy Conditions → 
Build BUY Request → Broker API → Update Runtime → Release Lock → Log
```

Time budget (PRD Performance): < 300ms


---

# **5.2 SELL Flow**

```
Task Received → Acquire Lock → Validate Sell Conditions → 
Build SELL Request → Broker API → Update Runtime → Release Lock → Log
```

---

# **5.3 STOPLOSS Flow**

STOPLOSS has **highest system priority**.
(Defined in PRD Event-Based Execution)


```
PRICE_TICK → STOPLOSS_TRIGGERED → LPUSH event → 
Engine RPOP → Lock → Validate SL → Broker SELL → 
runtime.position = exited_by_sl → cancel timers → Log
```

SL must execute in **real-time** (< 5ms from tick event).

---

# **6. RETRY Processing Flow**

```
event.retry_count += 1
if retry_count <= 3:
     LPUSH queue:orders (same event)
else:
     LPUSH SAFETY_ABORT
```

PRD requirement: Retry mechanism for order failures.


---

# **7. SAFETY_ABORT Processing Flow**

Triggered when:

* 3 retries failed
* broker token invalid
* runtime corruption
* lock never released
* unauthorized state transition

Flow:

```
Update runtime.status = failed
Cancel BUY/SELL timers
Clear lock_state
Log safety abort
```

Matches PRD “Safety Requirements.”


---

# **8. Strategy STOP Handling**

Triggered by:

* STOPLOSS exit
* SELL exit
* User STOP
* Safety abort
* Broker rejection chain

Engine performs:

```
Delete runtime:{id}
Delete lock_state:{id}
Delete strategy from symbol grouping
Cancel all scheduler jobs
Write STOP log
Update DB.status = stopped
```

---

# **9. Multi-Tenant Execution Engine Isolation**

As required by PRD 5.4
✔ “User A must not affect user B.”


Mechanisms:

* Per-strategy Redis keys
* Per-strategy lock
* StrategyId embedded in every event
* No shared mutable state
* Queued tasks processed independently

Engine processes thousands of strategies safely.

---

# **10. Execution Engine Crash Recovery**

DOCUMENT PACK availability requirement
✔ Auto-restart
✔ Reload strategies from DB


Flow:

```
On restart:
   Fetch all strategies from DB
   Rebuild strategy:{id}
   Rebuild runtime:{id}
   Resubscribe symbol groups
   Reschedule BUY/SELL timers
```

Execution resumes seamlessly.

---

# **11. Execution Engine Error Categories**

| Error Type               | Engine Action  |
| ------------------------ | -------------- |
| Broker timeout           | Retry          |
| Broker rejection         | Retry → Abort  |
| Token invalid            | Abort          |
| Price feed drop          | Wait → resume  |
| Redis unavailable        | Critical abort |
| JSON malformed           | Abort          |
| Illegal state transition | Abort          |

---

# **12. Performance Characteristics**

Matches PRD Non-Functional Requirements


| Operation        | Expected Time |
| ---------------- | ------------- |
| Redis read/write | < 1ms         |
| Event queue pop  | < 1ms         |
| BUY/SELL cycle   | 100–300ms     |
| SL trigger       | < 5ms         |
| Lock acquire     | < 1ms         |

---

# **13. Final Summary Diagram**

```
                ┌────────────────────────┐
                │   Redis queue:orders   │
                └───────────┬───────────┘
                            │
                        RPOP event
                            │
                            ▼
                ┌────────────────────────┐
                │   Execution Engine      │
                │  1. Lock                │
                │  2. Load Runtime        │
                │  3. Validate            │
                │  4. Build Order         │
                │  5. Broker Call         │
                │  6. Update Runtime      │
                │  7. Unlock              │
                │  8. Log                 │
                └───────────┬───────────┘
                            │
                            ▼
                      ┌──────────┐
                      │ Broker   │
                      └──────────┘
```

---

# ✔ EXECUTION-ENGINE-PROCESSING.md is complete.

I can now generate next-level technical documents:

### 🔹 BROKER-CONNECTOR-PROCESSING.md

### 🔹 REDIS-RUNTIME-STATE-MACHINE.md

### 🔹 EXECUTION-ENGINE-CODE-SKELETON.py (FastAPI + Redis + Broker SDK)

### 🔹 FULL EXECUTION ENGINE UML (PNG)


