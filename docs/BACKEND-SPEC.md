# 📘 **BACKEND-SPEC.md**

### **Algo Trading System – FastAPI + Redis + Worker Architecture**


# **1. Overview**

The backend of the Algo Trading System is a **high-performance, event-driven architecture** that manages:

* User authentication
* Broker integration
* Strategy creation
* Time-based & event-based automation
* Redis in-memory execution
* Stop-loss monitoring
* Worker-driven order placement
* Logging & monitoring

The design meets all PRD backend requirements: strategy management, time-based triggers, event-based execution, multi-tenant isolation, broker connection, safety, and high performance ().



# **2. Technology Stack**

| Component        | Technology          |
| ---------------- | ------------------- |
| API Framework    | FastAPI (Python)    |
| Runtime          | Python 3.11+        |
| In-memory engine | Redis               |
| Database         | PostgreSQL          |
| Scheduler        | APScheduler         |
| Workers          | Async Python Worker |
| Deployment       | AWS ECS/EKS         |
| Logging          | AWS CloudWatch      |
| Secrets          | AWS Secrets Manager |

---

# **3. Backend Architecture**

### Core Backend Components (From PRD & SDD)

 

1. **Auth Service** – JWT-based user authentication
2. **Broker Connector** – Zerodha API wrapper
3. **Strategy Service** – Create, validate, update strategies
4. **Scheduler Service** – Registers BUY/SELL triggers
5. **Market Listener** – Receives real-time prices
6. **Execution Engine** – Places orders & updates runtime
7. **Redis Runtime State** – Stores active strategies
8. **DB Layer** – Persistent strategy, user & log storage

---

# **4. Folder Structure**

```
backend/
│
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logger.py
│   ├── api/
│   │   ├── auth.py
│   │   ├── broker.py
│   │   ├── strategy.py
│   │   └── status.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── broker_service.py
│   │   ├── strategy_service.py
│   │   ├── redis_service.py
│   │   ├── scheduler_service.py
│   │   └── execution_producer.py
│   ├── workers/
│   │   ├── execution_engine.py
│   │   ├── market_listener.py
│   │   └── scheduler_worker.py
│   ├── db/
│   │   ├── session.py
│   │   ├── models.py
│   │   ├── repository/
│   │   │   ├── user_repo.py
│   │   │   ├── strategy_repo.py
│   │   │   ├── orderlog_repo.py
│   │   │   └── broker_repo.py
│   └── utils/
│       ├── encryption.py
│       ├── validators.py
│       └── time_utils.py
```

---

# **5. API Specification (Detailed)**

(Referencing PRD section 4.1, 5, and Document Pack API Contract)
 

Base URL:

```
/api/v1
```

---

## **5.1 Authentication APIs**

### **POST /auth/register**

Registers a new user.

**Request**

```
{
  "email": "user@gmail.com",
  "password": "pass123"
}
```

**Response**

```
{
  "user_id": "uuid",
  "token": "jwt"
}
```

---

### **POST /auth/login**

Logs user in.

**Request**

```
{
  "email": "user@gmail.com",
  "password": "pass123"
}
```

**Response**

```
{
  "token": "jwt"
}
```

---

## **5.2 Broker APIs**

### **POST /broker/connect**

Validates and stores encrypted broker keys.

**Request**

```
{
  "api_key": "",
  "api_secret": "",
  "access_token": ""
}
```

**Response**

```
{
  "status": "connected",
  "broker_valid": true
}
```

**Failure**

```
{ "error": "BROKER_AUTH_FAILED" }
```

---

## **5.3 Strategy APIs**

### **POST /strategy/create**

Creates a strategy.

**Request**

```
{
  "symbol": "TCS",
  "buy_time": "09:30:00",
  "sell_time": "15:30:00",
  "stop_loss": 3500,
  "quantity": 10
}
```

**Response**

```
{
  "strategy_id": "uuid",
  "status": "created"
}
```

---

### **POST /strategy/start**

Loads strategy into Redis and activates scheduler.

**Response**

```
{
  "strategy_id": "uuid",
  "status": "running"
}
```

---

### **POST /strategy/stop**

Stops active strategy.

**Response**

```
{
  "strategy_id": "uuid",
  "status": "stopped"
}
```

---

### **GET /strategy/status/{id}**

Returns runtime status from Redis.

**Response**

```
{
  "strategy_id": "uuid",
  "status": "running",
  "position": "bought",
  "last_action": "BUY",
  "last_price": 3521.50
}
```

---

# **6. Redis Data Structures**

(From Document Pack Redis schema)


---

## **6.1 strategy:{id}**

```
{
  "user_id": "uuid",
  "symbol": "TCS",
  "buy_time": "09:30:00",
  "sell_time": "15:30:00",
  "stop_loss": 3500,
  "quantity": 10,
  "status": "running"
}
```

---

## **6.2 runtime:{id}**

```
{
  "last_price": 3520.75,
  "position": "none | bought | sold",
  "last_buy_order": "...",
  "last_sell_order": "...",
  "lock_state": false
}
```

---

## **6.3 symbol:{symbol}:strategies**

```
[ "strategy1_uuid", "strategy2_uuid" ]
```

---

## **6.4 queue:orders (Redis List)**

Each entry:

```
{
  "strategy_id": "uuid",
  "event": "BUY | SELL | STOPLOSS",
  "timestamp": 1735512323231
}
```

---

# **7. Scheduler Specification**

### Scheduler Responsibilities

* Register BUY time trigger
* Register SELL time trigger
* Push execution events into Redis queue
* Handle missed triggers (run immediately)

### Scheduler Worker Functions

```
def schedule_buy(strategy_id, time)
def schedule_sell(strategy_id, time)
def push_buy_event(strategy_id)
def push_sell_event(strategy_id)
```

### Trigger Precision

< 100–300 ms (PRD requirement)


---

# **8. Market Listener Specification**

### Responsibilities

* Connect to WebSocket price feed
* Maintain subscription only for active symbols
* Compare tick price with stop-loss
* Push STOPLOSS events immediately

### Key Functions

```
def subscribe(symbol)
def on_tick(symbol, price)
def check_stop_loss(strategy_id, price)
```

### SL Priority

Stop-loss must override BUY/SELL and execute immediately.
(From PRD section 5.1 point 3)


---

# **9. Execution Engine Specification**

### Responsibilities

* Process order events FIFO
* Acquire per-strategy lock
* Place BUY/SELL/SL orders
* Update Redis runtime
* Log in DB

### Execution Flow

```
1. Pop event from Redis queue
2. Validate strategy state
3. Acquire lock: runtime:{id}:lock
4. Place order via broker
5. Update runtime attributes
6. Log to DB
7. Release lock
```

### Retry Mechanism

* 3 retries for broker call failures
* If still failing → stop strategy and log failure

(from PRD safety requirement)


---

# **10. Database Schema**

### Tables

* users
* broker_keys
* strategies
* order_logs

Defined fully in LLD.

---

# **11. Security Specification**

(From PRD section 6.4)


### Data Security

* AES-256 encryption for API keys
* JWT token for all calls
* HTTPS enforced

### Access Control

* Users can only access their own strategies

---

# **12. Performance Specification**

(From PRD section 6.1)


| Item                  | Requirement  |
| --------------------- | ------------ |
| Trade execution       | < 300ms      |
| Redis read/write      | microseconds |
| Concurrent strategies | 500+         |
| API response latency  | < 100ms      |

---

# **13. Logging & Monitoring**

From PRD section 6.5


### Log Types

* Strategy lifecycle logs
* BUY/SELL/SL logs
* Error logs
* Broker API logs

### Monitoring

* CloudWatch metrics
* Alerts for:

  * Strategy crash
  * Broker downtime
  * Worker failure

---

# **14. Error Handling Specification**

| Component        | Error                  | Action                                     |
| ---------------- | ---------------------- | ------------------------------------------ |
| Broker           | Authentication failure | Return error to user, stop broker workflow |
| Scheduler        | Missed trigger         | Execute immediately                        |
| Market Listener  | WS disconnect          | Reconnect automatically                    |
| Execution Engine | Order failure          | Retry 3 times                              |
| Redis            | Lock stuck             | Force release after timeout                |
| Strategy         | Invalid input          | 400 Bad Request                            |

---

# **15. Backend Deployment Specification**

### AWS Components

* ECS/EKS cluster
* RDS PostgreSQL
* ElastiCache Redis Cluster
* Secrets Manager
* CloudWatch Logging

### Horizontal Scaling

* Stateless FastAPI servers
* Multiple market listeners
* Multiple execution engines

(From PRD scalability requirements)


---

# ✔ BACKEND-SPEC.md IS COMPLETE

If you want, I can now generate:

### ✅ FRONTEND-SPEC.md

### ✅ WORKFLOW-SCHEMA.md

### ✅ SCHEMA.md

### ✅ A zip-ready folder structure

### ✅ A shell script to auto-generate all backend folders

### ✅ Architecture PNG file

### ✅ Developer Onboarding Guide

