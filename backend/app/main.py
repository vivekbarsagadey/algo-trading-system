from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, broker, strategies

app = FastAPI(
    title="Algo Trading System",
    description="Backend API for algorithmic trading",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(broker.router, prefix="/api/v1/broker", tags=["Broker"])
app.include_router(strategies.router, prefix="/api/v1/strategies", tags=["Strategies"])


@app.get("/")
async def root():
    return {"message": "Algo Trading System API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
