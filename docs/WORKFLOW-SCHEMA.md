# 📘 **WORKFLOW-SCHEMA.md**

### Algo Trading System – End-to-End Workflow & Event Schema

---

# **1. Overview**

This document defines **every operational workflow** used by the Algo Trading System:

* User onboarding workflow
* Broker setup workflow
* Strategy creation workflow
* Strategy activation workflow
* Redis runtime workflow
* Scheduler (BUY/SELL) workflows
* Market listener & stop-loss workflow
* Execution engine workflow
* Strategy stop workflow
* System failure & recovery workflows

All workflows match the PRD user flow and backend requirements.
✔ (Register → Connect Broker → Create Strategy → Start → BUY/SELL/SL → Stop)


---

# **2. Workflow Index**

1. User Registration & Login
2. Broker Setup
3. Strategy Creation
4. Strategy Activation
5. Redis Load & Runtime State Initialization
6. Scheduler Workflow (Time-based BUY/SELL)
7. Market Listener Workflow (Event-based STOP-LOSS)
8. Execution Engine Workflow
9. Strategy Stop Workflow
10. Error & Recovery Workflow
11. Multi-Tenant Isolation Workflow

---

# **3. Workflow 1 – User Registration & Login**

### **Step-by-step Flow**

```
User → Mobile App → /auth/register → DB insert → JWT issued
```

### **Flow Details**

1. User enters email & password (UI requirement)
2. Mobile app sends POST /auth/register
3. Backend:

   * Validates email format
   * Hashes password
   * Stores user in DB (users table)
4. JWT token is generated
5. Stored in SecureStore (mobile)
6. User is redirected to **Broker Setup** screen

### **State Changes**

| Component | Change               |
| --------- | -------------------- |
| DB        | New user row created |
| Mobile    | Saves JWT            |
| Backend   | None                 |

---

# **4. Workflow 2 – Broker Setup**

(PRD section 4.1 – Broker API Setup)


### **Flow**

```
User → Mobile → /broker/connect → Broker API Validation → DB → Redis(optional)
```

### **Steps**

1. User enters:

   * API Key
   * Secret Key
   * Access Token
2. Mobile sends POST /broker/connect
3. Backend:

   * Calls Zerodha API (`/user/profile`)
   * Validates credentials
   * Encrypts key/secret/token
   * Stores in DB (broker_keys table)
4. Returns success

### **State Changes**

| Component | Change                  |
| --------- | ----------------------- |
| DB        | broker_keys inserted    |
| Redis     | none (optional caching) |

---

# **5. Workflow 3 – Strategy Creation Workflow**

(PRD section: Strategy Creation Screen)


### **Flow**

```
User → Mobile App → /strategy/create → DB insert → Ready for activation
```

### **Steps**

1. User enters:

   * Symbol
   * Buy Time
   * Sell Time
   * Stop-loss (mandatory)
   * Quantity
2. Mobile sends POST /strategy/create
3. Backend:

   * Validates input
   * Ensures buy_time < sell_time
   * Ensures SL is present
   * Saves in DB (strategies table)
4. Returns strategy_id

### **State Changes**

| Component | Change                    |
| --------- | ------------------------- |
| DB        | New strategy row inserted |
| Redis     | None                      |

---

# **6. Workflow 4 – Strategy Activation Workflow**

(PRD section 8: User presses START)


### **Flow**

```
Mobile → /strategy/start → Strategy Manager → Redis → Scheduler Registration
```

### **Steps**

1. Mobile sends POST /strategy/start
2. Strategy Manager loads strategy from DB
3. Pushes strategy into Redis:

   * strategy:{id}
   * runtime:{id}
   * symbol:{symbol}:strategies
4. Scheduler registers BUY and SELL timers

### **State Changes**

| Component | Change                   |
| --------- | ------------------------ |
| Redis     | Strategy runtime created |
| Scheduler | Timers registered        |
| DB        | status → “running”       |

---

# **7. Workflow 5 – Redis Runtime Initialization**

(From Redis schema in Document Pack)


### **Keys Created**

```
strategy:{id}
runtime:{id}
symbol:{symbol}:strategies
```

### **Example**

#### strategy:{id}

```
{
 "symbol": "TCS",
 "buy_time": "09:30",
 "sell_time": "15:30",
 "stop_loss": 3500,
 "quantity": 10,
 "status": "running"
}
```

#### runtime:{id}

```
{
 "position": "none",
 "last_price": null,
 "lock_state": false
}
```

---

# **8. Workflow 6 – Scheduler Workflow (BUY/SELL)**

(PRD section 5.1 – Time-Based Execution)


### **Flow**

```
APScheduler → Redis queue:orders → Execution Engine
```

---

## **8.1 BUY Workflow**

### **Trigger**

At buy_time (e.g., 09:30:00)

### **Steps**

1. APScheduler triggers BUY
2. Scheduler worker fetches strategy from Redis
3. Pushes event:

```
{ "strategy_id": "...", "event": "BUY" }
```

into `queue:orders`
4. Execution Engine processes it

---

## **8.2 SELL Workflow**

### **Trigger**

At sell_time (e.g. 15:30:00)

### **Steps**

1. APScheduler triggers SELL
2. Same flow as BUY
3. Runtime position changes to “sold”

---

# **9. Workflow 7 – Market Listener & STOP-LOSS Workflow**

(PRD section 5.1 – Event-Based Execution)


### **Flow**

```
Broker WebSocket → Market Listener → Redis → Execution Engine
```

---

## **STOP-LOSS Trigger Steps**

1. Market Listener receives tick:

```
price = 3480
```

2. Compares with SL:

```
if price <= stop_loss:
    trigger SL
```

3. Pushes event:

```
{ "strategy_id": "...", "event": "STOPLOSS" }
```

→ `queue:orders`
4. Execution Engine consumes immediately
5. Strategy stops

### **Priority Rule**

STOP-LOSS overrides all other events.

---

# **10. Workflow 8 – Execution Engine Workflow**

(PRD: Backend must execute orders reliably)


### **Flow**

```
Execution Engine → Broker API → Redis runtime → DB logs
```

### **Detailed Steps**

1. Worker pops event from `queue:orders`
2. Acquire lock: `runtime:{id}:lock_state = true`
3. Determines order type:

   * BUY
   * SELL
   * STOPLOSS
4. Calls broker.place_order()
5. Updates Redis runtime:

```
position = "bought" / "sold"
last_buy_order = "id"
last_sell_order = "id"
```

6. Writes order log to DB
7. Releases lock

---

# **11. Workflow 9 – Strategy Stop Workflow**

### **Triggered By**

* User presses STOP
* STOP-LOSS triggered
* Order failure after 3 retries

### **Flow**

```
Mobile → /strategy/stop → Strategy Manager → Redis → Scheduler Cancellation
```

### **Steps**

1. Backend marks strategy as stopped in DB
2. Deletes Redis keys:

   * strategy:{id}
   * runtime:{id}
3. Removes strategy ID from symbol mapping
4. Cancels scheduler jobs

---

# **12. Workflow 10 – Error & Recovery Workflow**

(PRD section 6.5 – Logging & Monitoring)


### **Scenarios**

### **A. Broker Failure**

* Execution Engine retries 3 times
* If still failing → STOP strategy
* Log error

### **B. Redis Down**

* Worker halts safely
* Alerts via CloudWatch

### **C. Missed Scheduler Trigger**

* If delay < 5 seconds → execute immediately
* Else → log “missed execution”

### **D. Market Listener WebSocket Disconnect**

* Auto-reconnect loop every 2 seconds

---

# **13. Workflow 11 – Multi-Tenant Isolation Workflow**

(PRD section 5.1 – Multi-Tenant Isolation)


### **Rules**

1. Strategy is always tied to user_id
2. Redis keys never overlap:

   * `strategy:{id}`
   * `runtime:{id}`
3. Symbol mapping list ensures correct SL checks
4. Lock states prevent duplicate trades
5. DB access is always filtered by user_id

---

# **14. End-to-End Unified Workflow (Human Readable)**

This combines entire PRD user flow:


```
1. User registers → login
2. User adds broker API keys → validated → stored
3. User creates strategy (BUY time, SELL time, SL, qty)
4. User presses START
5. Backend:
     - Store strategy in DB
     - Load into Redis
     - Register BUY + SELL timers
     - Subscribe to symbol
6. Market Listener starts monitoring live price
7. At buy_time → BUY
8. At sell_time → SELL
9. If price <= stop_loss → STOPLOSS → SELL immediately
10. Strategy stops
11. User sees final status in app
```

---

# ✔ WORKFLOW-SCHEMA.md IS COMPLETE

I can now generate:

### ✅ PIPELINE-FLOW.md (developer-level workflows)

### ✅ EVENT-MAP.md (all event types + producers/consumers)

### ✅ STATE-MACHINE.md (strategy lifecycle state machine)

### ✅ COMPONENT-DIAGRAM.png

### ✅ END-TO-END SEQUENCE DIAGRAM

