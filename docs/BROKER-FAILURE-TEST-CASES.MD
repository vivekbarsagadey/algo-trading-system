# 📘 **broker-failure-test-cases.md**

### Complete Failure & Recovery Test Suite for Broker Integration

---

# **1. Purpose**

This document outlines all **failure scenarios** involving:

* Broker API downtime
* Expired/invalid tokens
* Failed BUY/SELL orders
* WebSocket disconnect
* Price feed instability
* Partial order fills
* Network-level failures
* Internal backend-to-broker failures

Matching PRD requirement:

> “Backend must have a retry mechanism for order failures and log all attempts.”
>

And SRS requirement:

> “Execution Engine must log all orders, handle failures gracefully, and retry.”
>

---

# **2. Broker Failure Test Case Categories**

1. **Authentication & Token Failures**
2. **BUY Order Failures**
3. **SELL Order Failures**
4. **STOP-LOSS Execution Failures**
5. **WebSocket Feed Failures (Price Stream)**
6. **Network/Transport Failures**
7. **Order Status Check Failures**
8. **High Latency / Performance Failures**
9. **Multi-Tenant Safety Failures**
10. **Logging & Monitoring Failures**

---

# **3. Detailed Test Cases**

---

# **3.1 Authentication & Token Failures**

### **TC-BF-01: Invalid API Token**

| Field               | Value                                                            |
| ------------------- | ---------------------------------------------------------------- |
| **Objective**       | System detects invalid token and rejects strategy start          |
| **Setup**           | User submits invalid access token                                |
| **Steps**           | POST /broker/connect                                             |
| **Expected Result** | “Invalid token” → Do not save keys → Do not allow strategy start |
| **Pass Criteria**   | No Redis keys created, API returns error                         |

---

### **TC-BF-02: Expired Token**

| Field        | Value                                                                       |
| ------------ | --------------------------------------------------------------------------- |
| Failure Type | Broker token expiration                                                     |
| Expected     | Backend detects expired token, notifies user                                |
| Recovery     | User must re-enter token manually (PRD requirement: no auto-refresh in MVP) |

---

### **TC-BF-03: Broker Authentication Server Down**

| Expected | Retry 3 times → Fail with system message |
| Logging | Logged in CloudWatch per PRD Logging requirement |


---

# **3.2 BUY Order Failure Cases**

### **TC-BF-10: BUY Order Timeout**

| Field            | Value                                      |
| ---------------- | ------------------------------------------ |
| Failure          | Broker does not respond to BUY order       |
| Expected         | Retry BUY 3 times (PRD Safety Requirement) |
| After Failure    | Strategy marked as `buy_failed`            |
| No Duplicate BUY | Redis lock must prevent repeated BUY       |

---

### **TC-BF-11: BUY Rejected by Broker**

Examples:

* Insufficient margin
* Market closed
* Invalid symbol

| Expected Results                        |
| --------------------------------------- |
| Reject BUY attempt                      |
| Log error                               |
| Update runtime: position = “buy_failed” |
| SELL/SL must not trigger                |

---

### **TC-BF-12: Duplicate BUY Prevention**

| Expected | Only one BUY order even if duplicate events pushed |
| Reason | Redis lock_state prevents duplicates |

---

# **3.3 SELL Order Failure Cases**

### **TC-BF-20: SELL Order Timeout**

| Expected | Retry 3 times |
| After retries fail | Strategy marked `sell_failed` |
| User notified | “SELL order failed. Manual intervention required.” |

---

### **TC-BF-21: SELL Rejected by Broker**

| Expected | Log + strategy moves to STOPPED |
| Safety | No further events allowed after SELL failure |

---

### **TC-BF-22: SELL Triggered Twice**

| Expected | Only 1 SELL order should execute |
| Protection | Redis lock prevents double execution |

---

# **3.4 STOP-LOSS Failure Cases**

### **TC-BF-30: SL SELL Timeout**

| Condition | SL hit but SELL fails due to network/broker timeout |
| Expected | Retry 3 times |
| Fallback | Strategy marked as `sl_failed` |
| Logging | Mandatory error-level logging (PRD Logging requirement) |


---

### **TC-BF-31: SL Trigger While BUY Not Executed**

| Expected | Ignore SL event, because runtime.position != “bought” |
| Outcome | No false stop-loss |

---

### **TC-BF-32: SL Trigger but Broker API Down**

| Expected |

* Retry 3 times
* Fail safely
* Strategy marked EXITED_BY_SL_FAILED |

| Safety Note | MUST NOT attempt any BUY again |

---

# **3.5 WebSocket (Price Feed) Failure Cases**

### **TC-BF-40: Price Stream Disconnect**

| Failure | WebSocket drops connection |
| Expected | MarketListener auto-reconnect every 2 seconds |
| During Downtime | No SL decisions allowed |
| Logging | Warning-level logs |

---

### **TC-BF-41: Delayed Price Updates**

| Expected |

* For delays > 2 seconds → log error
* Do NOT trigger SL based on stale price |

---

### **TC-BF-42: Incorrect Price Format**

| Expected | Reject tick and ignore |
| Logging | Error-level |

---

# **3.6 Network & Transport Layer Failures**

### **TC-BF-50: Backend Cannot Reach Broker**

| Expected |

* Retry
* Log error
* Mark order as failed |

### **TC-BF-51: DNS Resolution Failure**

| Expected |

* Logged
* Strategy paused automatically |

---

### **TC-BF-52: High Latency Network (>300ms)**

Per PRD Performance Requirement


| Expected |

* System logs latency violation
* Does not block next operations |

---

# **3.7 Order Status Polling Failures (if implemented)**

### **TC-BF-60: Order Status API Timeout**

| Expected | Retry 3 times |

---

### **TC-BF-61: Status Mismatch**

When broker status != internal state.

| Expected |

* Update runtime
* Log discrepancy |

---

# **3.8 Performance Failures**

From PRD 6.1 Performance Requirements

and SRS 4.1 Performance Constraints


### **TC-BF-70: BUY execution delay > 300ms**

| Expected |

* Log performance alert
* Strategy must continue normally |

### **TC-BF-71: SL trigger delay > 5ms**

| Expected |

* SL must still execute immediately
* Warning logged |

---

# **3.9 Multi-Tenant Safety Failures**

### **TC-BF-80: Strategy A’s SELL incorrectly affecting Strategy B**

| Expected | Hard fail – isolation must be preserved |
| Verification | Redis key namespaces |

---

### **TC-BF-81: Broker API rate-limit shared across users**

| Expected | Each user isolated; bulk operations throttled safely |
| Outcome | No user should bypass another’s execution |

---

# **3.10 Logging & Monitoring Failures**

From PRD 6.5 Logging & Monitoring

and SRS 4.5 Logging


### **TC-BF-90: Order Failure Not Logged**

| Expected | Must fail QA immediately |

### **TC-BF-91: Crash Without Alert**

| Expected | CloudWatch alert must trigger |

---

# **4. Summary Table of All Failure Scenarios**

| Scenario Category       | No. of Test Cases |
| ----------------------- | ----------------- |
| Authentication failures | 3                 |
| BUY failures            | 3                 |
| SELL failures           | 3                 |
| STOP-LOSS failures      | 3                 |
| WebSocket failures      | 3                 |
| Network failures        | 3                 |
| Status polling failures | 2                 |
| Performance failures    | 2                 |
| Multi-tenant failures   | 2                 |
| Logging failures        | 2                 |
| **Total**               | **26 Test Cases** |

---

# ✔ broker-failure-test-cases.md is complete.

I can now generate:

### 🔹 broker-integration-test-suite.xlsx

### 🔹 execution-engine-failure-modes.md

### 🔹 redis-failure-test-cases.md

### 🔹 price-feed-failure-test-cases.md

### 🔹 high-availability-test-plan.md

