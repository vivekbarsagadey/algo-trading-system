# 📘 **SCHEMA.md**

### Master Schema Definition for DB, Redis, Event Pipeline & API Contract



# **1. DATABASE SCHEMA (PostgreSQL/MySQL)**

Database stores persistent metadata only — not runtime state.
PRD Section 7 describes DB roles: user info, broker keys, strategy copy.


---

## **1.1 `users` Table**

| Field         | Type           | Description            |
| ------------- | -------------- | ---------------------- |
| id            | UUID (PK)      | Unique user identifier |
| name          | VARCHAR        | Full name              |
| email         | VARCHAR UNIQUE | Login identifier       |
| password_hash | VARCHAR        | Encrypted password     |
| created_at    | TIMESTAMP      | Registration timestamp |
| updated_at    | TIMESTAMP      | Last update            |

PRD Requirement: Register/login + secure password storage.


---

## **1.2 `broker_credentials` Table**

| Field        | Type                     | Description      |
| ------------ | ------------------------ | ---------------- |
| user_id      | UUID FK → users.id       | Owner            |
| api_key      | TEXT (AES-256 encrypted) | Zerodha API key  |
| api_secret   | TEXT (AES-256 encrypted) | Secret key       |
| access_token | TEXT (AES-256 encrypted) | Session token    |
| is_valid     | BOOLEAN                  | Whether verified |
| created_at   | TIMESTAMP                | Time of entry    |
| updated_at   | TIMESTAMP                | Time of update   |

PRD Requirement: API key, secret, token must be stored & validated.


---

## **1.3 `strategies` Table**

| Field      | Type                          | Description         |
| ---------- | ----------------------------- | ------------------- |
| id         | UUID PK                       | Strategy ID         |
| user_id    | UUID FK → users.id            | Owner               |
| symbol     | VARCHAR                       | Stock symbol        |
| buy_time   | TIME                          | Scheduled buy time  |
| sell_time  | TIME                          | Scheduled sell time |
| stop_loss  | FLOAT                         | Mandatory stop-loss |
| quantity   | INT                           | Order size          |
| status     | ENUM: created/running/stopped | Current lifecycle   |
| created_at | TIMESTAMP                     | Creation            |
| updated_at | TIMESTAMP                     | Last update         |

Matches PRD strategy fields exactly.


---

## **1.4 `order_logs` Table**

| Field            | Type                                    |
| ---------------- | --------------------------------------- |
| id               | UUID                                    |
| strategy_id      | UUID                                    |
| event_type       | ENUM: BUY, SELL, STOPLOSS, RETRY, ABORT |
| request_payload  | JSON                                    |
| response_payload | JSON                                    |
| status           | success / failed                        |
| created_at       | TIMESTAMP                               |

Matches PRD logging requirement (CloudWatch/RDS mirror).


---

---

# **2. REDIS SCHEMA (Runtime Execution Layer)**

Defined in DOCUMENT PACK Redis Key Structure.


Redis holds **all real-time execution state** for <1 ms latency.

---

## **2.1 `strategy:{strategyId}` (Static Strategy Config)**

```json
{
  "strategy_id": "uuid",
  "user_id": "uuid",
  "symbol": "INFY",
  "buy_time": "09:30:00",
  "sell_time": "15:30:00",
  "stop_loss": 1540.25,
  "quantity": 10,
  "status": "running"
}
```

Loaded from DB → Redis when strategy STARTS.
(PRD Section 5.1 Strategy Management)


---

## **2.2 `runtime:{strategyId}` (Dynamic Live State)**

```json
{
  "position": "none | bought | sold | exited_by_sl",
  "last_price": 1545.20,
  "last_buy_order": "orderId123",
  "last_sell_order": "orderId456",
  "lock_state": "free | locked",
  "updated_at": "timestamp"
}
```

Required by execution engine (SRS Section 3.4).


---

## **2.3 `symbol:{symbol}:strategies`**

Set of strategy IDs subscribed to the symbol.

Example:

```
symbol:INFY:strategies = {1, 5, 7, 12}
```

Used by market listener to check SL.

---

## **2.4 `price:{symbol}`**

```
1541.85
```

Latest market price per symbol.

---

## **2.5 `queue:orders`**

Internal event queue consumed by Execution Engine.

Sample entry:

```json
{
  "event_type": "BUY",
  "strategy_id": "uuid",
  "timestamp": "2025-02-25T09:30:00Z"
}
```

Events stored:

* BUY
* SELL
* STOPLOSS
* RETRY
* SAFETY_ABORT

Matches SDD Execution Engine design.


---

## **2.6 `lock_state:{strategyId}`**

Prevents duplicate BUY/SELL/STOPLOSS executions.

```
"locked"
```

---

---

# **3. EVENT SCHEMA (Pipeline Normalized Format)**

Matches SRS & Execution Engine design.


Unified event object:

```json
{
  "event_type": "BUY | SELL | STOPLOSS | RETRY | ABORT",
  "strategy_id": "uuid",
  "attempt": 1,
  "price": 1520.75,
  "trigger_time": "2025-02-25T09:30:00Z",
  "metadata": {}
}
```

---

### **BUY Event Schema**

```json
{
  "event_type": "BUY",
  "strategy_id": "uuid",
  "trigger_time": "09:30:00"
}
```

---

### **SELL Event Schema**

```json
{
  "event_type": "SELL",
  "strategy_id": "uuid",
  "trigger_time": "15:30:00"
}
```

---

### **STOPLOSS Event Schema**

```json
{
  "event_type": "STOPLOSS",
  "strategy_id": "uuid",
  "trigger_price": 1520.25
}
```

Generated when price feed crosses SL.

Matches PRD SL requirement.


---

---

# **4. API PAYLOAD SCHEMA**

Matches DOCUMENT PACK API Contract.


---

# **4.1 Register**

```json
{
  "email": "user@example.com",
  "password": "string",
  "name": "John Doe"
}
```

---

# **4.2 Login**

```json
{
  "email": "user@example.com",
  "password": "string"
}
```

---

# **4.3 Broker Connect**

```json
{
  "api_key": "string",
  "api_secret": "string",
  "access_token": "string"
}
```

Matches PRD Section 4.1 Broker API Key Setup.


---

# **4.4 Create Strategy**

```json
{
  "symbol": "INFY",
  "buy_time": "09:30:00",
  "sell_time": "15:30:00",
  "stop_loss": 1540.25,
  "quantity": 10
}
```

Exactly matches PRD Strategy Inputs.


---

# **4.5 Start Strategy**

```json
{
  "strategy_id": "uuid"
}
```

---

# **4.6 Stop Strategy**

```json
{
  "strategy_id": "uuid"
}
```

---

# **4.7 Status Response**

```json
{
  "status": "running | stopped",
  "position": "none | bought | sold | exited_by_sl",
  "last_action": "BUY | SELL | STOPLOSS",
  "last_price": 1541.10,
  "timestamp": "2025-02-25T12:15:33Z"
}
```

Matches PRD requirement for simple UI feedback.


---

---

# **5. Broker Order Schema**

```json
{
  "symbol": "INFY",
  "quantity": 10,
  "transaction_type": "BUY | SELL",
  "order_type": "MARKET",
  "trigger_price": null
}
```

---

# **6. Strategy Lifecycle Schema**

```json
{
  "status": "created | running | stopped | exited | failed",
  "started_at": "timestamp",
  "stopped_at": "timestamp"
}
```

---

# ✔ SCHEMA.md is complete

This is the final master schema for the entire system.

---

### Would you like me to generate any of these next?

1. **REDIS-SCHEMA.md** (full deep-dive version)
2. **API-SCHEMA.md** (OpenAPI + JSON schemas)
3. **STRATEGY-RUNTIME-SCHEMA.md**
4. **BROKER-ORDER-SCHEMA.md**
5. **DB-MIGRATIONS.sql**

