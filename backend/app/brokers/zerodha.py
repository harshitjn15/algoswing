"""
AlgoSwing — Zerodha Broker Adapter (Phase 4)
Stub implementation — full implementation in Phase 4.
"""
from typing import Optional
from loguru import logger

from app.brokers.base import BrokerAdapter, Order, OrderResult, Position, OrderStatus


class ZerodhaAdapter(BrokerAdapter):
    """
    Zerodha KiteConnect Adapter.
    Phase 4 implementation.
    """
    broker_name = "zerodha"

    def __init__(self, api_key: str = "", access_token: str = ""):
        self._api_key = api_key
        self._token = access_token

    async def place_order(self, order: Order) -> OrderResult:
        logger.warning("ZerodhaAdapter: Phase 4 not yet implemented")
        return OrderResult(order_id="", status=OrderStatus.REJECTED, message="Phase 4")

    async def cancel_order(self, order_id: str) -> bool:
        return False

    async def get_positions(self) -> list[Position]:
        return []

    async def get_orders(self) -> list[dict]:
        return []

    async def get_ltp(self, symbol: str, exchange: str = "NSE") -> Optional[float]:
        return None
