
---

# 📱 **MOBILE-FLOW-SEQUENCE.md**

### Algo Trading System — Mobile App UX & API Sequence Flows

---

# **0. Purpose**

This document describes the **screen-by-screen user flow**, **API calls**, **state changes**, and **backend interactions** that occur from the mobile application.

It is useful for:

* Frontend developers
* QA testers
* UX designers
* Backend integrators

---

# **1. Mobile Screens (Overview)**

| Screen                   | Purpose                                |
| ------------------------ | -------------------------------------- |
| Login                    | Authenticate user                      |
| Register                 | Create new account                     |
| Broker Connect           | Save & validate API Key, Secret, Token |
| Create Strategy          | Strategy input form                    |
| Strategy List (optional) | Shows list of user strategies          |
| Strategy Control         | Start/Stop + Status polling            |

---

# **2. Sequence: App Launch → Login**

```
User opens app
↓
Mobile App checks SecureStore for JWT
↓
IF JWT exists:
    Navigate → Strategy List / Broker Connect
ELSE:
    Navigate → Login Screen
```

---

# **3. Login Flow Sequence**

```
User → Login Screen: enters email + password
↓
Mobile → Backend: POST /auth/login
↓
Backend:
    - Validate credentials
    - Return JWT
↓
Mobile:
    - Save JWT in SecureStore
    - Navigate → Broker Connect Screen
```

**Backend Reference:** PRD Section: "Basic User Authentication"


---

# **4. Register Flow Sequence**

```
User → Register Screen: enters details
↓
Mobile → Backend: POST /auth/register
↓
Backend:
    - Hash password
    - Insert user
    - Generate JWT
↓
Mobile:
    - Save JWT
    - Navigate → Broker Connect Screen
```

---

# **5. Broker Connect Sequence**

(PRD Section 4.1 Broker API Setup)


```
User → Broker Connect Screen: enters API Key, Secret, Access Token
↓
Mobile → Backend: POST /broker/connect
↓
Backend:
    - Validate with Broker API
    - Encrypt + save in DB
↓
Mobile:
    - Show Connected
    - Navigate → Create Strategy Screen
```

**UI Validation:**

* All fields mandatory
* Disable Save button until valid

---

# **6. Strategy Creation Sequence**

```
User → Create Strategy Screen:
    fields: symbol, buy_time, sell_time, stop_loss, quantity
↓
Mobile: Validate fields locally
↓
Mobile → Backend: POST /strategy/create
↓
Backend:
    - Validate (stop_loss required)
    - Save to DB
    - Return strategy_id
↓
Mobile:
    - Store strategy_id temporarily
    - Navigate → Strategy Control Screen
```

Matches PRD: "Minimal fields + SL mandatory"


---

# **7. Strategy Start Sequence**

(When user presses START)

```
User → Strategy Control Screen: presses START
↓
Mobile → Backend: POST /strategy/start
↓
Backend:
    - Load strategy into Redis
    - Initialize runtime
    - Register BUY/SELL scheduler jobs
↓
Backend → Mobile: status = running
↓
Mobile UI:
    - Disable START button
    - Enable STOP button
    - Begin 5-second polling loop
```

**Mobile State Changes**

* strategyStatus = "running"
* position = "none"
* lastAction = null

---

# **8. Mobile → Status Polling Sequence**

Every 5 seconds:

```
Mobile → Backend: GET /strategy/status/{id}
↓
Backend → Redis(runtime)
↓
Backend → Mobile: JSON status
↓
Mobile:
    - Update UI (Running, Bought, Sold, SL Hit)
    - Update status color
```

**Returned fields:**

```
{
 status: "running",
 position: "bought|sold|none",
 last_action: "BUY|SELL|STOPLOSS",
 last_price: 3520.3,
 runtime_ts: ...
}
```

Matches PRD: must show simple feedback.


---

# **9. BUY Execution – Mobile View Sequence**

Triggered in backend automatically at **buy_time**.

### Mobile Perspective Only:

```
Scheduler triggers BUY
↓
Backend updates runtime
↓
Mobile polling fetches new status:
    last_action = "BUY"
    position = "bought"
↓
Mobile UI:
    Show "Bought @ price"
    Color switch (Green)
```

The user does not manually trigger BUY.

---

# **10. SELL Execution – Mobile View Sequence**

Triggered at **sell_time**.

```
Scheduler triggers SELL
↓
Backend updates runtime
↓
Mobile polling retrieves:
    last_action = "SELL"
    position = "sold"
↓
Mobile UI:
    Show "Sold @ price"
    Auto-stop strategy OR display completed
```

---

# **11. STOP LOSS Sequence – Mobile View**

This is the most critical UX event.

```
Price Feed → Backend: STOPLOSS triggered
↓
Backend: executes immediate SELL
↓
Backend: updates status = stopped
↓
Mobile polling fetches:
    last_action = "STOPLOSS"
    status = "stopped"
↓
Mobile UI:
    Highlight in RED:
    "STOP LOSS Triggered – Exited at price"
    Replace START/STOP with “Strategy Ended”
```

Matches PRD requirement: “Immediate execution + user must see SL hit.”


---

# **12. User Presses STOP Manually**

```
User → Strategy Control: presses STOP
↓
Mobile → Backend: POST /strategy/stop
↓
Backend:
    - Delete Redis keys
    - Cancel schedulers
↓
Backend → Mobile:
    status = "stopped"
↓
Mobile UI:
    - STOP button disabled
    - START enabled again
    - Status shown as Stopped
```

---

# **13. Mobile Error Handling Sequence**

### A. Token Expired

```
Backend → 401 Unauthorized
↓
Mobile:
    - Clear SecureStore
    - Redirect → Login Screen
```

### B. Communication Error

```
If GET /status fails:
    Show toast: “Unable to reach server”
```

### C. Missing Broker Keys

```
Backend → error: "BROKER_NOT_CONNECTED"
Mobile → navigate to Broker Connect Screen
```

### D. Strategy Creation Error

```
Backend → 400 "INVALID_INPUT"
Mobile → highlight all invalid fields
```

---

# **14. Recovery Sequence – App Relaunch**

If app is closed and reopened while strategy is running:

```
App launches
↓
Mobile checks SecureStore for JWT
↓
Mobile → Backend: GET /strategy/active
↓
If active:
    Navigate → Strategy Control Screen
    Start polling
Else:
    Navigate → Create Strategy or Strategy List
```

This ensures continuity without user confusion.

---

# **15. Mobile-Friendly Unified Flow (Human Version)**

```
Login/Register
→ Broker Connect
→ Create Strategy
→ Strategy Control (Start)
→ Polling updates UI
→ BUY happens automatically
→ SELL happens automatically
→ STOPLOSS exits instantly
→ Strategy ends
```

Perfectly matches PRD User Flow Section 8.


---

# **16. Complete Mobile State Machine**

### States:

| State        | Meaning                     |
| ------------ | --------------------------- |
| idle         | No strategy running         |
| running      | Scheduler + listener active |
| bought       | BUY completed               |
| sold         | SELL completed              |
| exited_by_sl | STOPLOSS hit                |
| stopped      | User/Backend stopped        |

---

# ✔ MOBILE-FLOW-SEQUENCE.md READY

If you want next:

### ✅ UX-FLOW-DIAGRAM.png

### ✅ UI-WIRE-FLOW.md

### ✅ USER-JOURNEY.md

### ✅ MOBILE-ERROR-MATRIX.md

### ✅ COMPLETE-DOCUMENT-PDF

