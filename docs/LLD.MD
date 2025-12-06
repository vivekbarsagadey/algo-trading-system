**FULL Low-Level Design (LLD)** for the Algo Trading System.

This will be extremely detailed and developer-ready.
It will include:

✔ Microservice-by-microservice LLD
✔ Directory structures
✔ Class diagrams
✔ Function-level details
✔ Redis & DB schema with keys and data types
✔ API request/response schemas
✔ Internal event flows
✔ Error handling design
✔ Worker design
✔ Sequence flows

---

# 📘 **LOW-LEVEL DESIGN (LLD)**

### **Algo Trading System – Python (FastAPI + Redis) + Mobile App**

---

# **1. Overall System Modules**

Below are the main components for which LLD will be defined:

1. **Auth Service**
2. **Broker Service**
3. **Strategy Service**
4. **Scheduler Service**
5. **Market Listener**
6. **Execution Engine**
7. **Redis Runtime Store**
8. **Database Models (PostgreSQL)**
9. **Mobile App (React Native)**

---

# **2. Backend Folder Structure (LLD Level)**

```
backend/
│
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
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
│
├── requirements.txt
└── Dockerfile
```

---

# **3. Database Table-level LLD (PostgreSQL)**

---

## **3.1 users Table**

| Column        | Type         | Description     |
| ------------- | ------------ | --------------- |
| id            | UUID         | Primary Key     |
| email         | VARCHAR(255) | Unique          |
| password_hash | TEXT         | Hashed password |
| created_at    | TIMESTAMP    | Default now     |

---

## **3.2 broker_keys Table**

| Column       | Type      | Description            |
| ------------ | --------- | ---------------------- |
| user_id      | UUID      | FK → users.id          |
| api_key      | TEXT      | AES-256 encrypted      |
| secret_key   | TEXT      | AES-256 encrypted      |
| access_token | TEXT      | AES-256 encrypted      |
| updated_at   | TIMESTAMP | Token refresh tracking |

---

## **3.3 strategies Table**

| Column      | Type        | Description                 |
| ----------- | ----------- | --------------------------- |
| strategy_id | UUID        | Primary Key                 |
| user_id     | UUID        | Owner                       |
| symbol      | VARCHAR(25) | Stock symbol                |
| buy_time    | TIME        | Buy trigger time            |
| sell_time   | TIME        | Sell trigger time           |
| stop_loss   | FLOAT       | SL                          |
| quantity    | INT         | Order qty                   |
| status      | VARCHAR(20) | created / running / stopped |
| created_at  | TIMESTAMP   |                             |
| updated_at  | TIMESTAMP   |                             |

---

## **3.4 order_logs Table**

| Column       | Type        | Description          |
| ------------ | ----------- | -------------------- |
| order_id     | UUID        | PK                   |
| strategy_id  | UUID        | FK                   |
| order_type   | VARCHAR(10) | BUY / SELL / SL      |
| timestamp    | TIMESTAMP   |                      |
| raw_response | JSONB       | Full broker response |

---

# **4. Redis Runtime LLD**

### Redis Key: `strategy:{id}`

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

### Redis Key: `runtime:{id}`

```
{
  "position": "none | bought | sold",
  "last_buy_order": "order_id",
  "last_sell_order": "order_id",
  "last_price": 3525.50,
  "lock": "true/false"
}
```

### Redis Key: `symbol:{symbol}:strategies`

```
["strategy_uuid_1", "strategy_uuid_2"]
```

### Redis Queue: `queue:orders`

* Holds order events for Execution Engine.

```
{
  "strategy_id": "...",
  "event": "BUY | SELL | STOPLOSS",
  "timestamp": "..."
}
```

---

# **5. Microservice LLD**

---

# **5.1 Auth Service (FastAPI)**

### **Functions**

```
register_user(email, password) → JWT
login_user(email, password) → JWT
hash_password(password)
verify_password(password, hash)
generate_jwt(user_id)
```

### **Error Cases**

* Email already exists
* Wrong password
* Invalid token

---

# **5.2 Broker Service**

### **Functions**

```
save_broker_keys(user_id, api_key, secret, token)
validate_broker_credentials(api_key, secret, token) → bool
encrypt(value)
decrypt(value)
```

### **Integration**

Uses Zerodha’s `/profile` endpoint for validation.

### **Error Handling**

* Invalid token → return "BROKER_AUTH_FAILED"
* API rate limit exceeded → retry logic

---

# **5.3 Strategy Service**

### **Functions**

```
create_strategy(data)
validate_strategy(data)
save_to_db(strategy)
load_to_redis(strategy)
update_strategy(strategy_id, new_data)
start_strategy(strategy_id)
stop_strategy(strategy_id)
```

### **Key Internal Logic**

* Ensures stop-loss is mandatory
* Ensures buy_time < sell_time
* Prevents overlapping strategies

---

# **5.4 Scheduler Worker (APScheduler)**

### **Core Functions**

```
schedule_buy(strategy_id, buy_time)
schedule_sell(strategy_id, sell_time)
trigger_buy(strategy_id)
trigger_sell(strategy_id)
```

### **Flow Example**

```
schedule_buy() → at 09:30 → push {"event": "BUY"} into queue:orders
```

### **Edge Cases**

* Missed trigger due to server restart → immediate execution

---

# **5.5 Market Listener**

### **Functions**

```
subscribe(symbol)
on_tick(symbol, price)
check_stop_loss(strategy_id, price)
push_sl_event(strategy_id)
```

### **SL Trigger Logic**

```
if price <= stop_loss:
     push {event: "STOPLOSS"} to Redis queue
```

### **Error Handling**

* WebSocket disconnect → auto-reconnect in 2 sec
* Invalid tick → ignore

---

# **5.6 Execution Engine (Worker)**

### **Functions**

```
run_worker()
fetch_order_event()
acquire_lock(strategy_id)
execute_buy()
execute_sell()
execute_stoploss()
update_runtime_state()
log_order_to_db()
release_lock()
```

### **Execution Flow**

```
1. Pop event from queue
2. Validate state
3. Acquire Redis lock
4. Call broker.place_order()
5. Update runtime:{id}
6. Release lock
7. Commit log to DB
```

### **Lock Mechanism**

Key: `runtime:{id}:lock`
Prevent double-order execution.

### **Retry Logic**

* Retry 3 times on failure
* If all fail → stop strategy

---

# **6. Event Flow LLD**

---

# **6.1 Buy Event (Detailed)**

```
Scheduler → Redis.queue → Execution Engine → Zerodha API → Redis.runtime → DB.log
```

### Step-by-step:

1. Scheduler triggers at exact buy_time
2. Push event `{type: BUY}`
3. Worker pops event
4. Worker checks:

   * status == running
   * position == none
5. Worker sends BUY order
6. Update Redis:

```
runtime:{id}.position = "bought"
last_buy_order = broker_order_id
```

7. Log into DB

---

# **6.2 Stop Loss Event**

```
Market Listener → Redis.queue → Execution Engine → Broker → Redis → DB
```

Stop-loss overrides all other events.

---

# **7. API Contract LLD**

---

## **7.1 POST /strategy/create**

### Request

```
{
  "symbol": "TCS",
  "buy_time": "09:30:00",
  "sell_time": "15:30:00",
  "stop_loss": 3500,
  "quantity": 10
}
```

### Response

```
{
  "strategy_id": "uuid",
  "status": "created"
}
```

---

## **7.2 POST /strategy/start**

### Response

```
{
  "strategy_id": "uuid",
  "status": "running"
}
```

---

## **7.3 GET /strategy/status/{id}**

### Response

```
{
  "strategy_id": "uuid",
  "status": "running",
  "last_action": "BUY",
  "position": "bought"
}
```

---

# **8. Mobile App (React Native) LLD**

---

## **8.1 Screen: ConnectBroker.jsx**

### State

```
apiKey
secretKey
accessToken
validationStatus
```

### Function

```
submitKeys() → POST /broker/connect
```

---

## **8.2 Screen: CreateStrategy.jsx**

### State

```
symbol
buyTime
sellTime
stopLoss
quantity
```

### Function

```
createStrategy() → POST /strategy/create
```

---

## **8.3 Screen: StrategyControl.jsx**

### Actions

* Start strategy
* Stop strategy
* View status

### Interval Polling

Every **5 seconds**, call:

```
GET /strategy/status/{id}
```

---

# **9. Error Handling LLD**

| Error              | Component        | Behavior                   |
| ------------------ | ---------------- | -------------------------- |
| BROKER_AUTH_FAILED | broker_service   | Ask user to re-enter token |
| ORDER_FAILED       | execution_engine | Retry 3 times              |
| REDIS_DOWN         | all workers      | Stop safely + alert        |
| STRATEGY_INVALID   | strategy_service | 400 Bad Request            |
| TOKEN_EXPIRED      | auth             | 401 Unauthorized           |

---

# **10. Logging LLD**

### Log Fields:

```
timestamp
component
event_type
strategy_id
user_id
execution_time_ms
broker_response
```

Logs stored in:

* DB (order logs)
* CloudWatch (system logs)

---

# **11. LLD Summary**

This LLD now includes:

✔ Microservice-level internal functions
✔ Redis schema
✔ Database schema
✔ Exact workflow of BUY/SELL/SL
✔ Class-level breakdown
✔ Worker logic
✔ Scheduler + Listener design
✔ Mobile UI LLD
✔ Error handling & logging

---

# ✅ What do you want next?

I can create any of these next:

### **A. BACKEND-SPEC.md (Developer bible)**

### **B. FRONTEND-SPEC.md**

### **C. WORKFLOW-SCHEMA.md**

### **D. FOLDER STRUCTURE + auto-create shell script**

### **E. Architecture PNG diagram**

### **F. API documentation in Swagger/OpenAPI format**

