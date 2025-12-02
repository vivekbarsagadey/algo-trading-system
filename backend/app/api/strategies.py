from enum import Enum
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()

# In-memory strategy store for demo (replace with database in production)
strategies_db: dict = {}


class StrategyType(str, Enum):
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    SCALPING = "scalping"


class StrategyStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"


class StrategyCreate(BaseModel):
    name: str
    strategy_type: StrategyType
    symbol: str
    parameters: dict
    user_id: str


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    parameters: Optional[dict] = None
    status: Optional[StrategyStatus] = None


class StrategyResponse(BaseModel):
    id: str
    name: str
    strategy_type: StrategyType
    symbol: str
    parameters: dict
    status: StrategyStatus
    user_id: str


@router.post("/", response_model=StrategyResponse)
async def create_strategy(strategy: StrategyCreate):
    """Create a new trading strategy."""
    strategy_id = str(uuid4())
    new_strategy = {
        "id": strategy_id,
        "name": strategy.name,
        "strategy_type": strategy.strategy_type,
        "symbol": strategy.symbol,
        "parameters": strategy.parameters,
        "status": StrategyStatus.STOPPED,
        "user_id": strategy.user_id,
    }
    strategies_db[strategy_id] = new_strategy
    return StrategyResponse(**new_strategy)


@router.get("/", response_model=List[StrategyResponse])
async def list_strategies(user_id: Optional[str] = None):
    """List all strategies, optionally filtered by user."""
    strategies = list(strategies_db.values())
    if user_id:
        strategies = [s for s in strategies if s["user_id"] == user_id]
    return [StrategyResponse(**s) for s in strategies]


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: str):
    """Get a specific strategy by ID."""
    if strategy_id not in strategies_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
    return StrategyResponse(**strategies_db[strategy_id])


@router.patch("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(strategy_id: str, update: StrategyUpdate):
    """Update a strategy."""
    if strategy_id not in strategies_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
    strategy = strategies_db[strategy_id]
    if update.name is not None:
        strategy["name"] = update.name
    if update.parameters is not None:
        strategy["parameters"] = update.parameters
    if update.status is not None:
        strategy["status"] = update.status
    return StrategyResponse(**strategy)


@router.delete("/{strategy_id}")
async def delete_strategy(strategy_id: str):
    """Delete a strategy."""
    if strategy_id not in strategies_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
    del strategies_db[strategy_id]
    return {"message": "Strategy deleted successfully"}


@router.post("/{strategy_id}/start", response_model=StrategyResponse)
async def start_strategy(strategy_id: str):
    """Start a strategy (activate for execution)."""
    if strategy_id not in strategies_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
    strategies_db[strategy_id]["status"] = StrategyStatus.ACTIVE
    return StrategyResponse(**strategies_db[strategy_id])


@router.post("/{strategy_id}/stop", response_model=StrategyResponse)
async def stop_strategy(strategy_id: str):
    """Stop a running strategy."""
    if strategy_id not in strategies_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
    strategies_db[strategy_id]["status"] = StrategyStatus.STOPPED
    return StrategyResponse(**strategies_db[strategy_id])
