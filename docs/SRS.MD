
# 📘 **Software Requirements Specification (SRS)**

### **Algo Trading System – High-Speed, Multi-Tenant Trading Automation**

---

# **1. Introduction**

## **1.1 Purpose**

The purpose of this SRS is to define detailed functional, non-functional, system, integration, and operational requirements for the Algo Trading System.
This system enables retail users to automate simple trading strategies using a mobile app while the backend executes logic with high-speed in-memory computation using Redis.

The SRS is intended for:

* Product owners
* Backend developers (FastAPI, Redis, AWS)
* Mobile developers (React Native / Expo)
* QA testers
* DevOps engineers
* Stakeholders, investors

---

## **1.2 Scope**

The system provides **dual access modes** for flexibility:

### **Mobile App (React Native/Expo)**
Users can:
* Register/login via mobile interface
* Add broker API credentials (e.g., Zerodha, Angel One, Dhan, Fyers)
* Create simple predefined strategies:
  * Buy time
  * Sell time
  * Stop-loss
  * Symbol
  * Quantity
* Start/Stop strategies
* Monitor live price and enforce mandatory stop-loss
* View execution history and analytics

### **Admin Web Application (Next.js 15)**
The system provides a comprehensive web interface with role-based access:

**Admin Users** can:
* Manage all users (create, edit, delete, assign roles)
* Monitor system health and performance
* View and control all strategies across users
* Access platform-wide analytics and reports
* Configure system settings
* View audit logs and system events

**Regular Users** can:
* Access all mobile app features via web browser
* Create and manage strategies through web UI
* Connect broker accounts
* Use strategy playground for testing (simulated data, no real money)
* View personal dashboard and analytics
* Monitor strategy performance in real-time

**Broker Role Users** can:
* View integration analytics
* Monitor API health and performance
* Access broker-specific reporting

### **Backend Ensures**
* Exact execution timing
* Fail-safe order placement
* Independent, isolated multi-tenant strategy execution
* High-speed Redis-based runtime
* Role-based access control and data isolation
* Real-time updates via Server-Sent Events

---

## **1.3 Definitions & Acronyms**

| Term                 | Definition                                                     |
| -------------------- | -------------------------------------------------------------- |
| **Algo Strategy**    | A predefined automation defining buy/sell times and stop-loss. |
| **Broker API**       | Trading broker integration (ex: Zerodha Kite).                 |
| **Execution Engine** | Backend service responsible for placing orders.                |
| **Scheduler**        | Time-based trigger system.                                     |
| **Market Listener**  | Monitors live prices via WebSockets.                           |
| **Redis Runtime**    | In-memory execution state for speed.                           |
| **SL**               | Stop Loss.                                                     |
| **JWT**              | JSON Web Token authentication.                                 |

---

# **2. Overall System Description**

## **2.1 Product Perspective**

The system consists of:

### **Frontend (Mobile App)**

* Built using React Native / Expo
* Minimal UI
* API-driven

### **Backend**

* FastAPI microservices
* Redis (active strategy state)
* PostgreSQL (persistent storage)
* AWS ECS/EKS deployment
* CloudWatch logging

(From PRD & Document Pack:  )

---

## **2.2 User Types**

The system supports multiple user roles with different access levels:

### **Role 1: Admin Users**

* Platform administrators with full system access
* Manage all users (create, edit, delete, assign roles)
* View and control all strategies across the platform
* Monitor system health, performance, and resources
* Access platform-wide analytics and reports
* Configure system settings and parameters
* View audit logs for compliance and security

**Access**: Admin Web Application (Next.js 15)

### **Role 2: Regular Users (Retail Traders)**

* Primary users who create and manage their own strategies
* Access via mobile app OR web application
* Manage broker connections and API credentials
* Create, edit, start, stop strategies
* View personal dashboard and analytics
* Use strategy playground for testing
* Monitor strategy execution in real-time

**Access**: Mobile App (React Native) AND/OR Admin Web Application

### **Role 3: Broker Users**

* Broker integration partners
* View strategies using their broker API
* Monitor API health and integration performance
* Access broker-specific analytics
* View order success rates and error metrics

**Access**: Admin Web Application (limited broker views)

### **Secondary Stakeholders**

* DevOps engineers managing infrastructure
* QA testers verifying functionality
* Backend developers maintaining services

---

## **2.3 Constraints**

* Broker API rate limits
* Mandatory stop-loss for safety
* In-memory execution must be failsafe
* Strategies must run independently (multi-tenant isolation)

---

## **2.4 Assumptions**

* Users will manually generate and enter broker access tokens.
* Internet connectivity is stable during trading sessions.
* Broker APIs are available and functioning.

---

# **3. Functional Requirements**

---

# **3.1 Authentication Module**

### **FR-1: User Registration**

The system shall allow users to register using:

* Email or mobile
* Password

### **FR-2: Password Encryption**

Passwords shall be stored using secure hashing (bcrypt/argon2).

### **FR-3: User Login**

The system shall allow users to log in and receive a JWT token.

### **FR-4: Forgot Password**

The system shall support password reset via email/mobile OTP.

---

# **3.2 Broker Integration Module**

### **FR-5: Add Broker Credentials**

User must submit:

* API Key
* Secret Key
* Access Token

(From PRD: )

### **FR-6: Credential Validation**

Backend shall validate the user’s broker credentials via a test API call.

### **FR-7: Secure Storage**

All keys must be stored encrypted (AES-256).

---

# **3.3 Strategy Management**

### **FR-8: Create Strategy**

User must be able to define:

| Field     | Type     | Mandatory |
| --------- | -------- | --------- |
| Symbol    | string   | Yes       |
| Buy Time  | HH:MM:SS | Yes       |
| Sell Time | HH:MM:SS | Yes       |
| Stop Loss | number   | Yes       |
| Quantity  | integer  | Yes       |

### **FR-9: Strategy Validation**

Backend must reject:

* Invalid times
* Invalid stop-loss
* Missing fields

### **FR-10: Strategy Persistence**

Save a copy of the strategy to DB.

### **FR-11: Load Strategy to Redis**

Once started, the strategy is moved to in-memory runtime.

### **FR-12: Update Strategy**

User may modify:

* Stop-loss
* Times
* Quantity
  Changes must update Redis instantly.

### **FR-13: Start/Stop Strategy**

User can toggle strategy status.

### **FR-14: Strategy Status API**

Return:

* Running / Stopped
* Last action (Buy/Sell/SL triggered)

---

# **3.4 Execution Engine**

### **FR-15: Time-Based Execution**

At Buy Time → place BUY order.
At Sell Time → place SELL order.

### **FR-16: Event-Based Execution**

System must monitor live prices for:

* Stop-loss
* Threshold-based triggers

### **FR-17: Stop-Loss Enforcement**

Stop-loss execution must take priority over any other order.

### **FR-18: Redis Locking**

Each strategy must use Redis lock state to prevent double execution.

### **FR-19: Order Logging**

All order attempts must be logged to DB.

---

# **3.5 Scheduler Module**

### **FR-20: Accurate Time Triggers**

Delay must be <300 ms (from PRD: ).

### **FR-21: Missed Execution Handling**

If time is missed by a short interval, system must execute immediately.

---

# **3.6 Market Listener Module**

### **FR-22: Price Subscription**

Connect to Broker WebSocket feed.

### **FR-23: Real-Time SL Monitoring**

If price <= SL → immediately trigger SELL.

### **FR-24: Error Handling**

If price feed disconnects:

* Attempt reconnection
* Notify backend logs

---

# **3.7 Multi-Tenant System Requirements**

### **FR-25: Strategy Isolation**

User A’s strategy must not interfere with User B’s.

### **FR-26: Redis Namespace Separation**

Each strategy must have unique Redis keys.

### **FR-27: User-Level Resource Limits**

Max quantity per user must be enforced.

---

# **3.8 Safety Requirements**

### **FR-28: Mandatory Stop-Loss**

User cannot create a strategy without an SL.

### **FR-29: Retry on Order Failure**

At least 3 retries before marking failure.

### **FR-30: Fail-Safe Shutdown**

If strategy misbehaves:

* Stop immediately
* Notify logs

---

# **3.9 Admin Web Application Module**

### **FR-31: Role-Based Authentication**

The system shall support three user roles:

* **Admin**: Full system access
* **User**: Own data access + playground
* **Broker**: Broker-specific analytics

Authentication shall use NextAuth.js v5 with JWT tokens containing role claims.

### **FR-32: User Management (Admin Only)**

Admins shall be able to:

* View all registered users in a paginated table
* Create new users with email, password, and role assignment
* Edit existing user details (email, role, status)
* Soft delete users (mark as inactive)
* Search and filter users by role, status, email
* View user activity logs

**Priority**: P0  
**User Story**: US-ADM-001

### **FR-33: System Health Monitoring (Admin Only)**

Admins shall see real-time system metrics:

* Total active users
* Total strategies (active, running, stopped)
* Total orders executed (today, this week, this month)
* System uptime percentage
* Average API response time
* Error rate (last 24 hours)
* Redis memory usage
* Database connection pool status

**Priority**: P0  
**User Story**: US-ADM-002

### **FR-34: Strategy Oversight (Admin Only)**

Admins shall be able to:

* View all strategies across all users
* Filter strategies by user, status, symbol, broker
* View strategy execution logs and order history
* Force stop any running strategy (emergency control)
* View failed orders with error details
* Export strategy data for analysis

**Priority**: P0  
**User Story**: US-ADM-003

### **FR-35: Platform Analytics (Admin Only)**

Admins shall access analytics dashboard showing:

* User growth over time (chart)
* Order volume trends (daily, weekly, monthly)
* Most traded symbols
* Broker usage distribution
* Success rate by broker
* Average P&L per user
* Top performing strategies

**Priority**: P1  
**User Story**: US-ADM-004

### **FR-36: Audit Logging (Admin Only)**

The system shall log all admin actions:

* User created/edited/deleted
* Strategy force-stopped
* System configuration changed
* Role assignments modified

Logs shall include:

* Admin user ID
* Action type
* Target entity (user ID, strategy ID)
* Timestamp
* IP address
* Details (JSON)

**Priority**: P0  
**User Story**: US-ADM-005

### **FR-37: Web-Based Strategy Management (Users)**

Regular users shall be able to:

* Create strategies using web form interface
* Edit strategy parameters (when not running)
* Start/Stop strategies via web UI
* View strategy execution history
* Monitor real-time strategy status via Server-Sent Events
* Delete strategies (soft delete)

**Priority**: P0  
**User Story**: US-USR-001

### **FR-38: Strategy Playground (Users)**

Users shall access a playground environment where:

* Strategies run with simulated market data
* No real money or broker connection required
* Historical data backtesting supported
* Results show P&L, win rate, execution accuracy
* Playground strategies clearly marked as "TEST"
* Users can copy playground strategies to live mode

**Priority**: P1  
**User Story**: US-USR-002

### **FR-39: Web-Based Broker Integration (Users)**

Users shall be able to:

* Add broker credentials via web form
* Test broker connection before saving
* View broker connection status (connected/disconnected)
* Update broker access tokens
* Remove broker integration

**Priority**: P0  
**User Story**: US-USR-003

### **FR-40: Real-Time Strategy Updates (Users)**

The web application shall provide real-time updates using Server-Sent Events:

* Strategy status changes (WAITING → BOUGHT → SOLD → STOPPED)
* Current market price for active strategies
* Order placement confirmations
* Stop-loss triggers
* Error notifications

**Priority**: P1  
**User Story**: US-USR-004

### **FR-41: Personal Dashboard (Users)**

Users shall see a dashboard with:

* Total strategies (active, running, stopped)
* Today's P&L
* This week's P&L
* Total orders executed
* Success rate (percentage)
* Quick action buttons (Create Strategy, Add Broker)
* Recent activity feed

**Priority**: P0  
**User Story**: US-USR-005

### **FR-42: Broker Analytics (Broker Role)**

Broker users shall see:

* Total strategies using their broker API
* Order volume statistics (daily, weekly, monthly)
* API success rate
* Average response time
* Error distribution by error code
* Top users by order volume

**Priority**: P1  
**User Story**: US-BRK-001

### **FR-43: Proxy Middleware Protection**

All Next.js routes except `/login` and `/register` shall be protected by middleware that:

* Validates JWT token from cookies
* Extracts user role from token
* Redirects unauthenticated users to `/login`
* Blocks unauthorized access to admin routes
* Logs failed authentication attempts

**Priority**: P0  
**User Story**: US-SEC-001

### **FR-44: Responsive UI Design**

The admin web application shall be responsive and work on:

* Desktop (1920x1080, 1440x900)
* Tablet (iPad, 768x1024)
* Mobile (responsive layout, 375x667)

All tables, charts, and forms shall adapt to screen size.

**Priority**: P1  
**User Story**: US-UX-001

---

# **4. Non-Functional Requirements**

---

# **4.1 Performance Requirements**

(from PRD: Execution <300 ms, Redis microseconds — )

| Component                  | Requirement           |
| -------------------------- | --------------------- |
| Order execution delay      | < 300 ms              |
| Redis read/write           | < 1 ms                |
| Price monitoring frequency | real-time (WebSocket) |
| Parallel strategies        | 500+                  |

---

# **4.2 Security Requirements**

### **NFR-1: Encryption**

* AES-256 for broker keys
* TLS 1.2+ for all communication

### **NFR-2: Authentication**

* JWT-based user sessions

### **NFR-3: Access Control**

Users must only access their own strategies.

---

# **4.3 Scalability Requirements**

### **NFR-4: Horizontal Scaling**

Backend must scale via AWS ECS/EKS.

### **NFR-5: Redis Cluster Support**

The system must allow scaling Redis for high load.

### **NFR-6: Stateless Backend**

All stateful components must run inside Redis/DB.

---

# **4.4 Availability Requirements**

### **NFR-7: Uptime**

System uptime target: **99%**.

### **NFR-8: Auto-Restart**

Containers restart after crash automatically.

---

# **4.5 Logging & Monitoring Requirements**

Use AWS CloudWatch for:

* Strategy lifecycle logs
* Stop-loss logs
* API failures
* Order execution logs

Alerts for:

* Strategy crash
* Redis failure
* Broker downtime

---

# **5. External Interface Requirements**

---

# **5.1 Mobile App UI Screens**

(Expanded from wireframes: )

### Screen 1 – Login

* Email, password
* Login button
* Register link

### Screen 2 – Register

* Name, email, password

### Screen 3 – Connect Broker

* API Key
* Secret Key
* Access Token

### Screen 4 – Create Strategy

* Symbol
* Buy time
* Sell time
* Stop-loss
* Quantity

### Screen 5 – Strategy Control

* Start/Stop
* Status card
* Last action

---

# **5.2 Admin Web Application UI Screens (Next.js 15)**

### Screen 1 – Login Page (`/login`)

**Purpose**: Authenticate users and redirect based on role

**Elements**:
* Email input field
* Password input field
* Login button
* "Forgot Password" link
* "Register" link (if public registration enabled)

**Behavior**:
* On successful login, redirect to appropriate dashboard:
  * Admin → `/admin/dashboard`
  * User → `/dashboard`
  * Broker → `/broker/dashboard`
* Show error message for invalid credentials
* Store JWT token in HTTP-only cookie

---

### Screen 2 – Admin Dashboard (`/admin/dashboard`)

**Access**: Admin only

**Elements**:
* **Header**: Logo, user menu (profile, logout)
* **Sidebar**: Navigation menu (Users, Strategies, System, Analytics)
* **Main Content**:
  * System metrics cards (Total Users, Active Strategies, Orders Today, Uptime)
  * Real-time system health chart
  * Recent activity feed (user registrations, strategy starts, errors)
  * Quick action buttons (Create User, View Logs)

**Behavior**:
* Real-time updates via Server-Sent Events
* Click metrics to drill down into details

---

### Screen 3 – User Management (`/admin/users`)

**Access**: Admin only

**Elements**:
* Search bar (search by email, name)
* Filter dropdowns (Role, Status)
* Data table with columns:
  * Email
  * Role (Admin/User/Broker)
  * Status (Active/Inactive)
  * Created At
  * Last Login
  * Actions (Edit, Delete)
* Pagination controls
* "Create User" button

**Behavior**:
* Click "Edit" to open user edit modal
* Click "Delete" to soft delete user (confirmation dialog)
* Click "Create User" to open user creation modal

---

### Screen 4 – Create/Edit User Modal

**Access**: Admin only

**Elements**:
* Email input
* Password input (for new users) / "Reset Password" button (for existing)
* Role dropdown (Admin, User, Broker)
* Status toggle (Active/Inactive)
* Save button
* Cancel button

**Validation**:
* Email must be unique and valid format
* Password must be 8+ characters
* Role is required

---

### Screen 5 – Strategy Oversight (`/admin/strategies`)

**Access**: Admin only

**Elements**:
* Search bar (search by symbol, user email)
* Filter dropdowns (Status, Broker, User)
* Data table with columns:
  * Strategy ID
  * User Email
  * Symbol
  * Status (ACTIVE/RUNNING/STOPPED)
  * Buy Time
  * Sell Time
  * Stop-Loss
  * Created At
  * Actions (View Details, Force Stop)
* Pagination controls

**Behavior**:
* Click "View Details" to see execution logs
* Click "Force Stop" to emergency stop strategy (confirmation dialog)
* Real-time status updates via SSE

---

### Screen 6 – System Health Monitor (`/admin/system`)

**Access**: Admin only

**Elements**:
* **Metrics Section**:
  * System uptime percentage
  * Average API response time
  * Error rate (last 24 hours)
  * Redis memory usage
  * Database connection pool status
* **Charts Section**:
  * API response time over time (line chart)
  * Error distribution by type (pie chart)
  * Request volume per minute (bar chart)
* **Logs Section**:
  * Recent error logs (filterable by severity)
  * Refresh button

**Behavior**:
* Auto-refresh metrics every 30 seconds
* Click chart data points to see detailed logs

---

### Screen 7 – Platform Analytics (`/admin/analytics`)

**Access**: Admin only

**Elements**:
* Date range selector
* **Charts Section**:
  * User growth over time (line chart)
  * Order volume trends (bar chart)
  * Most traded symbols (horizontal bar chart)
  * Broker usage distribution (pie chart)
  * Success rate by broker (table with sparklines)
* Export button (download as CSV/PDF)

**Behavior**:
* Update charts based on date range selection
* Hover over charts to see exact values

---

### Screen 8 – User Dashboard (`/dashboard`)

**Access**: User role

**Elements**:
* **Header**: Logo, user menu (profile, logout)
* **Sidebar**: Navigation (Strategies, Brokers, Playground, Profile)
* **Main Content**:
  * Personal metrics cards (Total Strategies, Today's P&L, This Week's P&L, Success Rate)
  * Active strategies list (with status badges)
  * Quick action buttons (Create Strategy, Add Broker, Go to Playground)
  * Recent activity feed

**Behavior**:
* Real-time P&L updates
* Click strategy to view details

---

### Screen 9 – Create Strategy (`/dashboard/strategies/create`)

**Access**: User role

**Elements**:
* **Form Fields**:
  * Symbol (text input with autocomplete)
  * Buy Time (time picker, HH:MM:SS)
  * Sell Time (time picker, HH:MM:SS)
  * Stop-Loss (number input, required)
  * Quantity (number input)
  * Broker (dropdown, pre-connected brokers)
* **Validation Messages**: Real-time field validation
* Save button
* Cancel button

**Validation**:
* All fields required
* Stop-loss must be positive
* Buy time must be before sell time
* Quantity must be positive integer

---

### Screen 10 – Strategy List (`/dashboard/strategies`)

**Access**: User role

**Elements**:
* Search bar (search by symbol)
* Filter dropdown (Status)
* Strategy cards with:
  * Symbol
  * Status badge (ACTIVE/RUNNING/STOPPED)
  * Buy Time / Sell Time
  * Stop-Loss
  * Current Price (if running)
  * Start/Stop button
  * Edit/Delete buttons
* "Create Strategy" button

**Behavior**:
* Real-time status updates via SSE
* Click "Start" to activate strategy
* Click "Stop" to deactivate
* Click "Edit" to modify (only if not running)

---

### Screen 11 – Broker Integration (`/dashboard/brokers`)

**Access**: User role

**Elements**:
* Connected brokers list (cards):
  * Broker name
  * Connection status (Connected/Disconnected)
  * Last synced timestamp
  * "Test Connection" button
  * "Edit" button
  * "Remove" button
* "Add Broker" button

**Behavior**:
* Click "Add Broker" to open broker connection form
* Click "Test Connection" to verify broker API
* Click "Remove" to disconnect broker (confirmation)

---

### Screen 12 – Add Broker Form (`/dashboard/brokers/add`)

**Access**: User role

**Elements**:
* Broker dropdown (Zerodha, Angel One, Dhan, Fyers)
* API Key input
* Secret Key input
* Access Token input (optional for some brokers)
* "Test Connection" button
* Save button
* Cancel button

**Validation**:
* All required fields based on broker type
* Test connection must succeed before saving

---

### Screen 13 – Strategy Playground (`/dashboard/playground`)

**Access**: User role

**Elements**:
* **Playground Strategy Form**:
  * Symbol
  * Buy Time
  * Sell Time
  * Stop-Loss
  * Quantity
  * Historical data date range selector
* **Results Section** (after running):
  * P&L calculation
  * Win rate percentage
  * Execution accuracy
  * Order timeline visualization
  * "Copy to Live Strategy" button

**Behavior**:
* Run strategy against historical data
* Show simulated order placements
* No real money or broker connection
* Clearly marked as "TEST MODE"

---

### Screen 14 – Broker Dashboard (`/broker/dashboard`)

**Access**: Broker role

**Elements**:
* **Metrics Cards**:
  * Total strategies using this broker
  * Order volume (today, week, month)
  * API success rate
  * Average response time
* **Charts Section**:
  * Order volume over time
  * Error distribution by error code
  * Top users by order volume
* **Integration Health**:
  * API endpoint status
  * Recent errors

**Behavior**:
* Real-time updates via SSE
* Click charts to drill down

---

# **6. System Models**

---

# **6.1 Redis Key Structure**

(from Document Pack: )

```
user:{userId}
strategy:{strategyId}
runtime:{strategyId}
symbol:{symbol}:strategies
queue:orders
```

---

# **6.2 Database Schema (High Level)**

### **User Table**

* id
* email
* password_hash
* created_at

### **BrokerKeys**

* user_id
* api_key (encrypted)
* secret_key (encrypted)
* access_token (encrypted)

### **Strategies**

* id
* user_id
* symbol
* buy_time
* sell_time
* stop_loss
* quantity
* status

### **OrderLogs**

* id
* strategy_id
* type (BUY/SELL/SL)
* timestamp
* response

---

# **7. Success Metrics**

(from PRD: )

| Metric                     | Target        |
| -------------------------- | ------------- |
| Onboarding time            | < 2 minutes   |
| Strategy creation time     | < 1 minute    |
| Execution delay            | < 0.5 seconds |
| Stop-loss reliability      | 99%           |
| API key validation success | 95%           |

---

# **8. Future Enhancements (Not part of MVP)**

(from PRD: )

* Multiple strategies
* Multiple symbols
* P&L analytics
* Push notifications
* Auto-refresh broker tokens

---

# ✔ **Your SRS is Ready**

This is now a **fully expanded, professional-grade SRS** aligned with your PRD and Document Pack.

If you want, I can also generate:

✅ PDF version
✅ DOCX version
✅ Architecture Diagram PNG
✅ API Contracts (Deep-level)
✅ Full HLD + LLD
✅ Developer onboarding handbook
✅ Swagger/OpenAPI spec

Just tell me **“Convert SRS to PDF”** or **“Give me HLD next”**.
