import enum

from sqlalchemy import (JSON, DateTime, Enum, ForeignKey, Integer,
                        String)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy.sql import func

from app.core.database import Base


class StrategyType(str, enum.Enum):
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    SCALPING = "scalping"


class StrategyStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"


class Strategy(Base):
    __tablename__ = "strategies"

    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, nullable=False)
    strategy_type: Mapped[StrategyType] = mapped_column(Enum(StrategyType), nullable=False)
    symbol = mapped_column(String, nullable=False)
    parameters: Mapped[dict] = mapped_column(JSON, nullable=False, default={})
    status: Mapped[StrategyStatus] = mapped_column(Enum(StrategyStatus), default=StrategyStatus.STOPPED)
    user_id = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())
