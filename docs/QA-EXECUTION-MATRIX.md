# 📘 **QA-EXECUTION-MATRIX.md**

### Algo Trading System – Full QA Coverage Matrix


# **1. Purpose**

This document ensures:

* Each PRD & SRS requirement is testable
* Each feature has test scenarios
* Execution results can be tracked
* QA covers functional + non-functional + recovery + safety

---

# **2. MASTER QA EXECUTION MATRIX**

---

# **2.1 User Authentication**

| Test ID | Requirement Reference        | Test Case Description | Steps                    | Expected Output        | Pass Criteria     |
| ------- | ---------------------------- | --------------------- | ------------------------ | ---------------------- | ----------------- |
| AUTH-01 | PRD 4.1 Login, SRS 3.1 | Valid login           | Enter email/pass → Login | JWT returned           | Home screen loads |
| AUTH-02 | Same                         | Invalid password      | Enter wrong pass         | Error message          | No login          |
| AUTH-03 | Same                         | Empty fields          | Leave fields blank       | Field validation       | Buttons disabled  |
| AUTH-04 | Same                         | Token expiry handling | Wait for JWT expiry      | App redirects to login | No crashes        |

---

# **2.2 Broker API Key Setup**

| Test ID | Requirement Reference               | Description        | Steps                        | Expected                   | Pass Criteria                 |
| ------- | ----------------------------------- | ------------------ | ---------------------------- | -------------------------- | ----------------------------- |
| BRK-01  | PRD 4.1 Broker Setup, SRS 3.2 | Valid API key      | Enter valid key/secret/token | "Connected" success        | Backend validates with broker |
| BRK-02  | Same                                | Invalid API key    | Enter wrong key              | Error: invalid credentials | No save to DB                 |
| BRK-03  | Same                                | Empty fields       | Submit empty                 | Validation error           | Cannot proceed                |
| BRK-04  | SRS 4.2 Security                    | API key encryption | Check DB storage             | Encrypted keys             | No plaintext storage          |

---

# **2.3 Strategy Creation**

| Test ID | Requirement Reference              | Description           | Steps                | Expected           | Pass Criteria           |
| ------- | ---------------------------------- | --------------------- | -------------------- | ------------------ | ----------------------- |
| STR-01  | PRD Strategy Screen, SRS 3.3 | Create valid strategy | Fill all fields      | Strategy saved     | strategy_id returned    |
| STR-02  | Same                               | Stop-loss missing     | Leave SL empty       | Error: SL required | Block strategy creation |
| STR-03  | Same                               | Invalid buy/sell time | buy_time > sell_time | Validation error   | No save                 |
| STR-04  | Same                               | Large quantity        | Enter > max limit    | Error message      | Quantity capped         |
| STR-05  | Same                               | Incorrect symbol      | Enter invalid        | Validation fails   | No save                 |

---

# **2.4 Strategy Start / Stop**

| ID          | Requirement Reference | Description       | Steps              | Expected                  | Pass Criteria      |
| ----------- | --------------------- | ----------------- | ------------------ | ------------------------- | ------------------ |
| ST-START-01 | PRD 4.1 Start/Stop | Start strategy    | Tap START          | Strategy moves to RUNNING | Redis keys created |
| ST-START-02 | Same                  | Start twice       | Press twice        | Second attempt ignored    | No duplication     |
| ST-STOP-01  | Same                  | Stop strategy     | Press STOP         | Strategy becomes STOPPED  | Redis keys removed |
| ST-STOP-02  | Same                  | Stop after SL hit | Auto-stop after SL | UI shows STOPPED          | No timers remain   |

---

# **2.5 Time-Based BUY Execution**

| ID     | Requirement Reference                 | Description                  | Steps                           | Expected             | Pass Criteria    |
| ------ | ------------------------------------- | ---------------------------- | ------------------------------- | -------------------- | ---------------- |
| BUY-01 | PRD 5.1 Time Execution, SRS 3.4 | BUY at exact time            | Set buy_time 1 min ahead        | BUY executed at time | Delay < 300 ms   |
| BUY-02 | Same                                  | Timer recovery after restart | Restart backend before buy_time | BUY still triggers   | No missed orders |
| BUY-03 | Same                                  | Redis lock test              | Trigger simultaneous events     | One BUY only         | No duplication   |

---

# **2.6 Time-Based SELL Execution**

| ID      | Description        | Steps                  | Expected          | Pass Criteria           |
| ------- | ------------------ | ---------------------- | ----------------- | ----------------------- |
| SELL-01 | SELL at exact time | Set sell_time upcoming | SELL executed     | Delay < 300 ms          |
| SELL-02 | SELL after BUY     | Verify system flow     | SELL logged       | Orders in correct order |
| SELL-03 | Timer persistence  | Restart backend        | SELL still occurs | Scheduler restored      |

---

# **2.7 Stop-Loss (Event-Based Execution)**

| ID    | Requirement Reference        | Description                | Steps                          | Expected                 | Pass Criteria      |
| ----- | ---------------------------- | -------------------------- | ------------------------------ | ------------------------ | ------------------ |
| SL-01 | PRD Stop-Loss, SRS 3.4 | SL triggers immediate exit | Send tick <= SL                | SELL executed instantly  | < 5 ms trigger     |
| SL-02 | Same                         | SL processed only once     | Trigger multiple ticks         | Only one exit            | No repeated orders |
| SL-03 | Same                         | SL priority over SELL      | Price hits SL before sell_time | SL executes, ignore SELL | Correct precedence |

---

# **2.8 Multi-Tenant Isolation**

| ID    | Requirement Reference           | Description          | Steps                        | Expected          | Pass Criteria        |
| ----- | ------------------------------- | -------------------- | ---------------------------- | ----------------- | -------------------- |
| MT-01 | PRD Multi-Tenant, SRS 3.5 | Separate Redis state | Start strategies for 2 users | No cross keys     | No shared runtime    |
| MT-02 | Same                            | Load testing         | Run 100 users                | No leakage        | All independent      |
| MT-03 | Same                            | Cross-user STOP      | User A stops strategy        | User B unaffected | Isolation maintained |

---

# **2.9 Execution Engine (Order Placement)**

| ID     | Requirement               | Description          | Steps             | Expected             | Pass                  |
| ------ | ------------------------- | -------------------- | ----------------- | -------------------- | --------------------- |
| ORD-01 | PRD Broker Integration | BUY order success    | Use mock broker   | BUY returns order_id | Logged                |
| ORD-02 | Same                      | Failure & retry      | Force API failure | Retry 3 times        | Strategy stops safely |
| ORD-03 | Same                      | Duplicate prevention | Queue 2 tasks     | Only 1 processed     | Lock works            |

---

# **2.10 Performance Testing**

| ID      | Requirement Reference              | Test Description           | Expected    | Pass Criteria        |
| ------- | ---------------------------------- | -------------------------- | ----------- | -------------------- |
| PERF-01 | PRD 6.1 Performance, SRS 4.1 | BUY latency                | < 300 ms    | Meets threshold      |
| PERF-02 | Same                               | SL trigger latency         | < 5 ms      | Redis pipeline works |
| PERF-03 | Same                               | 500+ concurrent strategies | All working | No crash             |

---

# **2.11 Security Testing**

| ID     | Requirement Reference           | Description       | Expected      | Pass Criteria     |               |
| ------ | ------------------------------- | ----------------- | ------------- | ----------------- | ------------- |
| SEC-01 | PRD 6.4 Security, SRS 4.2 | Encrypted keys    | Check DB      | AES-256 encrypted | No plaintext  |
| SEC-02 | Same                            | HTTPS enforcement | Call via HTTP | Reject request    | Must fail     |
| SEC-03 | Same                            | JWT validation    | Invalid token | 401               | Secure access |

---

# **2.12 Availability / Recovery**

| ID       | Requirement Reference               | Description          | Expected           | Pass Criteria      |
| -------- | ----------------------------------- | -------------------- | ------------------ | ------------------ |
| AVAIL-01 | PRD 6.2 Availability, SRS 4.4 | Restart backend      | No data loss       | Redis restored     |
| AVAIL-02 | Same                                | Redis reboot         | Scheduler recovers | No missed BUY/SELL |
| AVAIL-03 | Same                                | Network interruption | System retries     | No silent failures |

---

# **2.13 Logging & Monitoring**

| ID     | Requirement Reference          | Description | Expected                  | Pass Criteria          |
| ------ | ------------------------------ | ----------- | ------------------------- | ---------------------- |
| LOG-01 | PRD 6.5 Logging, SRS 4.5 | Order logs  | All orders logged         | Consistent format      |
| LOG-02 | Same                           | Error logs  | Failures recorded         | CloudWatch entry       |
| LOG-03 | Same                           | Alerts      | Strategy crash alert sent | Received in monitoring |

---

# **3. Summary of Coverage**

| Area                | Coverage |
| ------------------- | -------- |
| Authentication      | ✓ 100%   |
| Broker Setup        | ✓ 100%   |
| Strategy Management | ✓ 100%   |
| Execution Engine    | ✓ 100%   |
| SL Engine           | ✓ 100%   |
| Scheduler           | ✓ 100%   |
| Multi-Tenant        | ✓ 100%   |
| Performance         | ✓ 100%   |
| Security            | ✓ 100%   |
| Availability        | ✓ 100%   |
| Logging/Monitoring  | ✓ 100%   |

**No requirement is untested.**

---

# ✔ **QA-EXECUTION-MATRIX.md is complete.**

I can now generate:

### 📌 TEST-CASE-DOCUMENT.md (full test case descriptions)

### 📌 UAT-SCENARIOS.md

### 📌 DEFECT-MANAGEMENT-WORKFLOW.md

### 📌 QA-REPORT-TEMPLATE.md

### 📌 Export to Excel / Google Sheets

