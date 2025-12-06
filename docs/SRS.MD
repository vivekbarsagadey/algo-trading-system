
# 📘 **Software Requirements Specification (SRS)**

### **Algo Trading System – High-Speed, Multi-Tenant Trading Automation**

---

# **1. Introduction**

## **1.1 Purpose**

The purpose of this SRS is to define detailed functional, non-functional, system, integration, and operational requirements for the Algo Trading System.
This system enables retail users to automate simple trading strategies using a mobile app while the backend executes logic with high-speed in-memory computation using Redis.

The SRS is intended for:

* Product owners
* Backend developers (FastAPI, Redis, AWS)
* Mobile developers (React Native / Expo)
* QA testers
* DevOps engineers
* Stakeholders, investors

---

## **1.2 Scope**

The system allows users to:

* Register/login
* Add broker API credentials (e.g., Zerodha)
* Create simple predefined strategies:

  * Buy time
  * Sell time
  * Stop-loss
  * Symbol
  * Quantity
* Start/Stop the strategy
* Allow backend to execute trades securely and automatically
* Monitor live price and enforce mandatory stop-loss

Backend ensures:

* Exact execution timing
* Fail-safe order placement
* Independent, isolated multi-tenant strategy execution
* High-speed Redis-based runtime

---

## **1.3 Definitions & Acronyms**

| Term                 | Definition                                                     |
| -------------------- | -------------------------------------------------------------- |
| **Algo Strategy**    | A predefined automation defining buy/sell times and stop-loss. |
| **Broker API**       | Trading broker integration (ex: Zerodha Kite).                 |
| **Execution Engine** | Backend service responsible for placing orders.                |
| **Scheduler**        | Time-based trigger system.                                     |
| **Market Listener**  | Monitors live prices via WebSockets.                           |
| **Redis Runtime**    | In-memory execution state for speed.                           |
| **SL**               | Stop Loss.                                                     |
| **JWT**              | JSON Web Token authentication.                                 |

---

# **2. Overall System Description**

## **2.1 Product Perspective**

The system consists of:

### **Frontend (Mobile App)**

* Built using React Native / Expo
* Minimal UI
* API-driven

### **Backend**

* FastAPI microservices
* Redis (active strategy state)
* PostgreSQL (persistent storage)
* AWS ECS/EKS deployment
* CloudWatch logging

(From PRD & Document Pack:  )

---

## **2.2 User Types**

### **Primary Users**

* Retail traders
* Beginners with minimal trading knowledge
* Users wanting automated execution with minimal inputs

### **Secondary Users**

* Existing traders wanting simple automation
* Users running fixed-time strategies daily

---

## **2.3 Constraints**

* Broker API rate limits
* Mandatory stop-loss for safety
* In-memory execution must be failsafe
* Strategies must run independently (multi-tenant isolation)

---

## **2.4 Assumptions**

* Users will manually generate and enter broker access tokens.
* Internet connectivity is stable during trading sessions.
* Broker APIs are available and functioning.

---

# **3. Functional Requirements**

---

# **3.1 Authentication Module**

### **FR-1: User Registration**

The system shall allow users to register using:

* Email or mobile
* Password

### **FR-2: Password Encryption**

Passwords shall be stored using secure hashing (bcrypt/argon2).

### **FR-3: User Login**

The system shall allow users to log in and receive a JWT token.

### **FR-4: Forgot Password**

The system shall support password reset via email/mobile OTP.

---

# **3.2 Broker Integration Module**

### **FR-5: Add Broker Credentials**

User must submit:

* API Key
* Secret Key
* Access Token

(From PRD: )

### **FR-6: Credential Validation**

Backend shall validate the user’s broker credentials via a test API call.

### **FR-7: Secure Storage**

All keys must be stored encrypted (AES-256).

---

# **3.3 Strategy Management**

### **FR-8: Create Strategy**

User must be able to define:

| Field     | Type     | Mandatory |
| --------- | -------- | --------- |
| Symbol    | string   | Yes       |
| Buy Time  | HH:MM:SS | Yes       |
| Sell Time | HH:MM:SS | Yes       |
| Stop Loss | number   | Yes       |
| Quantity  | integer  | Yes       |

### **FR-9: Strategy Validation**

Backend must reject:

* Invalid times
* Invalid stop-loss
* Missing fields

### **FR-10: Strategy Persistence**

Save a copy of the strategy to DB.

### **FR-11: Load Strategy to Redis**

Once started, the strategy is moved to in-memory runtime.

### **FR-12: Update Strategy**

User may modify:

* Stop-loss
* Times
* Quantity
  Changes must update Redis instantly.

### **FR-13: Start/Stop Strategy**

User can toggle strategy status.

### **FR-14: Strategy Status API**

Return:

* Running / Stopped
* Last action (Buy/Sell/SL triggered)

---

# **3.4 Execution Engine**

### **FR-15: Time-Based Execution**

At Buy Time → place BUY order.
At Sell Time → place SELL order.

### **FR-16: Event-Based Execution**

System must monitor live prices for:

* Stop-loss
* Threshold-based triggers

### **FR-17: Stop-Loss Enforcement**

Stop-loss execution must take priority over any other order.

### **FR-18: Redis Locking**

Each strategy must use Redis lock state to prevent double execution.

### **FR-19: Order Logging**

All order attempts must be logged to DB.

---

# **3.5 Scheduler Module**

### **FR-20: Accurate Time Triggers**

Delay must be <300 ms (from PRD: ).

### **FR-21: Missed Execution Handling**

If time is missed by a short interval, system must execute immediately.

---

# **3.6 Market Listener Module**

### **FR-22: Price Subscription**

Connect to Broker WebSocket feed.

### **FR-23: Real-Time SL Monitoring**

If price <= SL → immediately trigger SELL.

### **FR-24: Error Handling**

If price feed disconnects:

* Attempt reconnection
* Notify backend logs

---

# **3.7 Multi-Tenant System Requirements**

### **FR-25: Strategy Isolation**

User A’s strategy must not interfere with User B’s.

### **FR-26: Redis Namespace Separation**

Each strategy must have unique Redis keys.

### **FR-27: User-Level Resource Limits**

Max quantity per user must be enforced.

---

# **3.8 Safety Requirements**

### **FR-28: Mandatory Stop-Loss**

User cannot create a strategy without an SL.

### **FR-29: Retry on Order Failure**

At least 3 retries before marking failure.

### **FR-30: Fail-Safe Shutdown**

If strategy misbehaves:

* Stop immediately
* Notify logs

---

# **4. Non-Functional Requirements**

---

# **4.1 Performance Requirements**

(from PRD: Execution <300 ms, Redis microseconds — )

| Component                  | Requirement           |
| -------------------------- | --------------------- |
| Order execution delay      | < 300 ms              |
| Redis read/write           | < 1 ms                |
| Price monitoring frequency | real-time (WebSocket) |
| Parallel strategies        | 500+                  |

---

# **4.2 Security Requirements**

### **NFR-1: Encryption**

* AES-256 for broker keys
* TLS 1.2+ for all communication

### **NFR-2: Authentication**

* JWT-based user sessions

### **NFR-3: Access Control**

Users must only access their own strategies.

---

# **4.3 Scalability Requirements**

### **NFR-4: Horizontal Scaling**

Backend must scale via AWS ECS/EKS.

### **NFR-5: Redis Cluster Support**

The system must allow scaling Redis for high load.

### **NFR-6: Stateless Backend**

All stateful components must run inside Redis/DB.

---

# **4.4 Availability Requirements**

### **NFR-7: Uptime**

System uptime target: **99%**.

### **NFR-8: Auto-Restart**

Containers restart after crash automatically.

---

# **4.5 Logging & Monitoring Requirements**

Use AWS CloudWatch for:

* Strategy lifecycle logs
* Stop-loss logs
* API failures
* Order execution logs

Alerts for:

* Strategy crash
* Redis failure
* Broker downtime

()

---

# **5. External Interface Requirements**

---

# **5.1 Mobile App UI Screens**

(Expanded from wireframes: )

### Screen 1 – Login

* Email, password
* Login button
* Register link

### Screen 2 – Register

* Name, email, password

### Screen 3 – Connect Broker

* API Key
* Secret Key
* Access Token

### Screen 4 – Create Strategy

* Symbol
* Buy time
* Sell time
* Stop-loss
* Quantity

### Screen 5 – Strategy Control

* Start/Stop
* Status card
* Last action

---

# **6. System Models**

---

# **6.1 Redis Key Structure**

(from Document Pack: )

```
user:{userId}
strategy:{strategyId}
runtime:{strategyId}
symbol:{symbol}:strategies
queue:orders
```

---

# **6.2 Database Schema (High Level)**

### **User Table**

* id
* email
* password_hash
* created_at

### **BrokerKeys**

* user_id
* api_key (encrypted)
* secret_key (encrypted)
* access_token (encrypted)

### **Strategies**

* id
* user_id
* symbol
* buy_time
* sell_time
* stop_loss
* quantity
* status

### **OrderLogs**

* id
* strategy_id
* type (BUY/SELL/SL)
* timestamp
* response

---

# **7. Success Metrics**

(from PRD: )

| Metric                     | Target        |
| -------------------------- | ------------- |
| Onboarding time            | < 2 minutes   |
| Strategy creation time     | < 1 minute    |
| Execution delay            | < 0.5 seconds |
| Stop-loss reliability      | 99%           |
| API key validation success | 95%           |

---

# **8. Future Enhancements (Not part of MVP)**

(from PRD: )

* Multiple strategies
* Multiple symbols
* P&L analytics
* Push notifications
* Auto-refresh broker tokens

---

# ✔ **Your SRS is Ready**

This is now a **fully expanded, professional-grade SRS** aligned with your PRD and Document Pack.

If you want, I can also generate:

✅ PDF version
✅ DOCX version
✅ Architecture Diagram PNG
✅ API Contracts (Deep-level)
✅ Full HLD + LLD
✅ Developer onboarding handbook
✅ Swagger/OpenAPI spec

Just tell me **“Convert SRS to PDF”** or **“Give me HLD next”**.
