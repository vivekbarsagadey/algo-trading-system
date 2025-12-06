Below is your **FULL-SEQUENCE-DOCUMENT.md** — a complete, production-grade **Sequence Flow Document** for the Algo Trading System.

This is deeply aligned with:

- Product Requirements Document (PRD)
- Document Pack
- SRS, HLD, LLD, Schema, Workflow-Schema & Pipeline-Flow

This document shows **all sequence diagrams in text form**, covering:

* User onboarding
* Broker setup
* Strategy creation
* Strategy start
* BUY sequence
* SELL sequence
* STOPLOSS sequence
* Execution engine sequence
* Strategy stop sequence
* Recovery sequence
* Multi-tenant isolation

It is written at a level suitable for architects, backend engineers, mobile engineers, QA, and DevOps.

---

# 📘 **FULL-SEQUENCE-DOCUMENT.md**

### End-to-End Sequence Flows for Algo Trading System

---

# **1. Document Purpose**

This document defines the **sequential message flows** between system components across all operational scenarios in the Algo Trading system.

Each sequence includes:

* Actor interactions
* Component communication
* API calls
* Redis access flow
* DB reads/writes
* Price streaming
* Order placement
* State updates
* Error and retry logic

Matches PRD Sequence Flow (User Flow Section 8)


---

# **2. System Actors**

| Actor            | Description                     |
| ---------------- | ------------------------------- |
| User             | Retail mobile user              |
| Mobile App       | The frontend interface          |
| FastAPI Backend  | API + core logic                |
| Auth Service     | Handles user registration/login |
| Strategy Service | Strategy creation & validation  |
| Strategy Manager | Loads strategy into Redis       |
| Scheduler        | Time triggers (BUY/SELL)        |
| Market Listener  | Price-based triggers            |
| Execution Engine | Processes orders                |
| Broker API       | Zerodha (or equivalent)         |
| Redis            | In-memory execution layer       |
| Database         | Persistent storage              |

---

# **3. Sequence 1 – User Registration & Login**

```
User → Mobile App: enter email & password
Mobile → Backend (/auth/register)
Backend → Auth Service: validate + hash password
Auth Service → DB: insert user
DB → Auth Service: success
Auth Service → Backend: return JWT
Backend → Mobile: JWT token
Mobile: stores token securely
```

Matches PRD requirement: **Basic user onboarding**


---

# **4. Sequence 2 – Broker API Key Setup**

```
User → Mobile: enters API key, secret, token
Mobile → Backend (/broker/connect)
Backend → Broker Connector: validate credentials
Broker Connector → Broker API: verify profile
Broker API → Broker Connector: valid
Broker Connector → DB: save encrypted keys
DB → Backend: saved
Backend → Mobile: Broker connected = true
```

PRD: Must validate broker credentials before strategy creation.


---

# **5. Sequence 3 – Strategy Creation**

```
User → Mobile: fills strategy (symbol, buy_time, sell_time, SL, qty)
Mobile → Backend (/strategy/create)
Backend → Strategy Service: validate fields
Strategy Service → DB: insert strategy
DB → Backend: strategy_id
Backend → Mobile: strategy_id
```

PRD: Mandatory stop-loss, required fields, DB storage.


---

# **6. Sequence 4 – Strategy Start (Load into Redis)**

```
User → Mobile: taps START
Mobile → Backend (/strategy/start)
Backend → Strategy Manager: load strategy from DB
Strategy Manager → DB: fetch strategy
DB → Strategy Manager: strategy data
Strategy Manager → Redis(strategy:{id}): save static metadata
Strategy Manager → Redis(runtime:{id}): initialize runtime
Strategy Manager → Redis(symbol:{sym}:strategies): append strategy id
Strategy Manager → Scheduler: register BUY job
Strategy Manager → Scheduler: register SELL job
Scheduler → Backend: scheduled OK
Backend → Mobile: strategy running
```

PRD: Backend must load strategy into Redis & schedule events.


---

# **7. Sequence 5 – BUY Execution at Buy Time**

```
Scheduler → Backend: BUY trigger at 09:30
Backend → Redis(queue:orders): push {BUY, strategy_id}
Execution Engine → Redis(queue:orders): pop event
Execution Engine → Redis(runtime): acquire lock
Execution Engine → Broker Connector: place BUY order
Broker Connector → Broker API: BUY request
Broker API → Connector: order_id
Connector → Execution Engine: success
Execution Engine → Redis(runtime): update position="bought", last_buy_order=order_id
Execution Engine → DB(order_logs): insert buy log
Execution Engine → Redis(runtime): release lock
Backend → Mobile (via polling): last_action="BUY"
```

PRD: Time-based BUY must occur at exact time.


---

# **8. Sequence 6 – SELL Execution at Sell Time**

```
Scheduler → Backend: SELL trigger at 15:30
Backend → Redis(queue:orders): push {SELL, strategy_id}
Execution Engine → Redis(queue:orders): pop event
Execution Engine → Redis(runtime): acquire lock
Execution Engine → Broker Connector: place SELL order
Broker Connector → Broker API: SELL request
Broker API → Connector: order_id
Connector → Execution Engine: success
Execution Engine → Redis(runtime): update position="sold", last_sell_order=order_id
Execution Engine → DB(order_logs): insert sell log
Execution Engine → Redis(runtime): release lock
Backend → Mobile: last_action="SELL"
```

PRD requirement: SELL at exact time, no delay.


---

# **9. Sequence 7 – STOP-LOSS Trigger (Price-Based Exit)**

```
Broker API → Market Listener: tick {price}
Market Listener → Redis(strategy:{id}): read stop_loss
Market Listener: if price <= stop_loss
Market Listener → Redis(queue:orders): push {STOPLOSS, strategy_id}
Execution Engine → Redis(queue:orders): pop STOPLOSS
Execution Engine → Redis(runtime): acquire lock immediately
Execution Engine → Broker Connector: place SELL order
Broker Connector → Broker API: SELL request
Broker API → Connector: order_id
Connector → Execution Engine: success
Execution Engine → Redis(runtime): update position="exited_by_sl"
Execution Engine → DB(order_logs): insert SL log
Execution Engine → Redis(runtime): release lock
Backend → Mobile: “STOP-LOSS Triggered”
Backend → Scheduler: cancel jobs
```

PRD: STOP-LOSS must be **instant** and **highest priority**.


---

# **10. Sequence 8 – Strategy Stop (Manual or Auto)**

```
User → Mobile: presses STOP
Mobile → Backend (/strategy/stop)
Backend → Strategy Manager: deactivate strategy
Strategy Manager → Redis: delete strategy:{id}, runtime:{id}
Strategy Manager → Redis(symbol:{sym}:strategies): remove id
Strategy Manager → Scheduler: cancel BUY/SELL jobs
Scheduler → Backend: cancelled
Backend → DB: update strategy status
Backend → Mobile: Stopped
```

PRD: User must be able to Stop strategy at any time.


---

# **11. Sequence 9 – Execution Engine Failure & Retry**

```
Execution Engine → Broker API: place order
Broker API → Execution Engine: timeout/error
Execution Engine: retry #1
Execution Engine: retry #2
Execution Engine: retry #3
If still failing:
Execution Engine → DB: log “order failed”
Execution Engine → Redis(runtime): update status="failed"
Execution Engine → Backend: auto-stop strategy
Backend → Scheduler: cancel timers
Backend → Mobile: “Order Failed – Strategy Stopped”
```

PRD: Must have retry mechanism + safe shutdown.


---

# **12. Sequence 10 – System Restart / Recovery Sequence**

```
Backend Restart → Strategy Manager
Strategy Manager → Redis: check active strategy keys
If keys missing:
    Strategy Manager → DB: read active strategies
    Strategy Manager → Redis: recreate strategy:{id}
    Strategy Manager → Redis: recreate runtime:{id}
    Strategy Manager → Scheduler: restore BUY/SELL timers
    Strategy Manager → Market Listener: re-subscribe for symbols
Backend → Logs: “Recovery Complete”
```

From SDD: Backend must auto-recover after crash.


---

# **13. Sequence 11 – Multi-Tenant Isolation**

Example: User A & User B run different strategies.

```
Mobile(A) → Backend → DB(strategy_A)
Mobile(B) → Backend → DB(strategy_B)

Strategy Manager:
    strategy:A → Redis(strategy:101)
    strategy:B → Redis(strategy:202)

Scheduler:
    BUY(A) job: 09:30_A
    BUY(B) job: 10:00_B

Market Listener:
    symbol:TCS → strategies=[A]
    symbol:INFY → strategies=[B]

Execution Engine:
    locks runtime:101 separately from runtime:202
```

PRD: Each user strategy must run independently.


---

# **14. Sequence 12 – User Status Polling Sequence**

```
Mobile → Backend (/strategy/status/{id})
Backend → Redis(runtime:{id}): read runtime
Backend → Mobile:
    last_action
    position
    last_price
    strategy_status
```

Matches UI feedback requirement in PRD.


---

# **15. Unified End-to-End Sequence (Complete Flow)**

This is the **master sequence** covering all steps.

```
1. User registers → login
2. User enters broker API key → backend validates → stored
3. User creates strategy → backend saves → returns id
4. User presses START
5. Backend loads strategy → Redis populated
6. Scheduler registers BUY & SELL timers
7. Market Listener starts monitoring price
8. At buy_time:
       Scheduler → BUY event → Queue → Execution Engine → BUY executed
9. During day:
       Market Listener compares live price
       If price <= SL → STOPLOSS event → Execution Engine → exit immediately
10. At sell_time:
       Scheduler → SELL event → Queue → Execution Engine → SELL executed
11. Strategy ends or user presses STOP
12. Redis keys removed, jobs cancelled, DB updated
13. Mobile polls for status → shows final result
```

This matches full PRD User Flow (Section 8).


---

# ✔ **FULL-SEQUENCE-DOCUMENT.md is complete.**

I can now also generate:

### ✅ SYSTEM-STATE-MACHINE.md

### ✅ EVENT-MAP.md

### ✅ COMPONENT-SEQUENCE-DIAGRAMS (PNG)

### ✅ FAILURE-SEQUENCE-DOC.md

### ✅ MOBILE-FLOW-SEQUENCE.md

Just tell me which one you want next.
