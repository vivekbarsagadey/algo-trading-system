# 📘 **FAILURE-SEQUENCE-DOC.md**

### Detailed Failure Sequences, Safety Actions & Recovery Logic

This document covers:

* All possible failure points
* Order of events when failure occurs
* How the Execution Engine reacts
* What Redis updates happen
* What logs are generated
* How the system recovers safely
* Final strategy state after recovery

---

# **1. MASTER FAILURE SEQUENCE MAP**

Every failure falls into **one of 7 universal categories**:

| Failure Category          | Trigger Source     |
| ------------------------- | ------------------ |
| Broker Timeout            | Broker API         |
| Broker Rejection          | Broker API         |
| Token Expired             | Broker API         |
| Network/Connectivity Drop | Internal or Broker |
| Redis Lock Stuck          | Execution Engine   |
| Price Feed Failure        | Market Listener    |
| Strategy State Corruption | Redis              |

Every category results in a **predictable failure sequence**.

---

# **2. FAILURE SEQUENCE: BROKER TIMEOUT**

### **Trigger:**

Execution Engine sends BUY/SELL/SL → broker does NOT respond in time (PRD reliability requirement).


---

## **Sequence**

```
1. Engine sends broker order
2. No response within timeout window (e.g., 2 seconds)
3. Engine marks event as TIMEOUT
4. Engine generates RETRY event
5. Redis queue receives RETRY
6. Execution Engine retries order (max 3)
```

---

## **Recovery Logic**

| Attempt | Action                                  |
| ------- | --------------------------------------- |
| Retry 1 | retry once                              |
| Retry 2 | retry again                             |
| Retry 3 | retry final time                        |
| Retry 4 | **NOT ALLOWED** → triggers SAFETY_ABORT |

---

## **Final Outcome**

* If retry succeeds → strategy continues normally
* If retry fails after 3 attempts → strategy forcibly stopped
* runtime.position remains **unchanged**
* Logs written for every attempt

---

# **3. FAILURE SEQUENCE: BROKER REJECTION**

### **Trigger:**

Broker responds with error → “Order Rejected”.
(PRD explicitly requires rejection handling + safe abort)


---

## **Sequence**

```
1. Engine sends order
2. Broker returns REJECTED
3. Engine logs rejection
4. Engine pushes RETRY event into Redis
5. Retry policy same as timeout
6. After 3 failures → SAFETY_ABORT
```

---

## **Possible Rejection Reasons**

* Insufficient balance
* Market closed
* Stock not tradable
* Invalid order type
* Rate limit exceeded

---

## **Final Outcome**

* Strategy safely stops after last retry
* User notified (via mobile status polling)
* All logs stored in DB + CloudWatch

---

# **4. FAILURE SEQUENCE: TOKEN INVALID / EXPIRED**

### **Trigger:**

Broker returns **TOKEN_INVALID** (session expired).
(SRS requires token handling and safe abort)


---

## **Sequence**

```
1. Engine sends order
2. Broker returns TOKEN_INVALID
3. Engine immediately halts retries
4. Engine pushes SAFETY_ABORT
5. Strategy moves into 'failed' state
```

---

## **Why RETRY is NOT allowed?**

PRD: expired token cannot be retried
→ user must reconnect broker manually


---

## **Final Outcome**

* Strategy stopped
* User sees "Broker connection expired"
* Must re-authenticate broker

---

# **5. FAILURE SEQUENCE: NETWORK FAILURE (ENGINE → BROKER)**

### **Trigger:**

Network issue in your AWS cluster or broker side.

---

## **Sequence**

```
1. Engine sends order
2. No connection to broker
3. Error caught: "Network unreachable"
4. RETRY event generated
5. Standard 3-attempt retry policy applies
```

---

## **If all retries fail:**

```
→ SAFETY_ABORT
→ Strategy moved to failed state
```

This preserves safety.

---

# **6. FAILURE SEQUENCE: REDIS LOCK STUCK**

### **Trigger:**

Lock key not released due to crash.

```
lock_state:{strategyId} = "locked"
```

Engine cannot process next event.

---

## **Sequence**

```
1. Engine attempts SETNX lock
2. Lock fails (already locked)
3. Engine waits lock timeout threshold (e.g., 3 sec)
4. Engine marks lock as stale
5. Engine removes lock key
6. Engine retries event
```

DOCUMENT PACK requires safe lock handling.


---

## **Final Outcome**

* Engine self-recovers
* No strategy corruption
* No manual intervention required

---

# **7. FAILURE SEQUENCE: MARKET PRICE FEED DROPPED**

### **Trigger:**

WS feed stops sending ticks.
(PRD requires live SL monitoring)


---

## **Sequence**

```
1. Market Listener detects no ticks for > N seconds
2. Listener marks symbol feed as stale
3. Execution Engine suspends SL triggers temporarily
4. Resume when feed reconnects
```

Stop-loss **does NOT** trigger during stale feed.

---

## **Final Outcome**

* No orders executed when blind
* SL triggers resume safely after reconnection
* System logs the feed outage

---

# **8. FAILURE SEQUENCE: STOP-LOSS FAILURE**

### **Critical Condition:**

SL trigger must ALWAYS override SELL schedule.
(PRD strict SL priority rule)


---

## **Sequence**

```
1. Market price hits SL
2. SL event generated
3. Redis queue receives STOPLOSS event
4. Execution Engine attempts SELL
   - If SELL fails → RETRY
   - After retries → SAFETY_ABORT
```

If system fails completely before executing SL (extremely rare):

```
Engine recovers → reads last price from Redis → sees SL condition still true → executes SL
```

SL cannot be skipped.

---

# **9. FAILURE SEQUENCE: STRATEGY STATE CORRUPTION**

### **Trigger:**

Redis value missing / malformed.

---

## **Sequence**

```
1. Engine loads runtime:{id}
2. Schema mismatch detected
3. Engine generates SAFETY_ABORT
4. Strategy transitions to failed state
5. Developer visible log created
```

DOCUMENT PACK SDD requires strict schema enforcement.


---

# **10. FAILURE SEQUENCE DURING STARTUP (COLD START RECOVERY)**

### **Trigger:**

Server restarts due to deployment, crash, or scaling.

---

## **Sequence**

```
1. Backend restarts
2. Loads strategies from DB
3. Rebuilds Redis runtime
4. Resubscribes Market Listener
5. Reinitializes Timers (BUY/SELL)
6. Picks up any pending events
```

This allows **safe continuation** of all running strategies.

---

# **11. FAILURE SEQUENCE WHEN STOPPING STRATEGY**

### Failure Mode: stop requested during an active BUY/SELL

```
1. User sends STOP command
2. Engine pauses incoming events
3. Ongoing order allowed to finish OR safely aborted
4. All timers cancelled
5. Redis entries deleted safely
```

If stop occurs while a BUY is being retried:
→ retries are canceled immediately.

---

# **12. COMPLETE FAILURE DECISION TREE**

```
               ┌──────────────┐
               │ Broker Error? │
               └───────┬──────┘
                       │
        ┌──────────────┼──────────────┐
        │               │              │
   TIMEOUT        REJECTED        TOKEN_INVALID
        │               │              │
  RETRY (max 3)    RETRY (max 3)   SAFETY_ABORT
        │               │              │
        └───────┬──────┘              │
                │                     │
            If retries fail → SAFETY_ABORT
```

---

# **13. SYSTEM-WIDE SAFETY GUARANTEES**

The system guarantees (per PRD and SRS):

### ✔ Stop-loss ALWAYS triggers

### ✔ No duplicate BUY/SELL orders

### ✔ No overlapping events (lock-system enforced)

### ✔ No runaway retries

### ✔ Strategy never stays in half-executed state

### ✔ Restart-resilient execution

---

# **14. FINAL FAILURE STATES**

| State            | Meaning                                     |
| ---------------- | ------------------------------------------- |
| **failed**       | Strategy aborted due to unrecoverable error |
| **exited_by_sl** | Stop-loss executed successfully             |
| **sold**         | Normal sell                                 |
| **bought**       | First leg done                              |
| **none**         | No orders executed                          |

---

# ✔ FAILURE-SEQUENCE-DOC.md is complete.

I can now generate:

🔹 **FAILURE-SEQUENCE-DIAGRAM.md** (UML + PNG)
🔹 **RECOVERY-PROTOCOL.md**
🔹 **FAILURE-TEST-CASES.md** (QA Matrix)
🔹 **FAILURE-SIMULATION-SCRIPT.md** (Python test harness)

