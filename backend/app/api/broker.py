from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()

# In-memory broker store for demo (replace with database in production)
broker_connections: dict = {}


class BrokerConfig(BaseModel):
    broker_name: str
    api_key: str
    api_secret: str
    user_id: str


class BrokerResponse(BaseModel):
    broker_name: str
    user_id: str
    is_connected: bool


class BrokerStatus(BaseModel):
    broker_name: str
    status: str
    message: Optional[str] = None


@router.post("/connect", response_model=BrokerResponse)
async def connect_broker(config: BrokerConfig):
    """Connect to a trading broker with provided credentials."""
    # In production, this would validate credentials with the actual broker API
    broker_connections[config.user_id] = {
        "broker_name": config.broker_name,
        "api_key": config.api_key,
        "api_secret": config.api_secret,
        "is_connected": True,
    }
    return BrokerResponse(
        broker_name=config.broker_name,
        user_id=config.user_id,
        is_connected=True,
    )


@router.delete("/disconnect/{user_id}", response_model=BrokerStatus)
async def disconnect_broker(user_id: str):
    """Disconnect from the broker."""
    if user_id not in broker_connections:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No broker connection found for this user",
        )
    broker_name = broker_connections[user_id]["broker_name"]
    del broker_connections[user_id]
    return BrokerStatus(
        broker_name=broker_name,
        status="disconnected",
        message="Successfully disconnected from broker",
    )


@router.get("/status/{user_id}", response_model=BrokerStatus)
async def get_broker_status(user_id: str):
    """Get the current broker connection status."""
    if user_id not in broker_connections:
        return BrokerStatus(
            broker_name="none",
            status="not_connected",
            message="No broker connection found",
        )
    connection = broker_connections[user_id]
    return BrokerStatus(
        broker_name=connection["broker_name"],
        status="connected" if connection["is_connected"] else "disconnected",
        message="Broker is connected and ready",
    )


@router.get("/supported", response_model=List[str])
async def get_supported_brokers():
    """Get list of supported brokers."""
    return ["zerodha", "upstox", "angelone", "fyers", "iifl"]
