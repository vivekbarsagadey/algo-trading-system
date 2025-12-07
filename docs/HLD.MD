# 📘 **High-Level Design (HLD)**

### **Algo Trading System – High-Speed, Multi-Tenant Automated Trading Platform**

---

# **1. System Overview**

The Algo Trading System consists of:

1. **Mobile App (React Native / Expo)** – Primary mobile interface for traders
2. **Admin Web Application (Next.js 15)** – Comprehensive web interface with role-based access
3. **Backend REST API (FastAPI)** – Core business logic and API layer
4. **Execution Engine (Python microservice)** – High-speed order execution
5. **Scheduler Service (Time-based triggers)** – Cron-based task scheduler
6. **Market Listener (WebSocket price feed)** – Real-time price monitoring
7. **Redis (In-memory execution runtime)** – High-speed state management
8. **PostgreSQL (persistent storage)** – Durable data storage
9. **Broker Integration Layer** – Multi-broker API wrappers (Zerodha, Dhan, Fyers, Angel One)
10. **AWS Infrastructure** – Cloud infrastructure (ECS/EKS, ElastiCache, RDS, CloudWatch)

The system executes BUY/SELL/SL orders with microsecond-level Redis access and minimal latency while providing dual access modes: mobile-first experience and comprehensive web administration.

---

# **2. High-Level Architecture Diagram (Text Form)**

(If you want, I will generate a **PNG version**.)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLIENT INTERFACES                                   │
│                                                                             │
│  ┌────────────────────────┐          ┌───────────────────────────────────┐ │
│  │   Mobile App            │          │   Admin Web App (Next.js 15)      │ │
│  │   (React Native)        │          │   - User Dashboard (Role: User)   │ │
│  │                         │          │   - Admin Panel (Role: Admin)     │ │
│  │  - Strategy Creation    │          │   - System Monitor                │ │
│  │  - Broker Setup         │          │   - User Management               │ │
│  │  - Real-time Status     │          │   - Playground/Testing            │ │
│  └───────────┬─────────────┘          └────────────────┬──────────────────┘ │
└──────────────┼──────────────────────────────────────────┼───────────────────┘
               │                                           │
               │ HTTPS/REST                    HTTPS/REST │
               │ JWT Auth                      JWT Auth + │
               │                               Role-Based  │
               └────────────────┬──────────────┘           │
                                │                          │
                                ▼                          ▼
              ┌─────────────────────────────────────────────────────────┐
              │              FastAPI Backend (API Gateway)               │
              │                                                          │
              │  ┌────────────┐  ┌────────────┐  ┌──────────────────┐  │
              │  │ Auth API   │  │Strategy API│  │ Admin API         │  │
              │  │ (JWT)      │  │            │  │ (Role Protected)  │  │
              │  └────────────┘  └────────────┘  └──────────────────┘  │
              │                                                          │
              │  ┌──────────────────────────────────────────────────┐   │
              │  │        Proxy Middleware                          │   │
              │  │  - Role validation (Admin/User/Broker)           │   │
              │  │  - Request authentication                        │   │
              │  │  - CORS handling                                 │   │
              │  └──────────────────────────────────────────────────┘   │
              └───────────────────────┬──────────────────────────────────┘
                                      │
          ┌───────────────────────────┴───────────────────────────┐
          │                                                       │
          ▼                                                       ▼
┌──────────────────────┐                           ┌──────────────────────┐
│  Strategy Manager    │                           │  Broker Connector    │
│  - Validation        │                           │  - Zerodha Wrapper   │
│  - State Management  │                           │  - Dhan Wrapper      │
│  - Lifecycle Control │                           │  - Fyers Wrapper     │
└──────────┬───────────┘                           └────────────┬─────────┘
           │                                                     │
           ▼                                                     ▼
    ┌────────────────┐                                ┌──────────────────────┐
    │  Redis Cache   │◄──────────────────────────────►│  Execution Engine    │
    │  (Runtime      │                                │  (Order Placement)   │
    │   State)       │                                │  - Buy Orders        │
    │                │                                │  - Sell Orders       │
    │ - Active       │                                │  - Stop-Loss         │
    │   Strategies   │                                │  - Retry Logic       │
    │ - Market Data  │                                └──────────────────────┘
    │ - User         │
    │   Sessions     │
    └────────┬───────┘
             │
     ┌───────┴────────┐
     │                │
     ▼                ▼
┌──────────┐   ┌──────────────────────┐
│Scheduler │   │  Market Listener      │
│  Service │   │  (WebSocket Feed)     │
│  - Cron  │   │  - Price Updates      │
│  - Timer │   │  - SL Monitoring      │
└──────────┘   └──────────────────────┘
     │                │
     └───────┬────────┘
             ▼
   ┌──────────────────────┐
   │  PostgreSQL (RDS)     │
   │  - Users (with roles) │
   │  - Strategies         │
   │  - Broker Creds       │
   │  - Execution Logs     │
   │  - System Config      │
   └──────────────────────┘
```

---

# **2.1 Role-Based Access Architecture**

### **Authentication & Authorization Flow**

```text
User Request (Mobile/Web)
     │
     ▼
┌─────────────────────┐
│  Next.js Proxy      │  ← For web requests
│  or JWT Middleware  │  ← For mobile requests
└─────────┬───────────┘
          │
          ▼
     Extract JWT
          │
          ▼
┌─────────────────────┐
│  Validate Token     │
│  & Extract Role     │
└─────────┬───────────┘
          │
          ├─→ Role: Admin  → Full Access (All Endpoints)
          ├─→ Role: User   → Limited Access (Own Data)
          └─→ Role: Broker → Broker-Specific Data
```

### **Role Permission Matrix**

| Endpoint Pattern | Admin | User | Broker | Guest |
|------------------|-------|------|--------|-------|
| `/auth/*` | ✅ | ✅ | ✅ | ✅ |
| `/strategy/create` | ✅ | ✅ | ❌ | ❌ |
| `/strategy/list` | ✅ (all) | ✅ (own) | ❌ | ❌ |
| `/admin/users` | ✅ | ❌ | ❌ | ❌ |
| `/admin/system` | ✅ | ❌ | ❌ | ❌ |
| `/broker/stats` | ✅ | ❌ | ✅ (own) | ❌ |
| `/playground/*` | ✅ | ✅ | ❌ | ❌ |

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

# **3.1.1 Admin Web Application (Next.js 15)**

### **Responsibilities**

* Role-based user interface (Admin/User/Broker)
* Server-side rendering for optimal performance
* Real-time strategy monitoring
* User management (Admin only)
* System health dashboard
* Strategy playground/testing
* Comprehensive analytics

### **Technology Stack**

* **Framework**: Next.js 15 with App Router
* **Authentication**: NextAuth.js v5 + JWT
* **UI Components**: Shadcn/ui + Tailwind CSS
* **State Management**: React Server Components + Zustand (client state)
* **Forms**: React Hook Form + Zod validation
* **Charts**: Recharts for analytics
* **Real-time**: Server-Sent Events (SSE)

### **Application Structure**

```text
admin-web/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx           # Login page
│   │   └── register/
│   │       └── page.tsx           # Registration
│   ├── (dashboard)/
│   │   ├── layout.tsx             # Authenticated layout with sidebar
│   │   ├── dashboard/
│   │   │   └── page.tsx           # User dashboard
│   │   ├── strategies/
│   │   │   ├── page.tsx           # Strategy list
│   │   │   ├── create/
│   │   │   │   └── page.tsx       # Create strategy
│   │   │   └── [id]/
│   │   │       └── page.tsx       # Strategy details
│   │   ├── brokers/
│   │   │   └── page.tsx           # Broker connection
│   │   ├── playground/
│   │   │   └── page.tsx           # Strategy testing
│   │   └── profile/
│   │       └── page.tsx           # User profile
│   ├── (admin)/
│   │   ├── admin/
│   │   │   ├── users/
│   │   │   │   └── page.tsx       # User management
│   │   │   ├── strategies/
│   │   │   │   └── page.tsx       # All strategies
│   │   │   ├── system/
│   │   │   │   └── page.tsx       # System monitoring
│   │   │   └── analytics/
│   │   │       └── page.tsx       # Platform analytics
│   ├── api/
│   │   ├── auth/
│   │   │   └── [...nextauth]/
│   │   │       └── route.ts       # NextAuth config
│   │   ├── strategies/
│   │   │   └── route.ts           # Strategy API proxy
│   │   └── admin/
│   │       └── route.ts           # Admin API proxy
│   ├── proxy.ts                   # Auth middleware
│   └── layout.tsx                 # Root layout
├── components/
│   ├── auth/
│   │   └── LoginForm.tsx
│   ├── dashboard/
│   │   ├── StrategyCard.tsx
│   │   ├── StatusMonitor.tsx
│   │   └── QuickActions.tsx
│   ├── admin/
│   │   ├── UserTable.tsx
│   │   ├── SystemMetrics.tsx
│   │   └── StrategyOverview.tsx
│   └── ui/                        # Shadcn components
├── lib/
│   ├── auth.ts                    # Auth utilities
│   ├── api.ts                     # API client
│   └── utils.ts                   # Helper functions
└── styles/
    └── globals.css
```

### **Key Modules**

#### **Authentication Module**

```typescript
// lib/auth.ts
export async function getCurrentUser() {
  const session = await getServerSession(authOptions)
  if (!session) return null
  
  return {
    id: session.user.id,
    email: session.user.email,
    role: session.user.role, // Admin | User | Broker
  }
}

export function requireRole(role: string[]) {
  return async function middleware(req) {
    const user = await getCurrentUser()
    if (!user || !role.includes(user.role)) {
      throw new Error('Unauthorized')
    }
    return user
  }
}
```

#### **Proxy Middleware**

```typescript
// proxy.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function proxy(request: NextRequest) {
  const token = request.cookies.get('next-auth.session-token')
  
  // Public routes
  if (request.nextUrl.pathname.startsWith('/login')) {
    return NextResponse.next()
  }
  
  // Protected routes require authentication
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  
  // Role-based route protection
  const user = await getUserFromToken(token)
  
  // Admin-only routes
  if (request.nextUrl.pathname.startsWith('/admin')) {
    if (user.role !== 'Admin') {
      return NextResponse.redirect(new URL('/dashboard', request.url))
    }
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
```

#### **API Integration**

```typescript
// lib/api.ts
class ApiClient {
  private baseUrl: string
  
  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL!
  }
  
  async request(endpoint: string, options: RequestInit = {}) {
    const token = await getToken()
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers,
      },
    })
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }
    
    return response.json()
  }
  
  // Strategy endpoints
  async getStrategies() {
    return this.request('/strategies')
  }
  
  async createStrategy(data: StrategyCreate) {
    return this.request('/strategies', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }
  
  // Admin endpoints (Admin role required)
  async getAllUsers() {
    return this.request('/admin/users')
  }
  
  async getSystemMetrics() {
    return this.request('/admin/system/metrics')
  }
}

export const api = new ApiClient()
```

### **Features by Role**

#### **Admin Role Features**

* User Management
  * View all users
  * Create/Edit/Delete users
  * Assign roles
  * Suspend/Activate accounts
* System Monitoring
  * Real-time metrics dashboard
  * Order execution logs
  * Error tracking
  * Performance analytics
* Strategy Oversight
  * View all strategies
  * Monitor execution status
  * Force stop strategies (emergency)
* Configuration Management
  * System settings
  * Broker configurations
  * Feature flags

#### **User Role Features**

* Strategy Management
  * Create/Edit strategies
  * Start/Stop own strategies
  * View execution history
* Broker Integration
  * Connect broker accounts
  * Manage API credentials
  * View connection status
* Dashboard
  * Personal analytics
  * Performance metrics
  * P&L tracking
* Playground
  * Test strategies with simulated data
  * Backtest historical performance

#### **Broker Role Features**

* Integration Monitoring
  * View strategies using their broker API
  * Monitor API health
  * Track order success rates
* Analytics
  * Order volume statistics
  * Integration performance

### **Real-Time Updates Implementation**

```typescript
// Server-Sent Events for real-time strategy updates
// app/api/strategies/[id]/stream/route.ts
export async function GET(req: Request, { params }: { params: { id: string } }) {
  const encoder = new TextEncoder()
  
  const stream = new ReadableStream({
    async start(controller) {
      // Subscribe to Redis pub/sub for strategy updates
      const redis = await getRedisClient()
      const subscriber = redis.duplicate()
      
      await subscriber.subscribe(`strategy:${params.id}:updates`, (message) => {
        const data = `data: ${JSON.stringify(message)}\n\n`
        controller.enqueue(encoder.encode(data))
      })
      
      // Keep connection alive
      const keepAlive = setInterval(() => {
        controller.enqueue(encoder.encode(': keepalive\n\n'))
      }, 30000)
      
      req.signal.addEventListener('abort', () => {
        clearInterval(keepAlive)
        subscriber.unsubscribe()
        controller.close()
      })
    },
  })
  
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  })
}
```

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

