# 📘 **FEATURE-TRACEABILITY-MATRIX.md**

## Algo Trading System – Complete Requirement to Feature Mapping


# **1. Purpose**

This matrix ensures every **Product Requirement (PRD)** is:

* mapped to **functional/non-functional requirement (SRS)**,
* implemented as a **feature**,
* backed by a **backend/frontend component**,
* exposed via **API**,
* verifiable via **test cases**.

This guarantees **full compliance** and **zero missing functionality**.

---

# **2. Traceability Matrix — MASTER TABLE**

---

## **2.1 User Authentication**

| PRD Requirement                        | SRS Requirement         | Feature         | API                                     | Component          | Test Cases                                                                                                      |
| -------------------------------------- | ----------------------- | --------------- | --------------------------------------- | ------------------ | --------------------------------------------------------------------------------------------------------------- |
| Users must register & login (PRD 4.1)  | SRS 3.1 Authentication  | Register, Login | POST /auth/register<br>POST /auth/login | Auth Service<br>DB | TC-AUTH-01 Register success<br>TC-AUTH-02 Login success<br>TC-AUTH-03 Invalid password<br>TC-AUTH-04 JWT expiry |

---

## **2.2 Broker API Key Setup**

| PRD Requirement                               | SRS Requirement       | Feature                        | API                  | Component                           | Test Cases                                                                    |
| --------------------------------------------- | --------------------- | ------------------------------ | -------------------- | ----------------------------------- | ----------------------------------------------------------------------------- |
| User enters API key, secret, token (PRD 4.1)  | SRS 3.2 Broker Setup  | Broker connection & validation | POST /broker/connect | Broker Connector<br>Secrets Manager | TC-BRKR-01 Valid API key<br>TC-BRKR-02 Invalid key<br>TC-BRKR-03 Token expiry |

---

## **2.3 Strategy Creation**

| PRD Requirement                                           | SRS Requirement              | Feature                            | API                   | Component              | Test Cases                                                                                  |
| --------------------------------------------------------- | ---------------------------- | ---------------------------------- | --------------------- | ---------------------- | ------------------------------------------------------------------------------------------- |
| User sets Buy Time, Sell Time, SL, Qty, Symbol (PRD 4.1)  | SRS 3.3 Strategy Management  | Strategy form + backend validation | POST /strategy/create | Strategy Service<br>DB | TC-STR-01 Create strategy<br>TC-STR-02 Mandatory stop-loss<br>TC-STR-03 Invalid time inputs |

---

## **2.4 Strategy Start / Stop**

| PRD Requirement                       | SRS Requirement              | Feature                    | API                                         | Component                 | Test Cases                                                   |
| ------------------------------------- | ---------------------------- | -------------------------- | ------------------------------------------- | ------------------------- | ------------------------------------------------------------ |
| User starts/stops strategy (PRD 4.1)  | SRS 3.3 Start/Stop Strategy  | Start/Stop runtime control | POST /strategy/start<br>POST /strategy/stop | Strategy Manager<br>Redis | TC-STR-START-01 Start success<br>TC-STR-STOP-01 Stop success |

---

## **2.5 Time-Based Execution (BUY/SELL)**

| PRD Requirement                           | SRS Requirement                                | Feature         | API                                     | Component                       | Test Cases                                                                                     |
| ----------------------------------------- | ---------------------------------------------- | --------------- | --------------------------------------- | ------------------------------- | ---------------------------------------------------------------------------------------------- |
| Execute BUY/SELL at exact time (PRD 5.1)  | SRS 3.4 Execution Engine – time-based trigger  | Scheduler tasks | Internal (Scheduler → Execution Engine) | APScheduler<br>Execution Engine | TC-SCH-01 BUY at exact time<br>TC-SCH-02 SELL at exact time<br>TC-SCH-03 Missed timer recovery |

---

## **2.6 Event-Based Execution (Stop-Loss Trigger)**

| PRD Requirement                       | SRS Requirement            | Feature                                  | API                             | Component                           | Test Cases                                                                                |
| ------------------------------------- | -------------------------- | ---------------------------------------- | ------------------------------- | ----------------------------------- | ----------------------------------------------------------------------------------------- |
| SL triggers immediate exit (PRD 5.1)  | SRS 3.4 Stop-loss trigger  | Real-time price monitoring & SL executor | WebSocket price feed (internal) | Market Listener<br>Execution Engine | TC-SL-01 SL hit executes SELL<br>TC-SL-02 No delay > 5ms<br>TC-SL-03 SL cannot be skipped |

---

## **2.7 Multi-Tenant Isolation**

| PRD Requirement                          | SRS Requirement               | Feature                  | API | Component                 | Test Cases                                                       |
| ---------------------------------------- | ----------------------------- | ------------------------ | --- | ------------------------- | ---------------------------------------------------------------- |
| User A must not affect User B (PRD 5.1)  | SRS 3.5 Multi-Tenant Support  | Tenant-scoped Redis keys | N/A | Redis<br>Strategy Manager | TC-MT-01 Separate runtimes<br>TC-MT-02 No cross-user data access |

---

## **2.8 Dynamic Strategy Updates**

| PRD Requirement                                            | SRS Requirement                                 | Feature                      | API                            | Component                 | Test Cases                                                                                 |
| ---------------------------------------------------------- | ----------------------------------------------- | ---------------------------- | ------------------------------ | ------------------------- | ------------------------------------------------------------------------------------------ |
| User must update SL, time, quantity dynamically (PRD 5.1)  | SRS 3.3 updates must apply instantly via Redis  | Edit strategy during runtime | POST /strategy/update (future) | Strategy Manager<br>Redis | TC-UPD-01 Update SL<br>TC-UPD-02 Update time<br>TC-UPD-03 Redis reflects changes instantly |

---

## **2.9 Broker Integration (Order Placement)**

| PRD Requirement                                | SRS Requirement           | Feature               | API                                      | Component        | Test Cases                                                                    |
| ---------------------------------------------- | ------------------------- | --------------------- | ---------------------------------------- | ---------------- | ----------------------------------------------------------------------------- |
| BUY/SELL order placement via broker (PRD 5.1)  | SRS 3.4 Broker API calls  | Place BUY/SELL orders | Internal (Execution Engine → Broker API) | Broker Connector | TC-ORD-01 BUY success<br>TC-ORD-02 SELL success<br>TC-ORD-03 Retry on failure |

---

## **2.10 Safety Requirements**

| PRD Requirement                                     | SRS Requirement                 | Feature                                 | API | Component                              | Test Cases                                                                                                        |
| --------------------------------------------------- | ------------------------------- | --------------------------------------- | --- | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Mandatory SL, retry mechanism (PRD 5.1 & 7 Safety)  | SRS 3.4 execution safety rules  | SL required, max qty limit, retry logic | N/A | Strategy Validator<br>Execution Engine | TC-SAFE-01 Reject strategy w/o SL<br>TC-SAFE-02 Retry order 3 times<br>TC-SAFE-03 Lock prevents duplicated orders |

---

## **2.11 Performance Requirements**

| PRD Requirement                   | SRS Requirement                         | Feature            | API | Component                 | Test Cases                                                      |
| --------------------------------- | --------------------------------------- | ------------------ | --- | ------------------------- | --------------------------------------------------------------- |
| Execution < 100–300 ms (PRD 6.1)  | SRS 4.1 performance rules (Redis <1ms)  | High-speed runtime | N/A | Redis<br>Execution Engine | TC-PERF-01 Measure BUY latency<br>TC-PERF-02 SL trigger latency |

---

## **2.12 Scalability**

| PRD Requirement                                | SRS Requirement                                | Feature            | API | Component                | Test Cases                           |
| ---------------------------------------------- | ---------------------------------------------- | ------------------ | --- | ------------------------ | ------------------------------------ |
| Must support 500+ active strategies (PRD 6.3)  | SRS 4.3 scalability rules (stateless backend)  | Horizontal scaling | N/A | ECS/EKS<br>Redis Cluster | TC-SCALE-01 Load test 500 strategies |

---

## **2.13 Security**

| PRD Requirement                | SRS Requirement                | Feature                  | API           | Component                     | Test Cases                                                                          |
| ------------------------------ | ------------------------------ | ------------------------ | ------------- | ----------------------------- | ----------------------------------------------------------------------------------- |
| AES-256, HTTPS, JWT (PRD 6.4)  | SRS 4.2 Security Requirements  | Encryption, secure comms | All endpoints | Secrets Manager<br>Auth Layer | TC-SEC-01 AES encryption works<br>TC-SEC-02 Reject HTTP<br>TC-SEC-03 JWT validation |

---

## **2.14 Logging & Monitoring**

| PRD Requirement                                  | SRS Requirement               | Feature                 | API | Component                    | Test Cases                                                |
| ------------------------------------------------ | ----------------------------- | ----------------------- | --- | ---------------------------- | --------------------------------------------------------- |
| Log all orders; CloudWatch monitoring (PRD 6.5)  | SRS 4.5 Logging Requirements  | Order logs, system logs | N/A | CloudWatch<br>Logger Service | TC-LOG-01 Order logged<br>TC-LOG-02 Crash alert generated |

---

## **2.15 Mobile App Simplicity (UI Requirements)**

| PRD Requirement                        | SRS Requirement                           | Feature                         | API | Component  | Test Cases                                                    |
| -------------------------------------- | ----------------------------------------- | ------------------------------- | --- | ---------- | ------------------------------------------------------------- |
| UI must be extremely simple (PRD 4.1)  | SRS 2.2 User Characteristics (simple UI)  | Minimal screens, minimal fields | All | Mobile App | TC-UI-01 Strategy form usability<br>TC-UI-02 App flow < 1 min |

---

# **3. Reverse Traceability (Feature → Requirement)**

This ensures **no feature exists without purpose**.

| Feature             | Mapped PRD Requirement |
| ------------------- | ---------------------- |
| Register/Login      | PRD 4.1                |
| Broker Connect      | PRD 4.1                |
| Strategy Create     | PRD 4.1                |
| Start/Stop Strategy | PRD 4.1                |
| BUY Scheduler       | PRD 5.1                |
| SELL Scheduler      | PRD 5.1                |
| SL Engine           | PRD 5.1                |
| Redis Runtime       | PRD 5.1, 6.1           |
| Multi-Tenant Keys   | PRD 5.1                |
| Retry Logic         | PRD 7                  |
| Logging & Alerts    | PRD 6.5                |

---

# **4. Coverage Summary**

| Domain                      | Coverage        |
| --------------------------- | --------------- |
| Functional Requirements     | **100% mapped** |
| Non-Functional Requirements | **100% mapped** |
| APIs                        | **100% mapped** |
| Runtime Components          | **100% mapped** |
| Safety                      | **100% mapped** |
| Mobile UI                   | **100% mapped** |

No requirement is left without a feature, and no feature exists without a reason.

---

# ✔ **FEATURE-TRACEABILITY-MATRIX.md is complete.**

Would you like:

### 📌 TEST-CASE-DOCUMENT.md

### 📌 QA-EXECUTION-MATRIX.md

### 📌 EXPORT TO EXCEL (.xlsx)

### 📌 TRACEABILITY DIAGRAM (PNG)

