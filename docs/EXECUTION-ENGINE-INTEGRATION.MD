# 📘 **redis-broker-flow.md**

### Detailed Runtime Flow Between Redis, Broker API, Execution Engine & Scheduler

---

# **0. Purpose**

This document explains every **runtime interaction** involving Redis (state storage & event routing) and Broker Integration (BUY/SELL/SL).

Redis is the **single source of truth** for:

* Strategy runtime state
* Price updates
* Execution events
* Buy/Sell scheduling
* Stop-loss trigger pipeline
* Multi-tenant isolation

Redis + Broker is the heart of Algo Trading Execution as described in:

* **PRD 5.1 Functional Requirements (BUY, SELL, SL)**

* **PRD 7 Safety & Reliability Requirements (Stop-loss priority, retries)**

* **SRS Strategy Execution + Redis Schema**

---

# **1. Redis Key Architecture**

From Document Pack → Redis Structure

| Key                          | Purpose                                                       |
| ---------------------------- | ------------------------------------------------------------- |
| `strategy:{id}`              | Strategy static config (symbol, buy_time, sell_time, SL, qty) |
| `runtime:{id}`               | Live state (position, last_order, lock, timestamps)           |
| `symbol:{symbol}:strategies` | List of strategy IDs for that symbol                          |
| `queue:orders`               | FIFO queue for BUY/SELL/SL execution                          |
| `lock_state:{id}`            | Prevents duplicate BUY/SELL/SL orders                         |
| `price:{symbol}`             | Latest price received from Market Listener                    |

Redis patterns used:

* **SET / GET** for fast key lookups
* **LPUSH / RPOP** for event queues
* **SADD / SMEMBERS** for strategy grouping
* **SETNX** for locking

---

# **2. High-Level Redis ↔ Broker Data Flow**

```
Scheduler → Redis → Execution Engine → Broker API
Market Listener → Redis → Execution Engine → Broker API
Strategy Manager → Redis → Scheduler
Execution Engine → Redis → DB
```

---

# **3. Full Redis Runtime Lifecycle**

---

## **3.1 Strategy Start Flow**

Triggered when user taps **START**.

### Sequence:

```
1. StrategyManager loads DB → Redis
2. Redis SET strategy:{id}
3. Redis SET runtime:{id} = { position: none, lock: free }
4. Redis SADD symbol:{symbol}:strategies id
5. Scheduler registers BUY + SELL timers
```

### Why?

Redis makes the strategy **hot-loaded** and prevents DB round-trips during execution.

---

## **3.2 BUY Event Flow (Time-based)**

Matches PRD "Execute BUY at exact time"

### Sequence:

```
SCHEDULER → Redis:
    LPUSH queue:orders {type: BUY, strategy_id}

EXECUTION ENGINE:
    RPOP queue:orders
    SETNX lock_state:{id} = locked   (Atomic lock)
    GET strategy:{id}
    GET runtime:{id}
    Build BUY order packet
    Call BrokerAPI: BUY()
```

After execution:

```
Redis SET runtime:{id}.position = bought
Redis SET runtime:{id}.last_buy_order = order_id
SAVE to DB (BUY log)
DEL lock_state:{id}
```

### Redis role:

* Ensures BUY executes **once**
* Ensures BUY is synchronous and conflict-free
* Stores BUY results for SELL decisions later

---

## **3.3 SELL Event Flow (Time-based)**

Matches PRD “SELL at exact time”

Sequence is identical to BUY:

```
Scheduler → Redis LPUSH queue:orders SELL
ExecutionEngine → RPOP → Lock → BrokerAPI → Redis Update → DB Log → Unlock
```

Redis sets:

```
runtime:{id}.position = sold
runtime:{id}.last_sell_order = order_id
```

---

# **4. STOPLOSS Flow (Event-Based SL)**

PRD places heavy emphasis on SL execution being immediate & overriding SELL.

STOPLOSS involves **two Redis pipelines**:

* **Pipeline A:** MarketListener updates price
* **Pipeline B:** ExecutionEngine processes SL event

---

## **4.1 Price Feed Storage**

```
MarketListener → Redis SET price:{symbol} = tick_price
```

---

## **4.2 Stop-Loss Check**

```
MarketListener:
    GET runtime:{id}.stop_loss
    if tick_price <= SL:
        LPUSH queue:orders {type: STOPLOSS, strategy_id}
```

Redis queue is used **instead of direct execution** to ensure:

✔ Ordering
✔ Locking
✔ Deduplication
✔ Safety via ExecutionEngine

---

## **4.3 STOPLOSS Execution (Redis → Broker)**

```
ExecutionEngine:
    RPOP queue:orders  (STOPLOSS)
    SETNX lock_state:{id} = locked
    Build SELL order
    BrokerAPI: SELL()  (SL exit)
```

Redis after execution:

```
runtime:{id}.position = exited_by_sl
runtime:{id}.last_sl_order = order_id
runtime:{id}.terminated_at = timestamp
```

Scheduler effects:

```
DELETE future BUY/SELL timers
```

---

## **4.4 STOPLOSS Priority Rules (Redis Enforced)**

If STOPLOSS event arrives **before SELL time**, it must override SELL:

```
If runtime.position == bought:
    Process STOPLOSS
Else:
    Skip SL event
```

Redis ensures the above through:

* Position flag
* Queue event ordering
* Locking

---

# **5. Redis Locking Logic**

Redis locks prevent:

* Double BUY
* Double SELL
* Double SL
* Conflicting events (BUY & SL arriving close together)

Locking uses:

```
SETNX lock_state:{id} "locked"
```

If SETNX fails:

```
ExecutionEngine discards event → No duplicate action
```

---

# **6. Multi-Tenant Isolation (Redis)**

Matches PRD multi-user isolation requirement.

Redis isolation rules:

| Area            | Enforcement                                           |
| --------------- | ----------------------------------------------------- |
| Strategy state  | strategy:{id} scoped by ID                            |
| Symbol grouping | separate sets for each symbol                         |
| Queues          | Events carry strategy_id                              |
| Locks           | Per-strategy locks                                    |
| Price feed      | Shared, but SL logic uses strategy-specific SL values |

No user can ever access another user's strategy keys.

---

# **7. Redis ↔ Broker Failure Handling**

From PRD Section 7 (Safety & Reliability)

---

## **7.1 Broker Timeout**

### Sequence:

```
ExecutionEngine places BUY/SELL:
    Broker timeout → retry (x3)
If all fail → runtime.status = failed
```

Redis allows safe recovery:

* Lock is released
* Future events are canceled
* Strategy moves to STOPPED

---

## **7.2 Redis Crash Recovery**

As per SRS High Availability requirements

On backend restart:

1. StrategyManager reads DB
2. Reconstructs:

```
strategy:{id}
runtime:{id}
symbol:{symbol}:strategies
Scheduler BUY/SELL timers
```

Redis is stateless; recovery is always possible.

---

# **8. Redis Data Flow Tables**

---

## **8.1 BUY Flow**

| Step               | Component       | Redis Operation                  |
| ------------------ | --------------- | -------------------------------- |
| Load strategy      | StrategyManager | SET strategy:{id}                |
| Initialize runtime | StrategyManager | SET runtime:{id}                 |
| Trigger BUY        | Scheduler       | LPUSH queue:orders BUY           |
| Consume event      | ExecutionEngine | RPOP queue:orders                |
| Lock               | ExecutionEngine | SETNX lock_state:{id}            |
| Update             | ExecutionEngine | SET runtime:{id}.position=bought |

---

## **8.2 SELL Flow**

Identical pattern except:

```
runtime:{id}.position = sold
```

---

## **8.3 STOPLOSS Flow**

| Step           | Component       | Redis Operation                        |
| -------------- | --------------- | -------------------------------------- |
| Tick price     | MarketListener  | SET price:{symbol}                     |
| SL trigger     | MarketListener  | LPUSH queue:orders STOPLOSS            |
| Execute SL     | ExecutionEngine | RPOP queue:orders                      |
| Update SL exit | ExecutionEngine | SET runtime:{id}.position=exited_by_sl |
| Remove timers  | StrategyManager | DEL scheduler keys                     |

---

# **9. Full Combined Redis ↔ Broker Integration Diagram**

```
Scheduler ----> Redis ----> ExecutionEngine ----> BrokerAPI
                     ↑               |
                     |               v
MarketListener ----> Redis <----- Redis Locks
                     ↑
        StrategyManager (initial load)
```

---

# **10. Summary**

Redis is responsible for:

* Fast, atomic state management
* Event routing (BUY, SELL, SL)
* Symbol-group tracking
* Lock safety
* Real-time price-based triggers
* Crash recovery foundation

Broker integration is responsible for:

* Final execution of BUY/SELL orders
* Price feeding via WebSocket
* Token validation and order responses

Together, they form the **core execution pipeline** described in PRD & SRS.

---

# ✔ redis-broker-flow.md is complete.

Would you like me to generate:

### 🔹 redis-runtime-state-machine.md

### 🔹 execution-engine-integration.md

### 🔹 redis-key-expiration-policy.md

### 🔹 redis-failure-test-cases.md

### 🔹 redis-broker-flow (PNG Diagram)

