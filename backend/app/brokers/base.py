"""
AlgoSwing — Broker Adapter Abstract Base
Implements the Adapter Pattern for broker integrations.

All broker adapters must implement this interface.
The strategy engine NEVER calls broker-specific code directly.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL = "SL"
    SL_M = "SL-M"


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    COMPLETE = "COMPLETE"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass
class Order:
    symbol: str
    exchange: str
    side: OrderSide
    order_type: OrderType
    qty: int
    price: Optional[float] = None
    trigger_price: Optional[float] = None
    tag: Optional[str] = "algoswing"


@dataclass
class OrderResult:
    order_id: str
    status: OrderStatus
    message: str = ""
    filled_price: Optional[float] = None
    filled_qty: int = 0
    timestamp: Optional[datetime] = None


@dataclass
class Position:
    symbol: str
    exchange: str
    qty: int
    avg_price: float
    ltp: float
    pnl: float
    day_pnl: float


class BrokerAdapter(ABC):
    """
    Abstract broker adapter interface.
    Add new brokers by implementing this class — no engine changes needed.
    """

    broker_name: str = "base"

    @abstractmethod
    async def place_order(self, order: Order) -> OrderResult:
        """Place a new order."""
        ...

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing order."""
        ...

    @abstractmethod
    async def get_positions(self) -> list[Position]:
        """Get all open positions."""
        ...

    @abstractmethod
    async def get_orders(self) -> list[dict]:
        """Get order book for today."""
        ...

    @abstractmethod
    async def get_ltp(self, symbol: str, exchange: str = "NSE") -> Optional[float]:
        """Get last traded price for a symbol."""
        ...

    async def is_connected(self) -> bool:
        """Test if broker connection is active."""
        try:
            await self.get_positions()
            return True
        except Exception:
            return False
