# 📘 **SYSTEM-STATE-MACHINE.md**

### Algo Trading System – Strategy Lifecycle State Machine


# **0. Purpose**

This document defines the **complete state machine** governing the lifecycle of a trading strategy.

It ensures:

* Predictable behavior
* Safe transitions
* Clean execution flow
* Consistent system interpretation
* Clear boundaries for STOP, SL, BUY, SELL
* Multi-tenant correctness

This state machine governs both backend runtime (Redis) and UI state (Mobile).

---

# **1. Strategy States Overview**

| State              | Meaning                               |
| ------------------ | ------------------------------------- |
| **CREATED**        | Strategy exists in DB but not running |
| **READY**          | Validated, eligible to start          |
| **RUNNING**        | Redis loaded, scheduler active        |
| **WAITING_BUY**    | Running but BUY time has not come     |
| **BOUGHT**         | BUY executed                          |
| **WAITING_SELL**   | Waiting for sell time or SL condition |
| **EXITED_BY_SELL** | Sell executed normally                |
| **EXITED_BY_SL**   | Stop-loss triggered                   |
| **STOPPED**        | Manually stopped or system-stopped    |
| **FAILED**         | System or order failure               |

These match PRD operational expectations (BUY, SELL, STOPLOSS, STOP).


---

# **2. Unified State Machine Diagram (Text Form)**

```
CREATED
   │
   │  validate inputs / broker connected
   ▼
READY
   │
   │  user presses START
   ▼
RUNNING
   │
   ├──→ WAITING_BUY
   │         │
   │         │  buy_time reached (scheduler)
   │         ▼
   │       BOUGHT
   │         │
   │         │  wait until sell_time
   │         ▼
   │     WAITING_SELL
   │         ├── sell_time reached → EXITED_BY_SELL
   │         └── price <= SL → EXITED_BY_SL
   │
   │
   └── user presses STOP → STOPPED

EXITED_BY_SELL → STOPPED (final)

EXITED_BY_SL → STOPPED (final)

FAILED → STOPPED (final)
```

All FINAL STATES collapse into **STOPPED**.

---

# **3. Detailed State Definitions & Transitions**

---

## **3.1 STATE: CREATED**

### Meaning:

* Strategy saved to DB
* User has not activated it

### Entry Conditions:

* POST /strategy/create success

### Exit Conditions:

* User presses START
* System validates broker & strategy correctness

### Transitions:

```
CREATED → READY
```

---

## **3.2 STATE: READY**

### Meaning:

* Strategy configured properly
* Broker connected
* User can start automation

### Entry:

* Validation passed

### Exit:

* User presses START → move to RUNNING

### Transitions:

```
READY → RUNNING
```

---

## **3.3 STATE: RUNNING**

### Meaning:

* Redis keys created
* Timers scheduled
* Market listener tracking symbol

### Entry:

Triggered from READY by user start.

System performs:

```
Load strategy into Redis
Initialize runtime state
Register BUY & SELL jobs
Add strategy to symbol listener list
```

### Exit:

* STOP
* SL triggered
* SELL executed
* Failure/error event

### Allowed Transitions:

```
RUNNING → WAITING_BUY
```

---

## **3.4 STATE: WAITING_BUY**

### Meaning:

* Strategy active
* BUY time has not arrived

### Entry:

* Immediately after entering RUNNING

### Exit Conditions:

* buy_time reached (scheduler)

### Transitions:

```
WAITING_BUY → BOUGHT
WAITING_BUY → STOPPED (manual)
WAITING_BUY → FAILED (system error)
```

---

## **3.5 STATE: BOUGHT**

### Meaning:

* BUY order executed
* Position opened

### Entry Condition:

* Execution Engine completes BUY

### Entry Actions:

* runtime.position = "bought"
* Save buy log to DB
* Update Redis runtime

### Exit:

* Wait for sell_time
* OR SL hit

### Transitions:

```
BOUGHT → WAITING_SELL
BOUGHT → EXITED_BY_SL
BOUGHT → STOPPED (manual)
BOUGHT → FAILED
```

---

## **3.6 STATE: WAITING_SELL**

### Meaning:

* Bought position open
* Waiting for sell_time
* OR SL trigger

### Entry:

* Immediately after BOUGHT

### Exit Conditions:

* sell_time reached
* OR price <= stop_loss

### Transitions:

```
WAITING_SELL → EXITED_BY_SELL
WAITING_SELL → EXITED_BY_SL
WAITING_SELL → STOPPED
WAITING_SELL → FAILED
```

---

## **3.7 STATE: EXITED_BY_SELL**

### Meaning:

* Normal exit
* End-of-day SELL executed

### Entry:

* SELL order executed successfully

### Exit:

```
EXITED_BY_SELL → STOPPED
```

Final terminal state.

---

## **3.8 STATE: EXITED_BY_SL**

### Meaning:

* Danger price hit
* Exit immediately

### Entry:

* STOPLOSS event via Market Listener
* Execution Engine sells immediately

### Exit:

```
EXITED_BY_SL → STOPPED
```

Terminal.

---

## **3.9 STATE: STOPPED**

### Meaning:

* Strategy no longer active
* Redis keys deleted
* Scheduler jobs cancelled

### Entry Conditions:

* Manual STOP
* SL exit
* SELL complete
* Failure

### Allowed Next Transitions:

NONE (Terminal)

This matches PRD requirement: **strategy must not restart automatically**.


---

## **3.10 STATE: FAILED**

### Meaning:

* Critical system error or repeated broker failure
* Retries exhausted

### Entry Conditions:

* Broker API failures
* Redis lock timeout
* Scheduler errors
* Unexpected exceptions

### System Behavior:

```
Mark strategy as FAILED
Trigger STOP logic
Cancel timers
Delete Redis runtime
Update DB
Notify mobile
```

### Final Transition:

```
FAILED → STOPPED
```

---

# **4. Complete Transition Table**

| From → To                     | Trigger/Event           |
| ----------------------------- | ----------------------- |
| CREATED → READY               | Strategy validated      |
| READY → RUNNING               | User presses START      |
| RUNNING → WAITING_BUY         | Initialization success  |
| WAITING_BUY → BOUGHT          | buy_time reached        |
| WAITING_BUY → STOPPED         | User STOP               |
| WAITING_BUY → FAILED          | Internal error          |
| BOUGHT → WAITING_SELL         | Buy order executed      |
| BOUGHT → EXITED_BY_SL         | SL hit immediately      |
| BOUGHT → STOPPED              | User STOP               |
| WAITING_SELL → EXITED_BY_SELL | sell_time reached       |
| WAITING_SELL → EXITED_BY_SL   | price <= SL             |
| WAITING_SELL → STOPPED        | User STOP               |
| ANY ACTIVE → FAILED           | Critical system failure |
| FAILED → STOPPED              | Cleanup                 |
| EXITED_BY_SLL/SELL → STOPPED  | Automatic finalization  |

---

# **5. State Ownership by Components**

| State          | Primary Owner                      |
| -------------- | ---------------------------------- |
| CREATED        | DB                                 |
| READY          | Backend Validator                  |
| RUNNING        | Strategy Manager                   |
| WAITING_BUY    | Scheduler                          |
| BOUGHT         | Execution Engine                   |
| WAITING_SELL   | Scheduler + Market Listener        |
| EXITED_BY_SELL | Execution Engine                   |
| EXITED_BY_SL   | Market Listener + Execution Engine |
| STOPPED        | Strategy Manager                   |
| FAILED         | Backend Runtime                    |

---

# **6. State Machine Guarantees**

The state machine enforces:

### ✔ No double BUY

Only WAITING_BUY → BOUGHT is allowed.

### ✔ No BUY after SL

SL moves directly to EXITED_BY_SL → STOPPED.

### ✔ No SELL without BUY

SELL transition only allowed from WAITING_SELL.

### ✔ SL always takes priority

SL transitions override SELL.

### ✔ Strategy auto-terminates

All FINAL states end in STOPPED.

Matches PRD safety requirements


---

# **7. Error & Recovery Transitions**

### If system restarts:

```
STOPPED remains STOPPED
RUNNING requires Redis recovery
WAITING_BUY/SELL are timer-recoverable
BOUGHT can continue
FAILED always transitions to STOPPED
```

### If Redis runtime lost:

* Strategy enters FAILED → STOPPED

### If Market Listener disconnects:

* System retries silently
* If persistent → FAILED

---

# **8. Visual Summary (Human-Readable)**

```
CREATED
↓
READY
↓ (Start)
RUNNING
↓
WAITING_BUY
↓ (Buy)
BOUGHT
↓
WAITING_SELL
↓ (Sell) → EXITED_BY_SELL → STOPPED
↓ (SL)   → EXITED_BY_SL   → STOPPED
↓ (Stop) → STOPPED
↓ (Error) → FAILED → STOPPED
```

---

# ✔ SYSTEM-STATE-MACHINE.md is complete.

I can now generate any of the following:

### 📌 COMPONENT-DIAGRAM.png

### 📌 STATE-MACHINE-DIAGRAM.png

### 📌 FAILURE-MODE-DOCUMENT.md

### 📌 STRATEGY-RUNTIME-MAP.md

### 📌 SYSTEM-CAPABILITIES-MATRIX.md

