
# 📘 **FOLDER-STRUCTURE.md**

### Master Folder Layout for Algo Trading System (Backend + Mobile + Infra + Docs)

This is the **canonical layout** for developers, DevOps, QA, and architects.

---

# **1. Root Directory**

```
algo-trading-system/
│
├── backend/
├── mobile-app/
├── infra/
├── docs/
├── scripts/
└── tests/
```

Each layer maps to PRD architecture:
✔ Mobile App → FastAPI Backend → Execution Engine → Redis → Broker → DB → AWS Infrastructure


---

# **2. Backend Folder Structure (FastAPI + Python)**

Backend implements:
✔ Auth Service
✔ Strategy Manager
✔ Scheduler
✔ Market Listener
✔ Execution Engine
✔ Broker Connector
✔ Redis State Manager
As defined in PRD & SRS



```
backend/
│
├── app/
│   ├── main.py
│   ├── config/
│   │   ├── settings.py
│   │   └── secrets_manager.py
│   │
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── broker.py
│   │   │   ├── strategy.py
│   │   │   └── status.py
│   │   └── dependencies.py
│   │
│   ├── core/
│   │   ├── scheduler/
│   │   │   ├── apscheduler_engine.py
│   │   │   ├── buy_trigger.py
│   │   │   └── sell_trigger.py
│   │   │
│   │   ├── market_listener/
│   │   │   ├── ws_listener.py
│   │   │   └── price_feed_handler.py
│   │   │
│   │   ├── execution_engine/
│   │   │   ├── engine.py
│   │   │   ├── handlers/
│   │   │   │   ├── buy_handler.py
│   │   │   │   ├── sell_handler.py
│   │   │   │   └── stoploss_handler.py
│   │   │   └── retry_manager.py
│   │   │
│   │   ├── broker_connector/
│   │   │   ├── zerodha_client.py
│   │   │   └── broker_interface.py
│   │   │
│   │   ├── strategy_manager/
│   │   │   ├── loader.py
│   │   │   ├── validator.py
│   │   │   └── updater.py
│   │   │
│   │   ├── redis/
│   │   │   ├── redis_client.py
│   │   │   ├── redis_keys.py
│   │   │   └── redis_runtime.py
│   │   │
│   │   └── logging/
│   │       ├── logger.py
│   │       └── event_logger.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── strategy.py
│   │   │   └── logs.py
│   │   └── repositories/
│   │       ├── user_repo.py
│   │       ├── strategy_repo.py
│   │       └── log_repo.py
│   │
│   ├── utils/
│   │   ├── time_utils.py
│   │   ├── crypto_utils.py
│   │   ├── constants.py
│   │   └── validators.py
│   │
│   └── workers/
│       ├── task_consumer.py
│       └── task_producer.py
│
├── requirements.txt
└── Dockerfile
```

### Why this structure?

Because the PRD defines **clear separation of services**:
✔ Scheduler
✔ Market Listener
✔ Execution Engine
✔ Broker Connector
✔ Strategy Management


---

# **3. Redis Key Schema Folder**

```
backend/app/redis/schema/
│
├── strategy_schema.json
├── runtime_schema.json
├── event_schema.json
└── redis_indexing.md
```

Matches DOCUMENT PACK Redis key structure:


---

# **4. Mobile App Folder Structure (React Native or Flutter)**

Based on PRD mobile requirements:
✔ Register/Login
✔ Broker API Key
✔ Create Strategy
✔ Start/Stop Strategy


```
mobile-app/
│
├── src/
│   ├── screens/
│   │   ├── LoginScreen.tsx
│   │   ├── RegisterScreen.tsx
│   │   ├── BrokerConnectScreen.tsx
│   │   ├── CreateStrategyScreen.tsx
│   │   └── StrategyControlScreen.tsx
│   │
│   ├── components/
│   │   ├── InputField.tsx
│   │   ├── TimePicker.tsx
│   │   └── Button.tsx
│   │
│   ├── api/
│   │   ├── auth_api.ts
│   │   ├── broker_api.ts
│   │   └── strategy_api.ts
│   │
│   ├── context/
│   │   └── user_context.ts
│   │
│   ├── utils/
│   │   └── validators.ts
│   │
│   └── theme/
│       ├── colors.ts
│       └── typography.ts
│
├── App.tsx
└── package.json
```

---

# **5. Infrastructure Folder (AWS + Docker + Deployment)**

Matches PRD infra requirements: ECS/EKS + RDS + Redis + CloudWatch.


```
infra/
│
├── docker/
│   ├── backend.Dockerfile
│   └── mobile.Dockerfile
│
├── aws/
│   ├── ecs/
│   │   ├── task_definition.json
│   │   ├── service.json
│   │   └── cluster.json
│   │
│   ├── rds/
│   │   ├── schema.sql
│   │   └── parameter_group.json
│   │
│   ├── redis/
│   │   └── elasticache_config.json
│   │
│   └── cloudwatch/
│       ├── alerts.json
│       └── log_groups.json
│
└── ci-cd/
    ├── github_actions.yml
    └── buildspec.yml
```

---

# **6. Testing Folder**

```
tests/
│
├── unit/
├── integration/
├── load/
└── mocks/
```

---

# **7. Scripts Folder**

```
scripts/
│
├── init_db.py
├── seed_data.py
├── start_scheduler.py
└── start_market_listener.py
```

---

# **8. Documentation Folder**

Includes all documents you asked for:

```
docs/
│
├── SRS.md
├── HLD.md
├── LLD.md
├── WORKFLOW-SCHEMA.md
├── EXECUTION-ENGINE-PROCESSING.md
├── EVENT-PROCESSING-PIPELINE.md
├── SYSTEM-STATE-MACHINE.md
├── PIPELINE-FLOW.md
├── FULL-SEQUENCE-DIAGRAM.md
├── FRONTEND-SPEC.md
├── BACKEND-SPEC.md
└── REDIS-SCHEMA.md
```

---

# **9. Event Queue + Worker Folder**

```
backend/app/workers/
│
├── task_producer.py    # Scheduler + Market Listener
├── task_consumer.py    # Execution Engine
└── retry_manager.py
```

Matches SRS requirement for high-speed event processing.


---

# **10. Strategy Isolation Folder**

```
backend/app/strategy_manager/
│
├── loader.py
├── validator.py
└── updater.py
```

Matches PRD requirement for **multi-tenant isolation**.


---

# ✔ Final Notes

This folder structure:

* Matches PRD architecture 100%
* Follows DOCUMENT PACK SRS + SDD exactly
* Clean separation of responsibilities
* Perfect for scalable FastAPI microservice
* Production-ready (ECS/EKS + Redis + RDS)
* Ready for developer onboarding

