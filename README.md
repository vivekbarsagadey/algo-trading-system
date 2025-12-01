# Algo Trading System

A monorepo containing a FastAPI backend service and an Expo React Native mobile app for algorithmic trading.

## Project Structure

```
.
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── api/            # API routes (auth, broker, strategies)
│   │   ├── core/           # Core configuration and security
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic services
│   │   └── workers/        # Redis workers for execution
│   ├── requirements.txt
│   └── Dockerfile
├── apps/
│   └── mobile/             # Expo React Native app
│       ├── app/            # App screens and navigation
│       ├── components/     # Reusable components
│       └── package.json
├── docker-compose.yml      # Postgres + Redis services
├── .env.example            # Environment variables template
└── README.md
```

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+ and npm
- Expo CLI (`npm install -g expo-cli`)

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/vivekbarsagadey/algo-trading-system.git
cd algo-trading-system
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start infrastructure services

```bash
docker-compose up -d
```

### 4. Set up the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 5. Set up the mobile app

```bash
cd apps/mobile
npm install
npx expo start
```

## Features

### Backend (FastAPI)
- **Authentication**: JWT-based user authentication
- **Broker Connect**: Integration with trading brokers
- **Strategies**: Create and manage trading strategies
- **Workers**: Redis-backed workers for trade execution

### Mobile App (Expo React Native)
- **Login**: User authentication screen
- **Broker Setup**: Configure broker connections
- **Strategy Management**: View and manage trading strategies

## License

MIT