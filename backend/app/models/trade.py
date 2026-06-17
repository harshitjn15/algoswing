"""
AlgoSwing — Pydantic models for paper trades
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, AliasChoices


class TradeStatus(str, Enum):
    OPEN = "OPEN"
    TP1_HIT = "TP1_HIT"
    TP2_HIT = "TP2_HIT"
    TP3_HIT = "TP3_HIT"
    STOPPED_OUT = "STOPPED_OUT"
    CLOSED = "CLOSED"


class TradeDirection(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class TradeType(str, Enum):
    PAPER = "PAPER"
    LIVE = "LIVE"


class Trade(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    trade_type: TradeType = TradeType.PAPER
    signal_id: Optional[str] = None
    user_id: str = "default"
    symbol: str
    exchange: str = "NSE"
    direction: TradeDirection = TradeDirection.LONG
    strategy_id: str = Field(validation_alias=AliasChoices('strategy_id', 'strategy'))

    # Order details
    entry_price: float
    qty: int
    position_value: float = 0.0

    # Risk levels
    stop_loss: float
    targets: list[float] = Field(default_factory=list)
    risk_amount: float = 0.0
    risk_pct: float = 0.0

    # P&L
    current_price: Optional[float] = None
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    pnl_pct: float = 0.0

    # Trade state
    status: TradeStatus = TradeStatus.OPEN
    sl_moved_to_entry: bool = False
    sl_moved_to_tp1: bool = False
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None

    # Timestamps
    opened_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class TradeCreate(BaseModel):
    trade_type: TradeType = TradeType.PAPER
    signal_id: Optional[str] = None
    user_id: str = "default"
    symbol: str
    strategy_id: str
    entry_price: float
    qty: int
    stop_loss: float
    targets: list[float]
    risk_pct: float


class TradeCloseRequest(BaseModel):
    exit_price: float
    exit_reason: str = "MANUAL"
