# 📘 **SCHEMA.md**

### **Algo Trading System – Unified Database & Redis Schema**

---

# **1. Overview**

The system uses a hybrid storage model:

| Layer          | Purpose                                                                         |
| -------------- | ------------------------------------------------------------------------------- |
| **PostgreSQL** | Persistent storage (users, strategies, logs, broker keys)                       |
| **Redis**      | In-memory execution state (active strategies, lock state, runtime, order queue) |

This document specifies **tables**, **fields**, **types**, **constraints**, and **relationships**, plus **Redis keys** and **data structures**.

---

# **2. PostgreSQL Schema**

All timestamps use `TIMESTAMP WITH TIME ZONE (UTC)`.

---

## **2.1 users Table**

Holds user account info.

### **Table: users**

| Column        | Type         | Constraints      | Description        |
| ------------- | ------------ | ---------------- | ------------------ |
| id            | UUID         | PK               | Unique user ID     |
| name          | VARCHAR(100) | NULLABLE         | Optional full name |
| email         | VARCHAR(255) | UNIQUE, NOT NULL | Login email        |
| password_hash | TEXT         | NOT NULL         | Bcrypt/Argon2 hash |
| created_at    | TIMESTAMP    | DEFAULT NOW()    | Registration time  |

---

## **2.2 broker_keys Table**

Stores encrypted Zerodha API credentials.

### **Table: broker_keys**

| Column       | Type      | Constraints           | Description                   |
| ------------ | --------- | --------------------- | ----------------------------- |
| id           | UUID      | PK                    | Primary key                   |
| user_id      | UUID      | FK → users.id, UNIQUE | One user = one broker key set |
| api_key      | TEXT      | NOT NULL              | AES-256 encrypted             |
| api_secret   | TEXT      | NOT NULL              | AES-256 encrypted             |
| access_token | TEXT      | NOT NULL              | AES-256 encrypted             |
| created_at   | TIMESTAMP | DEFAULT NOW()         | Added on                      |
| updated_at   | TIMESTAMP | DEFAULT NOW()         | Token refreshed on            |

---

## **2.3 strategies Table**

Stores strategy configuration and lifecycle.

### **Table: strategies**

| Column      | Type        | Constraints       | Description                         |
| ----------- | ----------- | ----------------- | ----------------------------------- |
| strategy_id | UUID        | PK                | Strategy ID                         |
| user_id     | UUID        | FK → users.id     | Strategy owner                      |
| symbol      | VARCHAR(25) | NOT NULL          | Stock/Instrument symbol             |
| buy_time    | TIME        | NOT NULL          | Scheduled buy time                  |
| sell_time   | TIME        | NOT NULL          | Scheduled sell time                 |
| stop_loss   | FLOAT       | NOT NULL          | Mandatory SL (from PRD requirement) |
| quantity    | INT         | NOT NULL          | Quantity to trade                   |
| status      | VARCHAR(20) | DEFAULT 'created' | created / running / stopped         |
| created_at  | TIMESTAMP   | DEFAULT NOW()     | Creation timestamp                  |
| updated_at  | TIMESTAMP   | DEFAULT NOW()     | Last update                         |

### **Constraints**

* **stop_loss MUST NOT be null** (PRD safety rule)
* **buy_time < sell_time**
* **quantity > 0**

---

## **2.4 order_logs Table**

Logs all BUY/SELL/STOPLOSS executions.

### **Table: order_logs**

| Column       | Type        | Constraints                 | Description     |
| ------------ | ----------- | --------------------------- | --------------- |
| order_id     | UUID        | PK                          | Order log ID    |
| strategy_id  | UUID        | FK → strategies.strategy_id | Source strategy |
| user_id      | UUID        | FK → users.id               | Owner           |
| order_type   | VARCHAR(10) | NOT NULL                    | BUY / SELL / SL |
| price        | FLOAT       | NULLABLE                    | Executed price  |
| quantity     | INT         | NULLABLE                    | Quantity        |
| raw_response | JSONB       | NULLABLE                    | Broker response |
| created_at   | TIMESTAMP   | DEFAULT NOW()               | Time executed   |

---

# **3. Database Relationships**

### **User → Broker Keys**

* 1-to-1

```
user.id → broker_keys.user_id
```

### **User → Strategies**

* 1-to-many

```
user.id → strategies.user_id
```

### **Strategies → Order Logs**

* 1-to-many

```
strategies.strategy_id → order_logs.strategy_id
```

### **User → Order Logs**

```
user.id → order_logs.user_id
```

---

# **4. Redis In-Memory Execution Schema**

Redis is the real **execution engine** for strategies (as defined in PRD and SDD).
 

---

## **4.1 Key: user:{userId}**

Basic cached user info.

```
{
  "email": "user@gmail.com",
  "status": "active",
  "broker_connected": true
}
```

---

## **4.2 Key: strategy:{strategyId}**

Represents the *static* configuration of a running strategy.

```
{
  "userId": "uuid",
  "symbol": "TCS",
  "buy_time": "09:30:00",
  "sell_time": "15:30:00",
  "stop_loss": 3500,
  "quantity": 10,
  "status": "running"
}
```

---

## **4.3 Key: runtime:{strategyId}**

Real-time data while strategy is executing.

```
{
  "last_price": 3520.75,
  "position": "none | bought | sold",
  "last_buy_order": "order_id",
  "last_sell_order": "order_id",
  "lock_state": false
}
```

### Notes:

* **lock_state** prevents double BUY/SELL
* **position** controls whether future SELL is valid

---

## **4.4 Key: symbol:{symbol}:strategies**

Tracks which strategies depend on a symbol → used by price listener.

Example:

```
["strategy_uuid_1", "strategy_uuid_2"]
```

---

## **4.5 Key: queue:orders**

Redis list used as FIFO queue for order events.

Each entry:

```
{
  "strategy_id": "uuid",
  "event": "BUY | SELL | STOPLOSS",
  "timestamp": 1735512323231
}
```

### Events:

* BUY (triggered by scheduler)
* SELL (triggered by scheduler)
* STOPLOSS (triggered by market listener)

---

## **4.6 Lock Key (optional)**

`runtime:{strategyId}:lock`

Used for atomic operations.

Values:

```
true / false
```

---

# **5. Auxiliary Runtime Schemas**

---

## **5.1 Scheduler Job Representation**

Not stored in DB — stored in APScheduler or Redis.

```
{
  "strategy_id": "uuid",
  "job_type": "BUY" | "SELL",
  "execute_at": "timestamp"
}
```

---

## **5.2 Price Feed Cache (optional)**

`price:{symbol}`

```
{
  "timestamp": 1735512323231,
  "price": 3521.20
}
```

Used by Market Listener for fallback.

---

# **6. Validation Rules**

(From PRD & SRS & LLD)

### Strategy validations:

* symbol required
* buy_time < sell_time
* stop_loss > 0
* quantity > 0
* must not create overlapping strategies for same symbol/user (optional)

### Broker validations:

* API key, secret, access_token required
* backend must validate via broker API

### Auth validations:

* Password ≥ 6 chars
* Email valid

---

# **7. Example Strategy Lifecycle in Schema Terms**

### 1. User creates strategy

→ Insert row in **strategies table**

### 2. User presses START

→ strategy:{id} created in Redis
→ runtime:{id} initialized
→ symbol:{symbol}:strategies updated
→ Scheduler jobs registered

### 3. Price listener receives ticks

→ checks runtime:{id}.stop_loss

### 4. At trigger

→ event pushed into queue:orders
→ Execution Engine pops event
→ Places order
→ Logs DB entry
→ Updates runtime:{id}

### 5. At STOP

→ Redis keys cleared
→ Strategy status updated in DB

---

# **8. Future Extensions (Schema-Ready)**

Already aligned with PRD future roadmap:

| Feature             | Schema Required?               |
| ------------------- | ------------------------------ |
| Multi-strategy      | YES (strategy_groups table)    |
| Multiple stocks     | YES (strategy_symbols table)   |
| P&L Analytics       | YES (positions, trades tables) |
| Notifications       | YES (notifications table)      |
| Auto-refresh tokens | YES (token_refresh_log table)  |

---

# ✔ SCHEMA.md IS COMPLETE

If you want next:

### ✅ WORKFLOW-SCHEMA.md

### ✅ Complete Prisma Model

### ✅ PostgreSQL migration scripts

### ✅ Redis key visual diagram

### ✅ Auto-generate folder structure + shell script

### ✅ System Architecture PNG

