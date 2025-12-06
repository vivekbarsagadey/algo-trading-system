# 📘 **STATE-MACHINE.md**

### Master State Machine for Strategy Execution, Event Flow, and Failure Transitions


# **1. Overview**

A strategy in the Algo Trading System moves through **7 primary states**:

```
created → ready → running → bought → sold → exited_by_sl → stopped/failed
```

The Execution Engine & Scheduler cause transitions based on:

* BUY time
* SELL time
* STOPLOSS trigger
* Broker responses
* Retry logic
* User STOP request
* Safety abort conditions

---

# **2. Top-Level State Machine Diagram (Text UML)**

```
┌──────────┐
│ created  │
└────┬─────┘
     │ user starts strategy
     ▼
┌──────────┐
│  ready   │
└────┬─────┘
     │ scheduler triggers BUY
     ▼
┌──────────┐
│ running  │
└────┬─────┬────────────┬──────────────┐
     │     │             │              │
     │     │ STOPLOSS    │ SELL time    │ failure (abort)
     │     ▼             ▼              ▼
     │ ┌──────────┐  ┌──────────┐   ┌───────────┐
     │ │exited_by_sl│ │  sold    │   │  failed   │
     │ └──────────┘  └─────┬────┘   └──────┬────┘
     │                      │ user stop     │
     │                      ▼               ▼
     └──────────────────►┌──────────┐   ┌──────────┐
                         │ stopped  │   │ stopped  │
                         └──────────┘   └──────────┘
```

---

# **3. State Descriptions**

### **STATE: created**

* Strategy saved in DB
* No Redis runtime exists
* Not yet scheduled

---

### **STATE: ready**

Strategy has been **started** by the user.

Redis entries created:

```
strategy:{id}
runtime:{id} = position: none
```

Timers scheduled:

* BUY timer
* SELL timer

---

### **STATE: running**

The system is actively managing the strategy.

Events allowed:

* BUY
* STOPLOSS
* SELL
* RETRY
* SAFETY_ABORT
* STOP

---

### **STATE: bought**

BUY executed successfully.

```
runtime.position = "bought"
```

Waiting for:

* STOPLOSS trigger
* SELL trigger

---

### **STATE: sold**

SELL executed successfully via scheduler.

This is a terminal state unless:

* user manually restarts strategy
* new BUY scheduled (future strategy instance)

---

### **STATE: exited_by_sl**

Stop-loss executed before SELL.

This is a terminal state and overrides SELL.
(PRD priority rule)


---

### **STATE: stopped**

Strategy stopped by user OR after completing lifecycle.

* Redis keys deleted
* Timers canceled
* Runtime erased

---

### **STATE: failed**

Entered when:

* Broker retries exhausted
* Token invalid
* State corruption
* Lock stuck beyond recovery
* Stop-loss execution fails after retry

(PRD safety rules → fail-safe always)


---

# **4. State Transition Table**

| Current State | Event        | Next State   |
| ------------- | ------------ | ------------ |
| created       | start        | ready        |
| ready         | BUY time     | bought       |
| bought        | STOPLOSS     | exited_by_sl |
| bought        | SELL time    | sold         |
| running       | failure      | failed       |
| running       | stop request | stopped      |
| bought        | stop request | stopped      |
| sold          | stop request | stopped      |
| exited_by_sl  | stop         | stopped      |
| failed        | stop         | stopped      |

---

# **5. Event-Driven Transitions**

---

## **5.1 BUY Event Transition**

### Preconditions:

* `runtime.position == none`
* Broker token valid

### Transition:

```
ready → bought
running → bought
```

Updates:

```
runtime.position = "bought"
```

---

## **5.2 SELL Event Transition (Scheduler)**

### Preconditions:

* `position == bought`

### Transition:

```
bought → sold
```

---

## **5.3 STOPLOSS Event Transition (Market Listener)**

PRD: STOPLOSS overrides SELL


### Preconditions:

* `position == bought`
* price ≤ stop_loss

### Transition:

```
bought → exited_by_sl
```

Action:

* Cancel SELL timer
* Log SL exit

---

## **5.4 RETRY Event Transition**

Retry does **NOT** change strategy state.

Retries apply to:

* BUY failure
* SELL failure
* SL failure

If retry #3 fails:

```
→ failed
```

---

## **5.5 SAFETY_ABORT Transition**

Caused by:

* token invalid
* corrupted runtime
* repeated failures
* lock stuck
* invalid transition

### Transition:

```
running → failed
```

---

## **5.6 STOP Event Transition (User Action)**

Regardless of position:

```
any_non_terminal_state → stopped
```

Engine deletes:

* runtime
* symbol grouping
* timers

---

# **6. Execution Engine Internal State-Machine**

Based on SDD Execution Engine Model.


```
┌───────────────┐
│  idle          │
└───────┬────────┘
        │ event read from Redis
        ▼
┌───────────────┐
│  validating   │
└───────┬────────┘
        │ valid
        ▼
┌───────────────┐
│  locked       │ (SETNX)
└───────┬────────┘
        │ strategy load OK
        ▼
┌───────────────┐
│  executing    │ (BUY/SELL/SL)
└───────┬────────┘
        │ broker success
        ▼
┌───────────────┐
│  updating     │ runtime update
└───────┬────────┘
        │ done
        ▼
┌───────────────┐
│  unlocking    │ DEL lock
└───────┬────────┘
        │
        ▼
┌───────────────┐
│   idle        │
└───────────────┘
```

Failures during ANY stage:

* Return to idle via RETRY or SAFETY_ABORT
* Lock is always released
* Runtime is always consistent

---

# **7. STOPLOSS Priority State-Machine (Safety)**

```
                  STOPLOSS TRIGGERED
                           │
                           ▼
                 ┌───────────────────┐
                 │ sl_pending        │
                 └─────────┬─────────┘
                           │ Execute SELL
                           ▼
                 ┌───────────────────┐
                 │ exited_by_sl      │
                 └───────────────────┘
```

SELL timer is **canceled** as soon as SL enters `sl_pending`.

---

# **8. Combined BUY → SELL → STOPLOSS State Flow**

```
ready
  │ BUY
  ▼
bought
  ├── STOPLOSS → exited_by_sl → stopped
  └── SELL → sold → stopped
```

---

# **9. Terminal States**

Terminal states have **no outgoing transitions**:

* sold
* exited_by_sl
* failed
* stopped

To restart a strategy:

```
stopped → start → ready
```

PRD requires simple restart flow.


---

# **10. State-Machine Safety Guarantees**

### ✔ No double BUY

(lock prevents parallel execution)

### ✔ No double SELL

(runtime.position protects this)

### ✔ STOPLOSS always overrides SELL

(defined by PRD)


### ✔ Strategy never stuck in inconsistent state

(safety abort + retries)

### ✔ Redis runtime always consistent

(atomic update rules)

### ✔ After restart → state reconstructed

(from DB + Redis)

---

# ✔ STATE-MACHINE.md is complete.

I can now generate:

1️⃣ **STATE-MACHINE-SEQUENCE-DIAGRAM.md**
2️⃣ **STATE-MACHINE-UML-PNG**
3️⃣ **RUNTIME-STATE-SCHEMA.md**
4️⃣ **STATE-MACHINE-TEST-CASES.md**

Tell me which one you want next.
