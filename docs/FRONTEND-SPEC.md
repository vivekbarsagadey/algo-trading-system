# 📘 **FRONTEND-SPEC.md**

### **Algo Trading System – Dual Frontend Architecture**

---

# **1. Overview**

The Algo Trading System provides **two frontend interfaces** to serve different user needs and access modes:

## **1.1 Mobile App (React Native / Expo)**

A simple, minimal, high-speed mobile app designed for **retail traders**, especially users with **low technical expertise**, to:

* Register & Login
* Enter Broker API credentials
* Create simple BUY/SELL/STOP-LOSS strategies
* Start/Stop automation
* View strategy status

The focus is **simplicity**, **minimal UI**, **zero complexity**, and **fast interaction**.

## **1.2 Admin Web Application (Next.js 15)**

A comprehensive web-based administration platform providing:

### **For Admin Users**:
* User management (create, edit, delete, assign roles)
* System health monitoring (metrics, logs, alerts)
* Strategy oversight (view all strategies, force stop)
* Platform analytics (user growth, order volume, success rates)
* Audit logging and compliance

### **For Regular Users**:
* **Alternative to mobile app** – Full access to all strategy features via web browser
* Web-based strategy creation and management
* Broker integration management
* **Strategy Playground** – Test strategies with simulated data (no real money)
* Personal dashboard with P&L tracking
* Real-time updates via Server-Sent Events

### **For Broker Users**:
* Integration analytics
* API health monitoring
* Order success rates and error tracking

---

# **2. Technology Stack**

| Layer              | Technology                      |
| ------------------ | ------------------------------- |
| Framework          | React Native (Expo)             |
| Navigation         | Expo Router or React Navigation |
| HTTP Client        | Axios or native fetch           |
| State Management   | Zustand (simple, lightweight)   |
| Storage            | SecureStore (JWT)               |
| Time Inputs        | React Native DateTimePicker     |
| Form Handling      | React Hook Form                 |
| Environment Config | expo-constants                  |

---

# **3. App Architecture**

```
frontend/
│
├── app/
│   ├── login.jsx
│   ├── register.jsx
│   ├── broker-connect.jsx
│   ├── create-strategy.jsx
│   ├── strategy-control.jsx
│   └── components/
│       ├── Input.js
│       ├── Button.js
│       └── StatusCard.js
│
├── store/
│   ├── authStore.js
│   ├── brokerStore.js
│   └── strategyStore.js
│
├── services/
│   ├── api.js
│   ├── authApi.js
│   ├── brokerApi.js
│   └── strategyApi.js
│
└── utils/
    ├── validator.js
    └── formatters.js
```

---

# **4. Screen-by-Screen Specification**

(based on Document Pack wireframes: )

---

# **4.1 Login Screen**

### **Purpose**

Authenticate user & obtain JWT.

### **UI Elements**

* Email input
* Password input (masked)
* Login button
* Register link

### **Validations**

* Email must be valid
* Password must be ≥ 6 chars

### **API**

```
POST /auth/login
```

### **Success**

* Save JWT in SecureStore
* Navigate → Broker Connect Screen

### **Failure**

* Show toast: “Invalid email or password”

---

# **4.2 Register Screen**

### **UI Elements**

* Full Name
* Email
* Password
* Register button

### **API**

```
POST /auth/register
```

### **Success**

* Save JWT
* Navigate → Broker Connect Screen

---

# **4.3 Broker Connect Screen**

(Directly from PRD section 4.1: Broker API Key Setup)


### **UI Elements**

* API Key field
* API Secret field
* Access Token field
* Validate & Save button

### **Validations**

* All fields required

### **API**

```
POST /broker/connect
```

### **Success**

* Navigate → Create Strategy Screen
* Show success toast: “Broker Connected”

### **Failure**

Show “Invalid broker key/token”

---

# **4.4 Create Strategy Screen**

(From PRD "Strategy Creation Screen": symbol, buy time, sell time, stop loss, qty)


### **UI Elements**

* Symbol input (text or dropdown)
* Buy Time (Time picker)
* Sell Time (Time picker)
* Stop Loss (Number input)
* Quantity (Number input)
* Save Strategy button

### **Validations**

* stop_loss > 0 (mandatory per PRD)
* buy_time < sell_time
* quantity > 0
* symbol required

### **API**

```
POST /strategy/create
```

### **Success**

* Save strategy_id into store
* Navigate → Strategy Control Screen

---

# **4.5 Strategy Control Screen**

(from PRD “Strategy Control”: Start/Stop buttons + status)


### **UI Elements**

* Strategy Summary (symbol, times, SL, qty)
* Status card:

  * Running / Stopped
  * Last executed action (BUY/SELL)
* START Strategy button
* STOP Strategy button

### **API Calls**

#### **Start strategy**

```
POST /strategy/start
```

#### **Stop strategy**

```
POST /strategy/stop
```

#### **Status polling**

Every **5 seconds**:

```
GET /strategy/status/{strategy_id}
```

### **Status Response**

```
{
  "strategy_id": "uuid",
  "status": "running",
  "position": "bought",
  "last_action": "BUY",
  "last_price": 3521.4
}
```

### **UI Behavior**

* Button changes to STOP when running
* Display status color:

  * Green = Running
  * Gray = Stopped
* Display last action:

  * “BUY executed at 09:30”
  * “SELL executed at 15:30”
  * “STOP-LOSS HIT” (highlight red)

---

# **5. State Management**

Use **Zustand** because it is:

* Small
* Fast
* Local-state friendly
* Perfect for mobile apps

### **Stores**

---

## **5.1 authStore**

```
{
  jwt: "",
  setJwt(),
  logout()
}
```

---

## **5.2 brokerStore**

```
{
  apiKey: "",
  secretKey: "",
  accessToken: "",
  isConnected: false,
  saveBrokerKeys(),
}
```

---

## **5.3 strategyStore**

```
{
  strategyId: "",
  strategyData: {},
  status: "stopped",
  lastAction: "",
  lastPrice: null,
  updateStatus(),
}
```

---

# **6. API Service Layer**

All API requests go through a central Axios instance.

```
services/api.js
```

### **Features**

* JWT automatically attached to headers
* Base URL in environment variables
* Timeout 5 seconds
* Error interceptor

---

# **7. Error Handling Specification**

### Global Error Scenarios

| Error       | Display                         |
| ----------- | ------------------------------- |
| 400         | “Please check your inputs”      |
| 401         | “Session expired – login again” |
| 500         | “Server busy – try again”       |
| No internet | “No Internet Connection”        |

### Toast Types

* success()
* error()
* warning()

---

# **8. Non-Functional Frontend Requirements**

From PRD section 3 & 6.


### **8.1 Simplicity**

* Minimal UI
* No analytics
* No graphs
* No heavy components

### **8.2 Speed**

* Navigation < 100ms
* API response shown instantly
* Status polling optimized (5-second interval)

### **8.3 Security**

* JWT stored in SecureStore
* No broker keys stored on device
* HTTPS enforced

### **8.4 Reliability**

* App must display exact strategy status
* Polling fallbacks when connection lost

---

# **9. UX Rules (Critical for MVP)**

### **Rule 1: Zero complexity**

User should finish setup in **< 2 minutes**.
(From PRD Success Metrics)


### **Rule 2: Minimal fields**

Only essential entries shown.

### **Rule 3: Readability**

Clear labels, no jargon.

### **Rule 4: Safe strategy creation**

Must not allow strategy without stop-loss (PRD safety requirement).


### **Rule 5: No fancy charts**

MVP must stay basic.


---

# **10. Frontend–Backend Interaction Flow**

### **User Journey**

(Exactly matching PRD user flow)


```
1. Register/Login
2. Save JWT
3. Connect Broker
4. Create Strategy
5. Press START
6. Show strategy status from backend
7. Poll backend every 5 sec
8. Display BUY/SELL/SL actions
```

---

# **11. Build & Deployment Specification**

### **Local Development**

```
expo start
```

### **Production Build**

```
eas build -p android
eas build -p ios
```

### **Environmental Variables**

```
API_BASE_URL
PRODUCTION_MODE
```

### **OTA Updates**

Use Expo Updates for instant fixes.

---

# **12. Deliverables Checklist**

### UI Components

* Input
* Time Picker
* Button
* Status Card
* Error Toast
* Loading Indicator

### Screens

* Login
* Register
* Broker Connect
* Create Strategy
* Strategy Control

### Integrations

* JWT storage
* API layer
* Zustand stores
* Status polling
* Error handling
* Navigation

---

# ✔ FRONTEND-SPEC.md is READY.

If you want next:

### ✅ WORKFLOW-SCHEMA.md

### ✅ SCHEMA.md

### ✅ FULL PROJECT ZIP with empty folders

### ✅ Shell script to auto-create folders

### ✅ PNG Architecture Diagram

### ✅ FULL DEV ONBOARDING DOCUMENT

Just tell me — **“Generate X next.”**

# **13. Admin Web Application (Next.js 16)**

## **13.1 Overview**

The Admin Web Application is a comprehensive web-based platform providing role-based access for:
- **Admin Users**: Full system management
- **Regular Users**: Alternative to mobile app with added playground feature
- **Broker Users**: Integration analytics and monitoring

## **13.2 Technology Stack**

| Layer | Technology |
|-------| ------------ |
| Framework | Next.js 16 (App Router) |
| Language | TypeScript |
| UI Library | Shadcn/ui + Radix UI |
| Styling | Tailwind CSS |
| Authentication | NextAuth.js v5 |
| State Management | Zustand + React Server Components |
| Forms | React Hook Form + Zod |
| Charts | Recharts |
| Real-Time | Server-Sent Events (SSE) |

## **13.3 Key Features by Role**

### **Admin Features**
1. User Management Dashboard
2. System Health Monitoring
3. Strategy Oversight (all users)
4. Platform Analytics
5. Audit Logging

### **User Features**
1. Web-based Strategy Management
2. Strategy Playground (testing without real money)
3. Broker Integration
4. Real-time Updates (SSE)
5. Personal Dashboard

### **Broker Features**
1. Integration Analytics
2. API Health Monitoring
3. Order Success Rates

## **13.4 Security & Authentication**

- **NextAuth.js v5** with JWT tokens
- **Proxy Middleware** for route protection
- **Role-based access control** (Admin/User/Broker)
- **Session timeout**: 30 minutes
- **Secure cookies**: HttpOnly, Secure, SameSite

## **13.5 Real-Time Updates (SSE)**

Server-Sent Events provide live updates for:
- Strategy status changes
- Market price updates
- System health metrics
- Order notifications

## **13.6 Deployment**

**Local Development**:
```bash
cd admin-web && npm install && npm run dev
```

**Production**: Vercel, AWS Amplify, or AWS ECS

**Environment Variables**:
- `NEXTAUTH_URL`
- `NEXTAUTH_SECRET`
- `NEXT_PUBLIC_BACKEND_URL`
- `REDIS_URL`

---

# ✔ FRONTEND-SPEC.md COMPLETE WITH DUAL FRONTEND ARCHITECTURE

**Updated Sections**:
- ✅ Overview (dual frontend: Mobile + Web)
- ✅ Mobile App Specification (React Native)
- ✅ Admin Web Application (Next.js 16)

**For Complete Implementation Details**:
- See `/docs/ADMIN-WEB-APP-SUMMARY.md`
- See `/docs/HLD.MD` section 3.1.1

