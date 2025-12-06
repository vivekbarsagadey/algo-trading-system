# 📘 **High-Level Design (HLD)**

### **Algo Trading System – High-Speed, Multi-Tenant Automated Trading Platform**

---

# **1. System Overview**

The Algo Trading System consists of:

1. **Mobile App (React Native / Expo)**
2. **Backend REST API (FastAPI)**
3. **Execution Engine (Python microservice)**
4. **Scheduler Service (Time-based triggers)**
5. **Market Listener (WebSocket price feed)**
6. **Redis (In-memory execution runtime)**
7. **PostgreSQL (persistent storage)**
8. **Broker Integration Layer (e.g., Zerodha API wrapper)**
9. **AWS Infrastructure (ECS/EKS, ElastiCache, RDS, CloudWatch)**

The system executes BUY/SELL/SL orders with microsecond-level Redis access and minimal latency.

---

# **2. High-Level Architecture Diagram (Text Form)**

(If you want, I will generate a **PNG version**.)

```
                 ┌──────────────────────────┐
                 │        Mobile App         │
                 │  - Register/Login         │
                 │  - Broker Key Input       │
                 │  - Strategy Creation      │
                 │  - Start/Stop Strategy    │
                 └──────────────┬───────────┘
                                │ HTTPS/REST
                                ▼
                 ┌──────────────────────────┐
                 │      FastAPI Backend     │
                 │  Auth API                │
                 │  Strategy API            │
                 │  Broker Validation API   │
                 └───────────┬──────────────┘
                     ┌───────┴──────────┐
                     ▼                  ▼
        ┌───────────────────┐   ┌──────────────────────┐
        │ Strategy Manager   │   │  Broker Connector     │
        │ (validation, save) │   │  Zerodha Wrapper      │
        └───────┬───────────┘   └─────────┬────────────┘
                │                         │
                ▼                         ▼
         ┌────────────────┐       ┌──────────────────────┐
         │   Redis Cache   │<---->│   Execution Engine    │
         │  (runtime state)│       │  (order placement)   │
         └─────────┬──────┘       └──────────────────────┘
                   │          
                   │          
       ┌───────────▼───────────┐       ┌──────────────────────────┐
       │       Scheduler        │       │      Market Listener      │
       │  (Buy/Sell timers)     │       │  (WebSocket price feed)  │
       └───────────┬───────────┘       └──────────┬───────────────┘
                   │                               │
                   └───────────────┬───────────────┘
                                   ▼
                    ┌─────────────────────────┐
                    │   PostgreSQL (RDS)       │
                    │ Users / Strategies / Logs │
                    └──────────────────────────┘
```

---

# **3. Component-Level Design**

---

# **3.1 Mobile App (Frontend)**

### **Responsibilities**

* User authentication
* Broker API key entry
* Strategy creation and modification
* Start/Stop strategy
* Show status (Running, Stopped, Last action)

### **Technology**

* React Native / Expo
* Axios or Fetch for API calls
* Secure Storage for tokens

### **Key Modules**

* Auth Module
* Broker Setup Module
* Strategy Creator
* Strategy Controller

---

# **3.2 FastAPI Backend (API Layer)**

### **Responsibilities**

* User Auth (JWT)
* Strategy creation/validation
* Storing strategies in DB
* Pushing strategy into Redis for execution
* Managing Start/Stop lifecycle

### **API Endpoints**

(From Document Pack: )

| Endpoint                  | Purpose                |
| ------------------------- | ---------------------- |
| POST /auth/register       | Register user          |
| POST /auth/login          | Login user             |
| POST /broker/connect      | Validate/save API keys |
| POST /strategy/create     | Create strategy        |
| POST /strategy/start      | Start strategy         |
| POST /strategy/stop       | Stop strategy          |
| GET /strategy/status/{id} | Get runtime status     |

### **Internal Modules**

* Strategy Manager
* Broker Validator
* Redis Publisher
* User Manager

---

# **3.3 Strategy Manager**

### **Responsibilities**

* Validate strategies
* Save strategy to DB
* Load runtime strategy into Redis
* Update strategy changes instantly
* Maintain mapping:

  * strategyId → Redis keys
  * symbol → strategy list

### **Data Written to Redis**

(From Redis structure: )

```
strategy:{id}
runtime:{id}
symbol:{symbol}:strategies
```

### **Example Redis Strategy Object**

```
{
  "symbol": "TCS",
  "buy_time": "09:30:00",
  "sell_time": "15:30:00",
  "stop_loss": 3500,
  "quantity": 10,
  "status": "running"
}
```

---

# **3.4 Scheduler Service**

### **Responsibilities**

* Create precise triggers for:

  * BUY at buy_time
  * SELL at sell_time
* Use APScheduler or custom event loop
* Trigger Execution Engine via Redis queues

### **Flow**

```
1. Load strategy settings from Redis
2. Register APScheduler job for BUY time
3. Register job for SELL time
4. On trigger → push order event to Redis (queue:orders)
```

### **Timing Accuracy**

* <100–300 ms latency (from PRD)
* Clock synchronized using NTP

---

# **3.5 Market Listener (Price Feed Engine)**

### **Responsibilities**

* Connect to broker WebSocket
* Receive live tick data
* For each tick:

  * Compare last_price ≤ stop_loss
  * If SL hit → push SELL event immediately
* Maintain per-symbol listener

### **Flow**

```
1. Subscribe to price feed for active symbols
2. Receive tick (price)
3. For each strategy in symbol:{symbol}:strategies
       if price <= stop_loss:
           push SELL event to Redis queue
```

---

# **3.6 Execution Engine**

### **Responsibilities**

* Process tasks in `queue:orders` (Redis list)
* Execute BUY, SELL, SL instantly
* Acquire Redis lock to prevent double execution
* Write logs to DB
* Update runtime state in Redis

### **Execution Flow**

```
1. Pop from queue:orders
2. Validate strategy state in Redis
3. Acquire lock: runtime:{id}:lock
4. Place order via Broker Connector
5. Update runtime:{id} state
6. Release lock
7. Log to DB
```

### **Order Types**

* BUY
* SELL
* STOP-LOSS SELL

### **Retry Logic**

* Retry 3 times on broker timeout
* If all fail → mark order as failed & stop strategy

---

# **3.7 Redis In-Memory Runtime**

Redis is the **heart of the system**.

### **Stores**

* Active strategies
* Current price
* Runtime state
* Position state
* Lock state
* Symbol → strategy mapping
* Orders queue

### **Key Design Goals**

* Microsecond-level access
* Minimal latency for signals
* Ensures isolation & concurrency safety

---

# **3.8 Broker Integration Layer**

### **Responsibilities**

* Wrap broker APIs (Zerodha)
* Handle access token authentication
* Provide normalized API:

  * place_order()
  * get_price()
  * validate_credentials()

### **Order Placement API (Example)**

```
broker.place_order(
    type="BUY",
    symbol="TCS",
    qty=10,
    order_type="MARKET"
)
```

---

# **3.9 Database (PostgreSQL)**

### **Tables**

#### **Users**

* id
* email
* password_hash

#### **BrokerKeys**

* encrypted API key
* encrypted secret key
* encrypted access token

#### **Strategies**

* strategy_id
* user_id
* symbol
* buy_time
* sell_time
* stop_loss
* quantity
* status

#### **OrderLogs**

* order_id
* strategy_id
* type
* timestamp
* raw_response

---

# **4. Data Flow Diagrams (DFD)**

---

# **4.1 Strategy Creation Flow**

```
Mobile App → Strategy API → Validate → Store in DB → Load to Redis → Scheduler activates
```

### **Step-by-step**

1. User submits strategy
2. Backend validates
3. Strategy saved to DB
4. Strategy pushed to Redis
5. Symbol mapping updated
6. Scheduler registers triggers

---

# **4.2 Strategy Execution Flow**

```
Scheduler/Market Listener → Redis Queue → Execution Engine → Broker API → Update Redis
```

### Steps:

1. Trigger event created
2. Task pushed to Redis queue
3. Execution Engine pops task
4. Order placed
5. Runtime updated
6. Logs stored

---

# **4.3 Stop-Loss Flow**

```
Tick Received → Compare with SL → SL Trigger → Push to Queue → Execute Immediately
```

Stop-loss ALWAYS has the highest priority.

---

# **5. Non-Functional Design Considerations**

---

# **5.1 Scalability**

The system supports:

* 100 → 500 → 1000+ parallel strategies
* Redis cluster for horizontal scaling
* Multiple Execution Engines (workers)
* Stateless API servers

---

# **5.2 Availability**

* Target uptime: **99%**
* Health checks
* Auto-scaling
* Auto-restart on crash

---

# **5.3 Performance**

| Component               | Target          |
| ----------------------- | --------------- |
| Order execution latency | < 300 ms        |
| Redis operations        | < 1 ms          |
| Tick processing rate    | 1000+ ticks/sec |
| Concurrency             | 500+ strategies |

---

# **5.4 Security Architecture**

* Zero API keys stored unencrypted
* AES-256 encryption for credentials
* JWT for session tokens
* HTTPS enforced
* RBAC for admin tools

---

# **6. Deployment Architecture**

---

# **6.1 AWS Infrastructure**

### **Compute**

* ECS or EKS cluster
* Auto-scaling enabled

### **Data Layer**

* RDS PostgreSQL
* ElastiCache Redis

### **Networking**

* Load balancer → API servers
* Private VPC for backend
* NAT gateway for broker communication

### **Monitoring**

* CloudWatch logs
* CloudWatch metrics
* Error alerts

---

# **7. High-Level Sequence Diagrams**

---

# **7.1 Buy Order Sequence**

```
Scheduler → Redis Queue → Execution Engine → Broker API → Redis Runtime → DB Log
```

---

# **7.2 Stop-Loss Sequence**

```
Market Listener → SL Check → Redis Queue → Execution Engine → Broker → Update Runtime
```

---

# **8. Risks & Mitigations**

| Risk                 | Mitigation                                   |
| -------------------- | -------------------------------------------- |
| Broker downtime      | Retry logic, alerts                          |
| Redis crash          | Use Redis cluster with replicas              |
| Delayed execution    | Dedicated scheduler worker, optimized timers |
| WebSocket disconnect | Auto-reconnect logic                         |
| Token expiration     | User notified to update access token         |

---

# ✔ Your HLD Is Ready

If you want, I can generate:

✅ **A clean PNG architecture diagram**
✅ **A DOCX/PDF version of this HLD**
✅ **Low-Level Design (LLD)** (extremely detailed)
✅ **Backend-SPEC.md**
✅ **Frontend-SPEC.md**
✅ **API contract document**
✅ **Shell script to generate folder structure**

