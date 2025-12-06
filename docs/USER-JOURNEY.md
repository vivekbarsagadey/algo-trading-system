# 📘 **USER-JOURNEY.md**

### Algo Trading System – End-to-End User Journey

---

# **0. Purpose**

This document describes the **entire experience** of a user interacting with the Algo Trading System mobile app — focusing on emotions, expectations, goals, micro-interactions, and system responses at each step.

This is the *human-level* journey behind the technical flows we have already documented.

---

# **1. Persona: Primary User**

**Name:** Retail Trader (beginner–intermediate)
**Goal:** Want automated execution without complexity
**Pain Points:**

* Doesn’t understand charts
* Wants simple buy/sell automation
* Wants to avoid emotional trading
* Prefers minimal setup
* Needs execution reliability

Matches PRD demand for **extreme simplicity**, “no charts”, “no complexity” ().

---

# **2. High-Level User Journey Stages**

| Stage                 | Description                                                |
| --------------------- | ---------------------------------------------------------- |
| 1. Discover           | User downloads app after hearing about simple algo trading |
| 2. Onboard            | Registers & logs in                                        |
| 3. Connect Broker     | Adds API Key/Secret/Token                                  |
| 4. Configure Strategy | Sets symbol, buy time, sell time, SL, quantity             |
| 5. Activate Strategy  | Starts automation                                          |
| 6. Monitor            | Sees status updates (BUY/SELL/SL Hit)                      |
| 7. Exit               | Strategy completes or user stops it                        |
| 8. Reflect            | User understands results & feels confident                 |

---

# **3. Detailed User Journey Map**

---

## **3.1 Stage 1: Discover & Launch App**

### **User Motivation**

* Wants a simple automated trading tool
* Wants to remove emotional decisions
* Wants to test basic automation first

### **User Actions**

* Downloads the app
* Opens it

### **System Response**

* App checks if JWT is saved
* If none → show Login screen

### **Emotions**

✔ Curious
✔ Cautious
✔ Looking for clarity

---

## **3.2 Stage 2: Login / Register**

### **User Actions**

* Enters email + password
* Taps Login or Register

### **System Response**

* Backend verifies credentials
* Returns JWT token
* App stores JWT
* Navigates to **Broker Connect**

### **Emotions**

✔ Feeling of progress
✔ Trust increases because process is simple

Matches PRD “Minimal onboarding friction”


---

## **3.3 Stage 3: Broker Connect**

### **User Actions**

* Enters Zerodha API Key
* Enters Secret Key
* Enters Access Token
* Taps “Save & Validate”

### **System Response**

* Backend verifies keys with broker
* If valid → saved securely
* App shows success
* Navigates to “Create Strategy”

### **Emotions**

✔ Relief
✔ Confidence
✔ Feeling safe

---

## **3.4 Stage 4: Strategy Configuration**

Matches PRD: only essential inputs.


### **User Actions**

* Enters **symbol**
* Selects **buy time**
* Selects **sell time**
* Enters **stop-loss** (mandatory)
* Enters **quantity**
* Taps “Create Strategy”

### **System Response**

* Backend validates
* Saves to DB
* Returns strategy_id
* App navigates to **Strategy Control** screen

### **Emotions**

✔ Clear
✔ Non-technical
✔ Empowered (first time user feels “algo trading is easy”)

---

## **3.5 Stage 5: Start Strategy**

### **User Actions**

* Presses **START**

### **System Response**

* Backend loads strategy into Redis
* Scheduler jobs created
* App shows **Running** state
* Polling begins (every 5 seconds)

### **Emotions**

✔ Excitement
✔ Mild anxiety (“Is this safe?”)
✔ Trust grows as app shows real-time status

---

## **3.6 Stage 6: BUY Event (Autonomous)**

Triggered at buy_time automatically.

### **System Behavior**

* Execution Engine places BUY
* Updates runtime
* App polling shows:

  * **Action: BUY Executed**
  * **Position: Bought**
  * **Last Price:** XX

### **User Emotions**

✔ Satisfaction
✔ Realization that app works
✔ New confidence

---

## **3.7 Stage 7: LIVE Monitoring (Between BUY → SELL)**

### **User Actions**

* Opens app occasionally
* Sees updates via polling

### **System Behavior**

* Shows status:

  * “Running”
  * Last Action
  * Last Price
  * SL Level
* If price is close to SL:

  * UI warns: “SL risk zone”

### **User Emotions**

✔ Engaged
✔ In control
✔ Not overwhelmed (simple UI)

---

## **3.8 Stage 8: STOPLOSS (Critical UX)**

Matches PRD requirement for immediate execution.


### **System Behavior**

* Market Listener triggers STOPLOSS
* Execution Engine sells immediately
* Mobile polling shows:

  * **STOP LOSS Triggered**
  * Exited at price
* Strategy auto-stopped

### **User Emotions**

✔ Protected
✔ Respected (system respected risk)
✔ Trust increases significantly

---

## **3.9 Stage 9: SELL Event (If no STOPLOSS)**

### **System Behavior**

* Scheduler triggers SELL at sell_time
* Execution Engine executes SELL
* App shows:

  * “SELL Executed @ price”
  * Strategy completed

### **User Emotions**

✔ Completion
✔ Success feeling
✔ Wants to create more strategies

---

## **3.10 Stage 10: Manual STOP**

### **User Actions**

* Presses STOP

### **System Behavior**

* Cancels schedulers
* Removes Redis keys
* Updates status
* UI shows:

  * “Strategy Stopped”
  * Start button enabled

### **User Emotions**

✔ Control
✔ Flexibility
✔ Safe exit

---

## **3.11 Stage 11: Review Results**

### **User Actions**

* Reads:

  * Buy price
  * Sell price
  * SL execution (if any)

### **System Behavior**

* Shows basic logs
* Shows status history
* No charts or analytics (per PRD MVP)

### **User Emotions**

✔ Clarity
✔ Understanding
✔ Satisfaction

---

# **4. Combined User Journey Timeline (Narrative Form)**

A simplified storytelling version:

```
User hears about a simple algo app.
They download it.

They log in → smooth.
They connect their broker → validated instantly.
They set a strategy in under 30 seconds.

They press START.

Now automation begins.
BUY happens right on schedule.
They check the app.
It shows real-time status — nothing confusing.

If market drops, STOPLOSS triggers instantly.
User feels safe.

If market is steady, system sells at end time.

User sees final summary.
Trust established.
They feel the system works automatically.

They create another strategy the next day.
```

---

# **5. Journey Emotions Matrix**

| Journey Stage   | Positive Emotions | Risks/Concerns           |
| --------------- | ----------------- | ------------------------ |
| Login           | Quick start       | None                     |
| Broker Connect  | Trust             | Fear of wrong keys       |
| Create Strategy | Empowerment       | Wrong time entries       |
| Start Strategy  | Excitement        | Complexity fear          |
| BUY             | Validation        | Delay fear               |
| Monitoring      | Engagement        | SL anxiety               |
| STOPLOSS        | Protection        | Shock if unexpected      |
| SELL            | Completion        | Minimal concern          |
| End             | Satisfaction      | Wants analytics (future) |

---

# **6. UX Priorities Derived from Journey**

These come directly from PRD UX constraints.


### **Highest UX Priorities**

1. **Clarity and safety over complexity**
2. **One-screen simplicity**
3. **Real-time readable status**
4. **Instant STOPLOSS visibility**
5. **Minimal taps**
6. **Error-proof forms**
7. **Consistent polling updates**

---

# ✔ USER-JOURNEY.md is complete

I can now generate:

### 📌 **MOBILE-ERROR-MATRIX.md**

### 📌 **UX-FLOW-DIAGRAM.png**

### 📌 **MOBILE-UI-COPY.md** (all button labels & messages)

### 📌 **COMPLETE-MVP-UX-DOC.md**

### 📌 **MOBILE-VALIDATION-RULES.md**
