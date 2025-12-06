# 📘 **API-SCHEMA.md**

### Master Specification for All REST Endpoints (MVP)

Base URL

```
/api/v1
```

All requests/responses are **JSON**.
Authentication uses **JWT**.



---

# **1. AUTHENTICATION API**

---

## **1.1 POST /auth/register**

### **Request Schema**

```json
{
  "name": "string",
  "email": "string",
  "password": "string"
}
```

### Validation

* name: required
* email: valid email
* password: min 6 chars


### **Response**

```json
{
  "user_id": "uuid",
  "message": "Registration successful"
}
```

---

## **1.2 POST /auth/login**

### **Request Schema**

```json
{
  "email": "string",
  "password": "string"
}
```

### **Response**

```json
{
  "access_token": "jwt-token",
  "user_id": "uuid"
}
```

---

# **2. BROKER INTEGRATION API**

**PRD Section 6 — Broker Integration:**
- Validate API tokens
- Save API Key / Secret / Access Token
- Support order placement downstream


---

## **2.1 POST /broker/connect**

### **Request Schema**

```json
{
  "api_key": "string",
  "api_secret": "string",
  "access_token": "string"
}
```

### Validation Rules

* api_key: required
* api_secret: required
* access_token: required
* Backend must validate using broker API


### **Response**

```json
{
  "status": "success",
  "message": "Broker credentials validated and saved"
}
```

### **Error Example**

```json
{
  "status": "error",
  "message": "Invalid broker token"
}
```

---

# **3. STRATEGY MANAGEMENT API**

**PRD:** User sets symbol, buy time, sell time, stop-loss, quantity.

**Backend must:**
- Validate → Save DB → Load Redis → Trigger execution


---

## **3.1 POST /strategy/create**

### **Request Schema**

```json
{
  "symbol": "string",
  "buy_time": "HH:MM:SS",
  "sell_time": "HH:MM:SS",
  "stop_loss": 1540.25,
  "quantity": 10
}
```

### Validation Rules

* symbol: required
* buy_time < sell_time
* stop_loss: required
* quantity > 0
* Stop-loss is mandatory (PRD Safety rule)


### **Response**

```json
{
  "strategy_id": "uuid",
  "message": "Strategy created successfully"
}
```

---

## **3.2 POST /strategy/start**

### **Request Schema**

```json
{
  "strategy_id": "uuid"
}
```

### Response

```json
{
  "status": "running",
  "message": "Strategy started and loaded into Redis"
}
```

Backend Action:

* Fetch from DB
* Create Redis keys
* Register timers for buy/sell
* Add symbol subscription

Conforms with SDD Strategy Manager.


---

## **3.3 POST /strategy/stop**

### Request

```json
{
  "strategy_id": "uuid"
}
```

### Response

```json
{
  "status": "stopped",
  "message": "Strategy stopped and removed from execution"
}
```

Backend removes:

* Redis keys
* Timers
* Symbol mapping

Matches PRD Stop strategy requirement.


---

## **3.4 GET /strategy/status/{strategy_id}**

### Response Schema

```json
{
  "strategy_id": "uuid",
  "status": "running | stopped",
  "position": "none | bought | sold | exited_by_sl",
  "last_action": "BUY | SELL | STOPLOSS | NONE",
  "last_price": 1542.10,
  "timestamp": "ISO-8601"
}
```

Matches PRD Basic Feedback requirement.


---

# **4. ORDER EVENTS (Internal API Used by Execution Engine)**

Not exposed to the mobile app.

---

## **4.1 /internal/order/buy**

```json
{
  "strategy_id": "uuid",
  "symbol": "INFY",
  "quantity": 10,
  "trigger": "TIME",
  "timestamp": "ISO-8601"
}
```

---

## **4.2 /internal/order/sell**

```json
{
  "strategy_id": "uuid",
  "symbol": "INFY",
  "quantity": 10,
  "trigger": "TIME | STOPLOSS",
  "timestamp": "ISO-8601"
}
```

Matches execution engine responsibilities in SDD.


---

# **5. ERROR RESPONSE SCHEMA**

All APIs follow a unified error schema:

```json
{
  "status": "error",
  "error_code": "INVALID_INPUT | BROKER_ERROR | STRATEGY_NOT_FOUND | AUTH_FAILED",
  "message": "string"
}
```

PRD requires full transparency of failures (Logging & Monitoring section).


---

# **6. AUTHENTICATION FORMAT (JWT)**

Every secured endpoint must include:

```
Authorization: Bearer <token>
```

Token contains:

* user_id
* issued_at
* expiry timestamp

Security requirement from SRS.


---

# **7. FULL OPENAPI-LIKE SUMMARY**

---

## **Endpoints**

| Method | Endpoint              | Description                     |
| ------ | --------------------- | ------------------------------- |
| POST   | /auth/register        | Register user                   |
| POST   | /auth/login           | Login user                      |
| POST   | /broker/connect       | Save + validate broker API keys |
| POST   | /strategy/create      | Create strategy                 |
| POST   | /strategy/start       | Start strategy execution        |
| POST   | /strategy/stop        | Stop strategy                   |
| GET    | /strategy/status/{id} | Status view                     |

Matches DOCUMENT PACK API Contract.


---

# **8. FULL DATA MODELS**

---

## **User Model**

```json
{
  "user_id": "uuid",
  "name": "string",
  "email": "string"
}
```

---

## **BrokerCredentials Model**

```json
{
  "api_key": "string",
  "api_secret": "string",
  "access_token": "string"
}
```

---

## **Strategy Model**

```json
{
  "strategy_id": "uuid",
  "symbol": "string",
  "buy_time": "HH:MM:SS",
  "sell_time": "HH:MM:SS",
  "stop_loss": "float",
  "quantity": "int"
}
```

---

# ✔ API-SCHEMA.md is complete.

---

# Would you like me to generate next?

1️⃣ **OpenAPI 3.1 YAML file**
2️⃣ **Postman Collection (JSON export)**
3️⃣ **AUTO-GENERATED API DOCS in Markdown**
4️⃣ **API Error Catalog**

