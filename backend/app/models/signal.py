"""
AlgoSwing — Pydantic models for trading signals
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, AliasChoices
from bson import ObjectId


class SignalStatus(str, Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    TRIGGERED = "TRIGGERED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Signal(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    symbol: str
    exchange: str = "NSE"
    strategy_id: str = Field(validation_alias=AliasChoices('strategy_id', 'strategy'))
    strategy_version: str = "1.0.0"
    isin: Optional[str] = None

    # Price levels
    entry: float
    stop_loss: float
    targets: list[float] = Field(default_factory=list)

    # Risk metrics
    risk_pct: float
    reward_risk_ratio: float = 0.0
    position_size: Optional[int] = None

    # ATH context
    ath: float
    ath_date: Optional[str] = None
    ath_distance_pct: float = 0.0
    breakout_date: Optional[str] = None
    breakout_price: Optional[float] = None
    breakout_volume: Optional[float] = None

    # Volume context
    volume_ratio: float = 0.0
    avg_volume_20d: Optional[float] = None

    # Signal metadata
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    signal_score: float = 0.0
    status: SignalStatus = SignalStatus.CREATED
    notes: Optional[str] = None

    # Timestamps
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    triggered_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class SignalCreate(BaseModel):
    symbol: str
    exchange: str = "NSE"
    strategy_id: str
    strategy_version: str = "1.0.0"
    isin: Optional[str] = None
    entry: float
    stop_loss: float
    targets: list[float]
    risk_pct: float
    reward_risk_ratio: float
    ath: float
    ath_date: Optional[str] = None
    ath_distance_pct: float
    breakout_date: Optional[str] = None
    breakout_price: Optional[float] = None
    breakout_volume: Optional[float] = None
    volume_ratio: float
    avg_volume_20d: Optional[float] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    signal_score: float = 0.0
    notes: Optional[str] = None


class SignalResponse(Signal):
    """API response model — always has an ID."""
    id: str = Field(..., alias="_id")
