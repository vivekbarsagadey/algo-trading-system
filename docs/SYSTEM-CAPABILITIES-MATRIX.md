# 📘 **SYSTEM-CAPABILITIES-MATRIX.md**

### Algo Trading System – Capability-to-Component Mapping

---

# **1. Purpose**

This matrix defines:

* **What the system must be capable of**
* **Which features satisfy each capability**
* **Which components implement them**
* **Which requirements must be met**
* **Which constraints apply**

This creates a single source of truth joining:

**Product → Engineering → Runtime Execution → Infrastructure**

---

# **2. Capability Matrix (Top Level)**

| Capability Category    | Capability | Description                             | Source (PRD/SRS)                           |
| ---------------------- | ---------- | --------------------------------------- | ------------------------------------------ |
| User Management        | C1         | Register, Login, Session                | PRD Section 4.1 (Login)                    |
| Broker Integration     | C2         | Validate & store API key/secret/token   | PRD Section 4.1 (Broker API Setup)         |
| Strategy Definition    | C3         | Create simple strategy with buy/sell/SL | PRD Strategy Creation Screen (fields)      |
| Strategy Execution     | C4         | Automate BUY/SELL at exact times        | PRD Section 5.1 (Time-Based Execution)     |
| Event-Based Execution  | C5         | Trigger STOPLOSS via price feed         | PRD Section 5.1 (Event-Based Execution)    |
| State Management       | C6         | Maintain runtime state in Redis         | PRD Section 7 (Architecture – Redis Role)  |
| Multi-Tenant Isolation | C7         | Ensure user A never affects user B      | PRD Section 5.1 (Isolation)                |
| Safety                 | C8         | Mandatory SL, retries, fallbacks        | PRD Section 5.1 + Safety requirements      |
| Performance            | C9         | Execute under 300 ms                    | PRD Section 6.1 (Performance)              |
| Scalability            | C10        | Support 500+ parallel strategies        | PRD Section 6.3 (Scalability)              |
| Availability           | C11        | 99% uptime, restart-safe                | PRD Section 6.2 (Availability)             |
| Security               | C12        | AES-256, HTTPS, JWT                     | PRD Section 6.4 (Security)                 |
| Observability          | C13        | Logs, alerts, monitoring                | PRD Section 6.5 (Logging & Monitoring)     |

---

# **3. Capability → Feature Matrix**

| Capability                    | Feature(s) that implement it                                              |
| ----------------------------- | ------------------------------------------------------------------------- |
| **C1 User Management**        | Register, Login, JWT storage, Session handling                            |
| **C2 Broker Setup**           | API key/secret/token validation, secure storage, Zerodha verification     |
| **C3 Strategy Definition**    | Strategy form (symbol/buy/sell/SL/qty), backend validation                |
| **C4 Time-Based Execution**   | APScheduler BUY job, APScheduler SELL job                                 |
| **C5 Event-Based Execution**  | Market Listener WebSocket, SL price comparator                            |
| **C6 State Management**       | Redis runtime keys, strategy keys, symbol mapping                         |
| **C7 Multi-Tenant Isolation** | Namespace-per-strategy keys, per-user db isolation                        |
| **C8 Safety**                 | Mandatory SL validation, retries, lock-state, crash-stop                  |
| **C9 Performance**            | Redis microsecond lookups, async FastAPI, optimized scheduler             |
| **C10 Scalability**           | Stateless backend containers, Redis cluster, horizontal scaling (ECS/EKS) |
| **C11 Availability**          | Auto-restart, container health checks, RDS + Redis HA                     |
| **C12 Security**              | AES encrypted broker keys, HTTPS, JWT                                     |
| **C13 Observability**         | CloudWatch logs, alerts, database logs, Redis monitoring                  |

---

# **4. Capability → Component Matrix**

| Capability                   | Component(s) Responsible                               |
| ---------------------------- | ------------------------------------------------------ |
| **C1 User Management**       | Auth Service, Mobile App                               |
| **C2 Broker Integration**    | Broker Connector, Mobile App (inputs), Secrets Manager |
| **C3 Strategy Definition**   | Strategy Service, Mobile App                           |
| **C4 Time-Based Execution**  | Scheduler (APScheduler), Execution Engine              |
| **C5 Event-Based Execution** | Market Listener, Execution Engine                      |
| **C6 State Management**      | Redis, Strategy Manager                                |
| **C7 Isolation**             | Redis Key Design, DB FK rules, Execution Locks         |
| **C8 Safety**                | Execution Engine, Retry Handler, SL comparator         |
| **C9 Performance**           | Redis, Async IO in FastAPI, optimized tick handler     |
| **C10 Scalability**          | ECS/EKS, Load Balancer, Redis Cluster                  |
| **C11 Availability**         | ECS health checks, Auto-restart, RDS Multi-AZ          |
| **C12 Security**             | Secrets Manager, HTTPS, AES-256 engine                 |
| **C13 Observability**        | CloudWatch, ELB logs, API logging layer                |

---

# **5. Capability → Requirement Matrix (Functional)**

| Capability | Functional Requirements Fulfilled                 |
| ---------- | ------------------------------------------------- |
| **C1**     | SRS 3.1 User Authentication                       |
| **C2**     | SRS 3.2 Broker Setup, validation                  |
| **C3**     | SRS 3.3 Strategy Management                       |
| **C4**     | SRS 3.4 Execution Engine – BUY/SELL triggers      |
| **C5**     | SRS 3.4 Execution Engine – SL execution           |
| **C6**     | Strategy Manager & Redis schema storage           |
| **C7**     | SRS 3.5 Multi-Tenant Support                      |
| **C8**     | PRD Safety Rules: Mandatory SL, retries           |
| **C9**     | SRS 4.1 Performance (<300 ms)                     |
| **C10**    | SRS 4.3 Scalability via containers/Redis cluster  |
| **C11**    | SRS 4.4 Availability (99%)                        |
| **C12**    | SRS 4.2 Security (AES, JWT, HTTPS)                |
| **C13**    | SRS 4.5 Logging (order logs, API logs)            |

---

# **6. Capability → Non-Functional Matrix (Constraints)**

| Capability | Non-Functional Constraints                                 |
| ---------- | ---------------------------------------------------------- |
| **C1**     | JWT expiry rules, credential hashing                       |
| **C2**     | AES-256, secure secrets storage                            |
| **C3**     | Mobile UI simplicity (PRD goal: extremely simple)          |
| **C4**     | BUY/SELL must execute within defined latency (<300 ms)     |
| **C5**     | SL comparison must be real-time (<5 ms tick handler)       |
| **C6**     | Redis operations must be <1ms (SRS 4.1)                    |
| **C7**     | No cross-strategy Redis key overlap                        |
| **C8**     | Mandatory stop-loss; retry 3x before fail-stop             |
| **C9**     | System must support 500+ concurrent strategies             |
| **C10**    | Stateless scaling, container-based deployment              |
| **C11**    | Automatic restart, worker crash handling                   |
| **C12**    | All channels HTTPS; access token masked in logs            |
| **C13**    | CloudWatch logs, alerts for API failures, strategy crashes |

---

# **7. Capability → Data Layer Mapping**

| Capability | DB Involvement       | Redis Involvement                      |
| ---------- | -------------------- | -------------------------------------- |
| **C1**     | users table          | none                                   |
| **C2**     | broker_keys table    | optional caching                       |
| **C3**     | strategies table     | none                                   |
| **C4**     | order_logs table     | queue:orders, runtime:{id}             |
| **C5**     | order_logs           | runtime:{id}, price feed               |
| **C6**     | none                 | strategy:{id}, symbol:{sym}:strategies |
| **C7**     | user_id FK isolation | per-strategy keys                      |
| **C8**     | logs                 | lock_state keys                        |
| **C9**     | none                 | microsecond-level reads                |
| **C10**    | persistent storage   | ephemeral runtime                      |
| **C11**    | durable history      | volatile state recreated               |
| **C12**    | encrypted columns    | no sensitive data stored               |
| **C13**    | logs, errors         | none                                   |

---

# **8. Capability → API Mapping**

| Capability | APIs Used                                  |
| ---------- | ------------------------------------------ |
| **C1**     | POST /auth/register, POST /auth/login      |
| **C2**     | POST /broker/connect                       |
| **C3**     | POST /strategy/create                      |
| **C4**     | POST /strategy/start, GET /strategy/status |
| **C5**     | internal SL trigger → Execution Engine     |
| **C6**     | Redis internal API                         |
| **C7**     | Scoped queries / scoped Redis keys         |
| **C8**     | All execution engine routes                |
| **C9–C13** | No public APIs (internal runtime services) |

---

# **9. Capability → Infrastructure Mapping**

| Capability | Infra Component                        |
| ---------- | -------------------------------------- |
| **C1**     | FastAPI + RDS                          |
| **C2**     | Secrets Manager + RDS                  |
| **C3**     | FastAPI + RDS                          |
| **C4**     | Scheduler, ECS worker nodes            |
| **C5**     | Market Listener, WebSocket connections |
| **C6**     | Redis (ElastiCache)                    |
| **C7**     | Network namespace & IAM separation     |
| **C8**     | Autoscaling, retry queues              |
| **C9**     | Load Balancer, Autoscaling Group       |
| **C10**    | ECS/EKS                                |
| **C11**    | Multi-AZ RDS, Redis HA                 |
| **C12**    | Certificate Manager, HTTPS             |
| **C13**    | CloudWatch Logs, Metrics, Alarms       |

---

# **10. Capability Maturity Ranking (MVP Level)**

| Capability | Maturity            | Notes                                    |
| ---------- | ------------------- | ---------------------------------------- |
| C1         | ✓ Fully implemented | Simple flows                             |
| C2         | ✓ Fully implemented | Broker validation required               |
| C3         | ✓ Fully implemented | Minimal inputs                           |
| C4         | ✓ Fully implemented | Exact timers                             |
| C5         | ✓ Fully implemented | SL triggers instantly                    |
| C6         | ✓ Fully implemented | Redis runtime stable                     |
| C7         | ✓ Fully implemented | Per-user isolation strong                |
| C8         | ✓ Fully implemented | Mandatory SL + retries                   |
| C9         | ✓ Meets MVP         | Can handle 500+ strategies               |
| C10        | ✓ Meets MVP         | ECS/EKS-ready                            |
| C11        | ✓ Meets MVP         | Auto-restart but no failover cluster yet |
| C12        | ✓ Meets MVP         | Strong encryption                        |
| C13        | ✓ Meets MVP         | Logs present; dashboards optional        |

---

# ✔ SYSTEM-CAPABILITIES-MATRIX.md is complete.

Would you like:

### ✅ SYSTEM-CAPABILITIES-DIAGRAM.png

### ✅ ARCHITECTURE-CAPABILITY-MAP.md

### ✅ QA-TEST-CASE-MATRIX.md

### ✅ FEATURE-TRACEABILITY-MATRIX.md

### ✅ EXPORT TO EXCEL / CSV

