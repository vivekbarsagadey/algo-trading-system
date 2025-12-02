from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.strategy import Strategy as StrategyModel, StrategyStatus, StrategyType

router = APIRouter()


# Reuse StrategyType and StrategyStatus from `app.models.strategy` to ensure consistent enums across model & API.


class StrategyCreate(BaseModel):
    name: str
    strategy_type: StrategyType
    symbol: str
    parameters: dict
    user_id: int


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    parameters: Optional[dict] = None
    status: Optional[StrategyStatus] = None


class StrategyResponse(BaseModel):
    id: int
    name: str
    strategy_type: StrategyType
    symbol: str
    parameters: dict
    status: StrategyStatus
    user_id: int

    model_config = ConfigDict(from_attributes=True)


@router.post("/", response_model=StrategyResponse)
def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    """Create a new trading strategy and persist to the database."""
    db_strategy = StrategyModel(
        name=strategy.name,
        strategy_type=strategy.strategy_type,
        symbol=strategy.symbol,
        parameters=strategy.parameters,
        status=StrategyStatus.STOPPED,
        user_id=strategy.user_id,
    )
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return StrategyResponse.from_orm(db_strategy)


@router.get("/", response_model=List[StrategyResponse])
def list_strategies(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    """List all strategies, optionally filtered by user."""
    query = db.query(StrategyModel)
    if user_id:
        query = query.filter(StrategyModel.user_id == user_id)
    strategies = query.all()
    return [StrategyResponse.from_orm(s) for s in strategies]


@router.get("/{strategy_id}", response_model=StrategyResponse)
def get_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Get a specific strategy by ID."""
    strategy = db.get(StrategyModel, strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
    return StrategyResponse.from_orm(strategy)


@router.patch("/{strategy_id}", response_model=StrategyResponse)
def update_strategy(strategy_id: int, update: StrategyUpdate, db: Session = Depends(get_db)):
    """Update a strategy."""
    strategy = db.get(StrategyModel, strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
    if update.name is not None:
        strategy.name = update.name
    if update.parameters is not None:
        strategy.parameters = update.parameters
    if update.status is not None:
        strategy.status = update.status
    db.commit()
    db.refresh(strategy)
    return StrategyResponse.from_orm(strategy)


@router.delete("/{strategy_id}")
def delete_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Delete a strategy."""
    strategy = db.get(StrategyModel, strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
    db.delete(strategy)
    db.commit()
    return {"message": "Strategy deleted successfully"}


@router.post("/{strategy_id}/start", response_model=StrategyResponse)
def start_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Start a strategy (activate for execution)."""
    strategy = db.get(StrategyModel, strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
    strategy.status = StrategyStatus.ACTIVE
    db.commit()
    db.refresh(strategy)
    return StrategyResponse.from_orm(strategy)


@router.post("/{strategy_id}/stop", response_model=StrategyResponse)
def stop_strategy(strategy_id: int, db: Session = Depends(get_db)):
    """Stop a running strategy."""
    strategy = db.get(StrategyModel, strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
    strategy.status = StrategyStatus.STOPPED
    db.commit()
    db.refresh(strategy)
    return StrategyResponse.from_orm(strategy)
