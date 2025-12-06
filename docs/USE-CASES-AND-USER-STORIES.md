# 📘 Use Cases & User Stories Document

## Algo Trading System

**Version:** 1.0  
**Last Updated:** December 2024  
**Status:** Active

---

## Table of Contents

1. [Overview](#1-overview)
2. [Actors](#2-actors)
3. [Use Cases](#3-use-cases)
4. [User Stories](#4-user-stories)
5. [Acceptance Criteria Summary](#5-acceptance-criteria-summary)

---

## 1. Overview

This document defines all use cases and user stories for the Algo Trading System. It serves as the bridge between business requirements (PRD) and technical implementation (SRS/LLD).

### 1.1 Document Purpose

- Define all system interactions from user perspective
- Provide clear acceptance criteria for each feature
- Enable QA to create test cases
- Guide development prioritization

### 1.2 Scope

Covers all MVP (P0) features plus important P1 features:
- User Authentication
- Broker Integration
- Strategy Management
- Trade Execution
- Real-Time Monitoring

---

## 2. Actors

### 2.1 Primary Actors

| Actor | Description | Goals |
|-------|-------------|-------|
| **Retail Trader** | End user of the mobile app | Automate simple trading strategies |
| **System Scheduler** | Automated time-based trigger | Execute BUY/SELL at specified times |
| **Market Listener** | Real-time price monitor | Trigger stop-loss when price breaches |

### 2.2 Secondary Actors

| Actor | Description | Role |
|-------|-------------|------|
| **Broker API** | External trading platform (Zerodha, etc.) | Execute actual trades |
| **Backend System** | FastAPI + Redis infrastructure | Process requests, maintain state |

---

## 3. Use Cases

### 3.1 Use Case Diagram (Text Representation)

```
┌─────────────────────────────────────────────────────────────────┐
│                     ALGO TRADING SYSTEM                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐                                                   │
│  │  Retail  │──── UC-1: Register Account                       │
│  │  Trader  │──── UC-2: Login                                   │
│  │          │──── UC-3: Connect Broker                          │
│  │          │──── UC-4: Create Strategy                         │
│  │          │──── UC-5: Start Strategy                          │
│  │          │──── UC-6: Stop Strategy                           │
│  │          │──── UC-7: View Strategy Status                    │
│  │          │──── UC-8: Update Strategy                         │
│  └──────────┘                                                   │
│                                                                 │
│  ┌──────────┐                                                   │
│  │ Scheduler│──── UC-9: Execute Time-Based BUY                  │
│  │          │──── UC-10: Execute Time-Based SELL                │
│  └──────────┘                                                   │
│                                                                 │
│  ┌──────────┐                                                   │
│  │ Market   │──── UC-11: Monitor Price Feed                     │
│  │ Listener │──── UC-12: Trigger Stop-Loss                      │
│  └──────────┘                                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 3.2 Detailed Use Cases

---

#### UC-1: Register Account

| Attribute | Description |
|-----------|-------------|
| **Use Case ID** | UC-1 |
| **Name** | Register Account |
| **Actor** | Retail Trader |
| **Priority** | P0 (Critical) |
| **Preconditions** | User has installed the mobile app |
| **Postconditions** | User account created, JWT token issued |

**Main Flow:**
1. User opens the app
2. User taps "Register"
3. User enters email address
4. User enters password (min 6 characters)
5. User confirms password
6. User taps "Create Account"
7. System validates input
8. System creates user in database
9. System generates JWT token
10. System navigates to Broker Connect screen

**Alternative Flows:**

| ID | Condition | Flow |
|----|-----------|------|
| AF-1.1 | Email already exists | Show error "Email already registered" |
| AF-1.2 | Invalid email format | Show error "Please enter valid email" |
| AF-1.3 | Password too short | Show error "Password must be at least 6 characters" |
| AF-1.4 | Passwords don't match | Show error "Passwords do not match" |

**Exception Flows:**

| ID | Condition | Flow |
|----|-----------|------|
| EF-1.1 | Network error | Show error "Connection failed. Please try again" |
| EF-1.2 | Server error | Show error "Something went wrong. Please try later" |

---

#### UC-2: Login

| Attribute | Description |
|-----------|-------------|
| **Use Case ID** | UC-2 |
| **Name** | Login |
| **Actor** | Retail Trader |
| **Priority** | P0 (Critical) |
| **Preconditions** | User has registered account |
| **Postconditions** | User authenticated, JWT token issued |

**Main Flow:**
1. User opens the app
2. System checks for stored JWT
3. If no valid JWT, show Login screen
4. User enters email
5. User enters password
6. User taps "Login"
7. System validates credentials
8. System generates new JWT token
9. System stores JWT in secure storage
10. System navigates to appropriate screen (Broker Connect or Strategy List)

**Alternative Flows:**

| ID | Condition | Flow |
|----|-----------|------|
| AF-2.1 | Invalid credentials | Show error "Invalid email or password" |
| AF-2.2 | Valid stored JWT | Skip login, navigate directly to app |

---

#### UC-3: Connect Broker

| Attribute | Description |
|-----------|-------------|
| **Use Case ID** | UC-3 |
| **Name** | Connect Broker |
| **Actor** | Retail Trader |
| **Priority** | P0 (Critical) |
| **Preconditions** | User is logged in |
| **Postconditions** | Broker credentials validated and securely stored |

**Main Flow:**
1. User navigates to Broker Connect screen
2. User selects broker (Zerodha, Dhan, etc.)
3. User enters API Key
4. User enters API Secret
5. User enters Access Token
6. User taps "Validate & Save"
7. System calls broker API to validate credentials
8. System encrypts credentials with AES-256
9. System stores encrypted credentials in database
10. System shows success message
11. System navigates to Strategy Creation screen

**Alternative Flows:**

| ID | Condition | Flow |
|----|-----------|------|
| AF-3.1 | Invalid API key | Show error "Invalid API key" |
| AF-3.2 | Invalid secret | Show error "Invalid API secret" |
| AF-3.3 | Expired token | Show error "Access token expired. Please generate new token" |
| AF-3.4 | Broker already connected | Show option to update credentials |

**Exception Flows:**

| ID | Condition | Flow |
|----|-----------|------|
| EF-3.1 | Broker API unavailable | Show error "Broker service unavailable. Try later" |

---

#### UC-4: Create Strategy

| Attribute | Description |
|-----------|-------------|
| **Use Case ID** | UC-4 |
| **Name** | Create Strategy |
| **Actor** | Retail Trader |
| **Priority** | P0 (Critical) |
| **Preconditions** | User is logged in, Broker is connected |
| **Postconditions** | Strategy saved in database |

**Main Flow:**
1. User navigates to Create Strategy screen
2. User enters stock symbol (e.g., "RELIANCE")
3. User selects buy time using time picker
4. User selects sell time using time picker
5. User enters stop-loss price
6. User enters quantity
7. User taps "Create Strategy"
8. System validates all inputs
9. System saves strategy to database
10. System shows success message with strategy ID
11. System navigates to Strategy Control screen

**Validation Rules:**

| Field | Rule |
|-------|------|
| Symbol | Required, valid NSE/BSE symbol |
| Buy Time | Required, valid time format HH:MM:SS |
| Sell Time | Required, must be after buy time |
| Stop-Loss | Required, must be positive number |
| Quantity | Required, must be positive integer |

**Alternative Flows:**

| ID | Condition | Flow |
|----|-----------|------|
| AF-4.1 | Missing stop-loss | Show error "Stop-loss is mandatory for safety" |
| AF-4.2 | Sell time before buy time | Show error "Sell time must be after buy time" |
| AF-4.3 | Invalid symbol | Show error "Invalid stock symbol" |
| AF-4.4 | Quantity ≤ 0 | Show error "Quantity must be greater than 0" |

---

#### UC-5: Start Strategy

| Attribute | Description |
|-----------|-------------|
| **Use Case ID** | UC-5 |
| **Name** | Start Strategy |
| **Actor** | Retail Trader |
| **Priority** | P0 (Critical) |
| **Preconditions** | Strategy exists, Broker connected |
| **Postconditions** | Strategy loaded into Redis, Scheduler jobs registered |

**Main Flow:**
1. User views Strategy Control screen
2. User taps "START" button
3. System fetches strategy from database
4. System loads strategy into Redis (strategy:{id})
5. System initializes runtime state (runtime:{id})
6. System registers BUY job with scheduler
7. System registers SELL job with scheduler
8. System adds strategy to symbol listener
9. System updates status to "Running"
10. UI shows "Running" status with green indicator
11. System begins 5-second status polling

**Alternative Flows:**

| ID | Condition | Flow |
|----|-----------|------|
| AF-5.1 | Strategy already running | Show message "Strategy is already running" |
| AF-5.2 | Broker token expired | Show error "Please refresh broker token" |
| AF-5.3 | Outside market hours | Show warning "Strategy will execute during market hours" |

---

#### UC-6: Stop Strategy

| Attribute | Description |
|-----------|-------------|
| **Use Case ID** | UC-6 |
| **Name** | Stop Strategy |
| **Actor** | Retail Trader |
| **Priority** | P0 (Critical) |
| **Preconditions** | Strategy is running |
| **Postconditions** | Strategy stopped, Redis keys deleted, Scheduler jobs cancelled |

**Main Flow:**
1. User views Strategy Control screen
2. User taps "STOP" button
3. System confirms action (optional)
4. System cancels scheduler jobs
5. System deletes Redis keys (strategy:{id}, runtime:{id})
6. System removes from symbol listener
7. System updates database status to "Stopped"
8. UI shows "Stopped" status with gray indicator

**Alternative Flows:**

| ID | Condition | Flow |
|----|-----------|------|
| AF-6.1 | Strategy not running | Button disabled or show message |
| AF-6.2 | Position open (bought) | Show warning "You have open position. Stopping will not auto-sell" |

---

#### UC-7: View Strategy Status

| Attribute | Description |
|-----------|-------------|
| **Use Case ID** | UC-7 |
| **Name** | View Strategy Status |
| **Actor** | Retail Trader |
| **Priority** | P0 (Critical) |
| **Preconditions** | Strategy exists |
| **Postconditions** | None (read-only) |

**Main Flow:**
1. User views Strategy Control screen
2. System polls backend every 5 seconds
3. System displays:
   - Strategy status (Running/Stopped/Completed)
   - Current position (None/Bought/Sold)
   - Last action (BUY/SELL/SL Hit)
   - Last price (if running)
   - Timestamps
4. UI updates in real-time

**Status Indicators:**

| Status | Color | Meaning |
|--------|-------|---------|
| Running | Green | Strategy active, waiting for triggers |
| Stopped | Gray | Strategy manually stopped |
| Bought | Blue | BUY executed, holding position |
| Sold | Green | SELL executed, cycle complete |
| SL Hit | Red | Stop-loss triggered |
| Failed | Red | Execution error |

---

#### UC-8: Update Strategy

| Attribute | Description |
|-----------|-------------|
| **Use Case ID** | UC-8 |
| **Name** | Update Strategy |
| **Actor** | Retail Trader |
| **Priority** | P1 (Important) |
| **Preconditions** | Strategy exists |
| **Postconditions** | Strategy updated in DB and Redis (if running) |

**Main Flow:**
1. User views Strategy Control screen
2. User taps "Edit" button
3. System displays current values
4. User modifies desired fields (SL, times, quantity)
5. User taps "Save"
6. System validates changes
7. System updates database
8. If strategy is running:
   - System updates Redis keys
   - System reschedules jobs if times changed
9. System shows success message

**Constraints:**
- Symbol cannot be changed while running
- Changes apply immediately if running

---

#### UC-9: Execute Time-Based BUY

| Attribute | Description |
|-----------|-------------|
| **Use Case ID** | UC-9 |
| **Name** | Execute Time-Based BUY |
| **Actor** | System Scheduler |
| **Priority** | P0 (Critical) |
| **Preconditions** | Strategy running, buy_time reached, position = NONE |
| **Postconditions** | BUY order placed, position = BOUGHT |

**Main Flow:**
1. Scheduler triggers at buy_time
2. System pushes BUY event to Redis queue
3. Execution Engine pops event
4. Engine acquires Redis lock (lock_state:{id})
5. Engine validates preconditions:
   - Strategy still running
   - Position is NONE
   - Broker token valid
6. Engine builds order payload
7. Engine calls Broker API to place BUY order
8. Broker returns order_id
9. Engine updates Redis runtime (position = BOUGHT)
10. Engine logs order to database
11. Engine releases lock
12. Mobile app receives updated status on next poll

**Exception Flows:**

| ID | Condition | Flow |
|----|-----------|------|
| EF-9.1 | Broker timeout | Retry up to 3 times |
| EF-9.2 | Broker rejection | Log error, mark strategy failed |
| EF-9.3 | Insufficient margin | Log error, notify user |
| EF-9.4 | Lock already held | Skip (prevent duplicate) |

---

#### UC-10: Execute Time-Based SELL

| Attribute | Description |
|-----------|-------------|
| **Use Case ID** | UC-10 |
| **Name** | Execute Time-Based SELL |
| **Actor** | System Scheduler |
| **Priority** | P0 (Critical) |
| **Preconditions** | Strategy running, sell_time reached, position = BOUGHT |
| **Postconditions** | SELL order placed, position = SOLD |

**Main Flow:**
1. Scheduler triggers at sell_time
2. System checks if position = BOUGHT (skip if already sold by SL)
3. System pushes SELL event to Redis queue
4. Execution Engine pops event
5. Engine acquires Redis lock
6. Engine validates preconditions
7. Engine calls Broker API to place SELL order
8. Broker returns order_id
9. Engine updates Redis runtime (position = SOLD)
10. Engine logs order to database
11. Engine releases lock
12. Strategy marked as completed

**Alternative Flows:**

| ID | Condition | Flow |
|----|-----------|------|
| AF-10.1 | Position already SOLD (by SL) | Skip SELL, log info |
| AF-10.2 | Position is NONE | Skip SELL (BUY never executed) |

---

#### UC-11: Monitor Price Feed

| Attribute | Description |
|-----------|-------------|
| **Use Case ID** | UC-11 |
| **Name** | Monitor Price Feed |
| **Actor** | Market Listener |
| **Priority** | P0 (Critical) |
| **Preconditions** | At least one strategy running for symbol |
| **Postconditions** | Price updated in Redis |

**Main Flow:**
1. Market Listener connects to Broker WebSocket
2. Listener subscribes to symbols with active strategies
3. Broker sends price tick
4. Listener updates Redis (price:{symbol})
5. Listener checks all strategies for that symbol
6. For each strategy: compare price with stop_loss
7. If price ≤ stop_loss AND position = BOUGHT:
   - Trigger UC-12 (Stop-Loss)

**Exception Flows:**

| ID | Condition | Flow |
|----|-----------|------|
| EF-11.1 | WebSocket disconnect | Auto-reconnect every 2 seconds |
| EF-11.2 | Invalid price data | Log error, ignore tick |

---

#### UC-12: Trigger Stop-Loss

| Attribute | Description |
|-----------|-------------|
| **Use Case ID** | UC-12 |
| **Name** | Trigger Stop-Loss |
| **Actor** | Market Listener |
| **Priority** | P0 (Critical) |
| **Preconditions** | Price ≤ stop_loss, position = BOUGHT |
| **Postconditions** | Emergency SELL executed, position = EXITED_BY_SL |

**Main Flow:**
1. Market Listener detects price ≤ stop_loss
2. Listener immediately pushes STOPLOSS event to Redis queue
3. Execution Engine pops event (highest priority)
4. Engine acquires Redis lock
5. Engine validates position = BOUGHT
6. Engine calls Broker API to place SELL order
7. Broker returns order_id
8. Engine updates Redis runtime (position = EXITED_BY_SL)
9. Engine cancels scheduled SELL job
10. Engine logs SL execution to database
11. Engine releases lock
12. Mobile app shows "STOP-LOSS HIT" on next poll

**Performance Requirement:**
- Total latency from price breach to event push: < 5 ms

**Exception Flows:**

| ID | Condition | Flow |
|----|-----------|------|
| EF-12.1 | SELL fails | Retry up to 3 times with 100ms delay |
| EF-12.2 | All retries fail | Mark as SL_FAILED, alert user |

---

## 4. User Stories

### 4.1 Authentication Stories

---

#### US-1.1: User Registration

| Attribute | Value |
|-----------|-------|
| **Story ID** | US-1.1 |
| **Epic** | Authentication |
| **Priority** | P0 |

**User Story:**
```
As a new user,
I want to register with my email and password,
So that I can create an account and start using the app.
```

**Acceptance Criteria:**
- [ ] AC-1.1.1: User can enter email address
- [ ] AC-1.1.2: User can enter password (masked)
- [ ] AC-1.1.3: User can confirm password
- [ ] AC-1.1.4: System validates email format
- [ ] AC-1.1.5: System validates password length (min 6 chars)
- [ ] AC-1.1.6: System checks if email already exists
- [ ] AC-1.1.7: System creates user account on success
- [ ] AC-1.1.8: System issues JWT token on success
- [ ] AC-1.1.9: User is redirected to Broker Connect screen

---

#### US-1.2: User Login

| Attribute | Value |
|-----------|-------|
| **Story ID** | US-1.2 |
| **Epic** | Authentication |
| **Priority** | P0 |

**User Story:**
```
As a registered user,
I want to login with my credentials,
So that I can access my strategies and broker connection.
```

**Acceptance Criteria:**
- [ ] AC-1.2.1: User can enter email and password
- [ ] AC-1.2.2: System validates credentials against database
- [ ] AC-1.2.3: System issues JWT token on success
- [ ] AC-1.2.4: JWT is stored in secure storage
- [ ] AC-1.2.5: User is redirected to appropriate screen
- [ ] AC-1.2.6: Error message shown for invalid credentials

---

#### US-1.3: Auto-Login

| Attribute | Value |
|-----------|-------|
| **Story ID** | US-1.3 |
| **Epic** | Authentication |
| **Priority** | P1 |

**User Story:**
```
As a returning user,
I want to be automatically logged in if I have a valid session,
So that I don't have to enter credentials every time.
```

**Acceptance Criteria:**
- [ ] AC-1.3.1: App checks for stored JWT on launch
- [ ] AC-1.3.2: If valid JWT exists, skip login screen
- [ ] AC-1.3.3: If JWT expired, show login screen
- [ ] AC-1.3.4: User can manually logout

---

### 4.2 Broker Integration Stories

---

#### US-2.1: Connect Broker Account

| Attribute | Value |
|-----------|-------|
| **Story ID** | US-2.1 |
| **Epic** | Broker Integration |
| **Priority** | P0 |

**User Story:**
```
As a trader,
I want to connect my broker account using API credentials,
So that the system can place trades on my behalf.
```

**Acceptance Criteria:**
- [ ] AC-2.1.1: User can select broker (Zerodha initially)
- [ ] AC-2.1.2: User can enter API Key
- [ ] AC-2.1.3: User can enter API Secret
- [ ] AC-2.1.4: User can enter Access Token
- [ ] AC-2.1.5: System validates credentials with broker API
- [ ] AC-2.1.6: Credentials are encrypted with AES-256
- [ ] AC-2.1.7: Encrypted credentials stored in database
- [ ] AC-2.1.8: Success message shown on valid connection
- [ ] AC-2.1.9: Error message shown for invalid credentials

---

#### US-2.2: Update Broker Credentials

| Attribute | Value |
|-----------|-------|
| **Story ID** | US-2.2 |
| **Epic** | Broker Integration |
| **Priority** | P1 |

**User Story:**
```
As a trader,
I want to update my broker credentials when my access token expires,
So that my strategies can continue executing.
```

**Acceptance Criteria:**
- [ ] AC-2.2.1: User can access broker settings
- [ ] AC-2.2.2: User can update access token
- [ ] AC-2.2.3: System re-validates with broker API
- [ ] AC-2.2.4: Updated credentials encrypted and saved

---

### 4.3 Strategy Management Stories

---

#### US-3.1: Create Trading Strategy

| Attribute | Value |
|-----------|-------|
| **Story ID** | US-3.1 |
| **Epic** | Strategy Management |
| **Priority** | P0 |

**User Story:**
```
As a trader,
I want to create a simple trading strategy with symbol, times, stop-loss, and quantity,
So that the system can automate my trading plan.
```

**Acceptance Criteria:**
- [ ] AC-3.1.1: User can enter stock symbol
- [ ] AC-3.1.2: User can select buy time using time picker
- [ ] AC-3.1.3: User can select sell time using time picker
- [ ] AC-3.1.4: User must enter stop-loss (mandatory)
- [ ] AC-3.1.5: User can enter quantity
- [ ] AC-3.1.6: System validates sell time > buy time
- [ ] AC-3.1.7: System validates all required fields
- [ ] AC-3.1.8: Strategy saved to database on success
- [ ] AC-3.1.9: Strategy ID returned to user

---

#### US-3.2: Mandatory Stop-Loss

| Attribute | Value |
|-----------|-------|
| **Story ID** | US-3.2 |
| **Epic** | Strategy Management |
| **Priority** | P0 |

**User Story:**
```
As a safety-conscious platform,
I want to require stop-loss for every strategy,
So that users are protected from excessive losses.
```

**Acceptance Criteria:**
- [ ] AC-3.2.1: Stop-loss field is required in UI
- [ ] AC-3.2.2: Backend rejects strategies without stop-loss
- [ ] AC-3.2.3: Error message: "Stop-loss is mandatory for safety"
- [ ] AC-3.2.4: 100% of strategies must have stop-loss

---

#### US-3.3: Start Strategy

| Attribute | Value |
|-----------|-------|
| **Story ID** | US-3.3 |
| **Epic** | Strategy Management |
| **Priority** | P0 |

**User Story:**
```
As a trader,
I want to start my strategy with a single tap,
So that the automation begins executing.
```

**Acceptance Criteria:**
- [ ] AC-3.3.1: START button visible on strategy screen
- [ ] AC-3.3.2: Tapping START loads strategy into Redis
- [ ] AC-3.3.3: System registers scheduler jobs
- [ ] AC-3.3.4: System subscribes to price feed
- [ ] AC-3.3.5: UI shows "Running" status
- [ ] AC-3.3.6: Button changes to STOP

---

#### US-3.4: Stop Strategy

| Attribute | Value |
|-----------|-------|
| **Story ID** | US-3.4 |
| **Epic** | Strategy Management |
| **Priority** | P0 |

**User Story:**
```
As a trader,
I want to stop my strategy immediately,
So that I can take manual control when needed.
```

**Acceptance Criteria:**
- [ ] AC-3.4.1: STOP button visible when strategy running
- [ ] AC-3.4.2: Tapping STOP cancels scheduler jobs
- [ ] AC-3.4.3: System removes strategy from Redis
- [ ] AC-3.4.4: UI shows "Stopped" status
- [ ] AC-3.4.5: Strategy can be restarted later

---

#### US-3.5: View Strategy Status

| Attribute | Value |
|-----------|-------|
| **Story ID** | US-3.5 |
| **Epic** | Strategy Management |
| **Priority** | P0 |

**User Story:**
```
As a trader,
I want to see real-time status of my strategy,
So that I know what actions have been executed.
```

**Acceptance Criteria:**
- [ ] AC-3.5.1: Status updates every 5 seconds
- [ ] AC-3.5.2: Shows current state (Running/Stopped/Bought/Sold)
- [ ] AC-3.5.3: Shows last action (BUY/SELL/SL Hit)
- [ ] AC-3.5.4: Shows current price (when running)
- [ ] AC-3.5.5: Color-coded status indicators

---

### 4.4 Execution Stories

---

#### US-4.1: Time-Based BUY Execution

| Attribute | Value |
|-----------|-------|
| **Story ID** | US-4.1 |
| **Epic** | Execution Engine |
| **Priority** | P0 |

**User Story:**
```
As a trader,
I want my BUY order to execute exactly at the specified time,
So that I enter the market at my planned entry point.
```

**Acceptance Criteria:**
- [ ] AC-4.1.1: Scheduler triggers within 300ms of buy_time
- [ ] AC-4.1.2: BUY order placed via broker API
- [ ] AC-4.1.3: Position updated to BOUGHT on success
- [ ] AC-4.1.4: Order logged to database
- [ ] AC-4.1.5: Retry up to 3 times on failure
- [ ] AC-4.1.6: No duplicate BUY orders (lock prevents)

---

#### US-4.2: Time-Based SELL Execution

| Attribute | Value |
|-----------|-------|
| **Story ID** | US-4.2 |
| **Epic** | Execution Engine |
| **Priority** | P0 |

**User Story:**
```
As a trader,
I want my SELL order to execute exactly at the specified time,
So that I exit the market at my planned exit point.
```

**Acceptance Criteria:**
- [ ] AC-4.2.1: Scheduler triggers within 300ms of sell_time
- [ ] AC-4.2.2: SELL order placed only if position = BOUGHT
- [ ] AC-4.2.3: Position updated to SOLD on success
- [ ] AC-4.2.4: Order logged to database
- [ ] AC-4.2.5: Skip if already exited by stop-loss

---

#### US-4.3: Stop-Loss Execution

| Attribute | Value |
|-----------|-------|
| **Story ID** | US-4.3 |
| **Epic** | Execution Engine |
| **Priority** | P0 |

**User Story:**
```
As a trader,
I want my position to automatically exit when price hits stop-loss,
So that my losses are limited even if I'm not watching.
```

**Acceptance Criteria:**
- [ ] AC-4.3.1: System monitors price in real-time
- [ ] AC-4.3.2: When price ≤ stop_loss, SELL triggered within 5ms
- [ ] AC-4.3.3: Position updated to EXITED_BY_SL
- [ ] AC-4.3.4: Scheduled SELL job cancelled
- [ ] AC-4.3.5: UI shows "STOP-LOSS HIT" in red
- [ ] AC-4.3.6: Order logged to database

---

#### US-4.4: Order Retry on Failure

| Attribute | Value |
|-----------|-------|
| **Story ID** | US-4.4 |
| **Epic** | Execution Engine |
| **Priority** | P0 |

**User Story:**
```
As a platform,
I want to retry failed orders automatically,
So that temporary broker issues don't cause missed trades.
```

**Acceptance Criteria:**
- [ ] AC-4.4.1: On broker timeout, retry order
- [ ] AC-4.4.2: Maximum 3 retry attempts
- [ ] AC-4.4.3: Log each retry attempt
- [ ] AC-4.4.4: After 3 failures, mark strategy as failed
- [ ] AC-4.4.5: Notify user of failure

---

#### US-4.5: Duplicate Order Prevention

| Attribute | Value |
|-----------|-------|
| **Story ID** | US-4.5 |
| **Epic** | Execution Engine |
| **Priority** | P0 |

**User Story:**
```
As a platform,
I want to prevent duplicate orders,
So that users don't accidentally buy/sell twice.
```

**Acceptance Criteria:**
- [ ] AC-4.5.1: Redis lock acquired before order placement
- [ ] AC-4.5.2: If lock already held, skip order
- [ ] AC-4.5.3: Lock released after order completion
- [ ] AC-4.5.4: 100% prevention of duplicate orders

---

### 4.5 Monitoring Stories

---

#### US-5.1: Real-Time Price Feed

| Attribute | Value |
|-----------|-------|
| **Story ID** | US-5.1 |
| **Epic** | Monitoring |
| **Priority** | P0 |

**User Story:**
```
As a system,
I want to receive real-time price updates,
So that I can trigger stop-loss immediately when needed.
```

**Acceptance Criteria:**
- [ ] AC-5.1.1: Connect to broker WebSocket
- [ ] AC-5.1.2: Subscribe to symbols with active strategies
- [ ] AC-5.1.3: Update price in Redis on each tick
- [ ] AC-5.1.4: Auto-reconnect on disconnect
- [ ] AC-5.1.5: Handle malformed price data gracefully

---

#### US-5.2: Strategy Status Polling

| Attribute | Value |
|-----------|-------|
| **Story ID** | US-5.2 |
| **Epic** | Monitoring |
| **Priority** | P0 |

**User Story:**
```
As a trader using the mobile app,
I want to see updated strategy status,
So that I know what's happening with my trades.
```

**Acceptance Criteria:**
- [ ] AC-5.2.1: App polls backend every 5 seconds
- [ ] AC-5.2.2: Response includes status, position, last action
- [ ] AC-5.2.3: Response includes last price
- [ ] AC-5.2.4: UI updates without full refresh
- [ ] AC-5.2.5: Works even when app in background (limited)

---

## 5. Acceptance Criteria Summary

### 5.1 Acceptance Criteria by Priority

| Priority | Total Stories | Total Criteria |
|----------|---------------|----------------|
| P0 (Critical) | 15 | 72 |
| P1 (Important) | 3 | 12 |
| **Total** | **18** | **84** |

### 5.2 Acceptance Criteria by Epic

| Epic | Stories | Criteria |
|------|---------|----------|
| Authentication | 3 | 18 |
| Broker Integration | 2 | 13 |
| Strategy Management | 5 | 26 |
| Execution Engine | 5 | 21 |
| Monitoring | 2 | 10 |
| **Total** | **17** | **88** |

### 5.3 Testing Traceability

Each acceptance criterion maps to:
- **Unit Test**: Technical implementation verification
- **Integration Test**: Component interaction verification
- **E2E Test**: User flow verification

---

## Appendix: Story Map

```
                                    USER JOURNEY
    ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
    │ Register │  Login   │ Connect  │  Create  │  Start   │ Monitor  │
    │          │          │  Broker  │ Strategy │ Strategy │  Status  │
    └────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘
         │          │          │          │          │          │
    ┌────┴────┐┌────┴────┐┌────┴────┐┌────┴────┐┌────┴────┐┌────┴────┐
    │ US-1.1  ││ US-1.2  ││ US-2.1  ││ US-3.1  ││ US-3.3  ││ US-3.5  │
    │Register ││ Login   ││ Connect ││ Create  ││ Start   ││ View    │
    └─────────┘└─────────┘└─────────┘└─────────┘└─────────┘└─────────┘
                                          │          │
                                     ┌────┴────┐┌────┴────┐
                                     │ US-3.2  ││ US-3.4  │
                                     │ Req SL  ││ Stop    │
                                     └─────────┘└─────────┘

                                SYSTEM (BACKGROUND)
    ┌───────────────────┬───────────────────┬───────────────────┐
    │    Time-Based     │    Price-Based    │    Reliability    │
    │    Execution      │    Execution      │                   │
    └────────┬──────────┴────────┬──────────┴────────┬──────────┘
             │                   │                   │
    ┌────────┴────────┐ ┌────────┴────────┐ ┌────────┴────────┐
    │     US-4.1      │ │     US-4.3      │ │     US-4.4      │
    │   Time BUY      │ │   Stop-Loss     │ │     Retry       │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
    ┌─────────────────┐                     ┌─────────────────┐
    │     US-4.2      │                     │     US-4.5      │
    │   Time SELL     │                     │  No Duplicates  │
    └─────────────────┘                     └─────────────────┘
```

---

**Document Owner:** Product Team  
**Last Updated:** December 2024  
**Related Documents:** [PRD.md](PRD.md), [SRS.MD](SRS.MD), [QA-EXECUTION-MATRIX.md](QA-EXECUTION-MATRIX.md)
