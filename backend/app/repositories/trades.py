"""
AlgoSwing — Trades Repository
MongoDB data access layer for paper trades.
"""
from datetime import datetime
from typing import Optional

from bson import ObjectId
from loguru import logger

from app.core.database import paper_trades_col
from app.models.trade import Trade, TradeStatus


class TradesRepository:
    """CRUD operations for the paper_trades collection."""

    async def create(self, trade: Trade) -> Trade:
        """Insert a new paper trade. Returns trade with generated _id."""
        doc = trade.model_dump(exclude={"id"})
        doc["opened_at"] = trade.opened_at

        result = await paper_trades_col().insert_one(doc)
        trade.id = str(result.inserted_id)
        logger.info(f"✅ Paper Trade saved: {trade.symbol} [{trade.id}]")
        return trade

    async def find_by_id(self, trade_id: str) -> Optional[Trade]:
        """Find a trade by MongoDB ObjectId."""
        try:
            doc = await paper_trades_col().find_one({"_id": ObjectId(trade_id)})
            if not doc:
                return None
            doc["_id"] = str(doc["_id"])
            return Trade(**doc)
        except Exception as e:
            logger.error(f"❌ find_by_id failed for trade {trade_id}: {e}")
            return None

    async def list_trades(self, user_id: str = "default", limit: int = 100) -> list[Trade]:
        """Return all trades for a user, newest first."""
        cursor = (
            paper_trades_col()
            .find({"user_id": user_id})
            .sort("opened_at", -1)
            .limit(limit)
        )
        trades = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            trades.append(Trade(**doc))
        return trades

    async def get_closed_trades(self, user_id: str = "default", limit: int = 1000) -> list[Trade]:
        """Return closed trades to calculate historical PnL."""
        cursor = (
            paper_trades_col()
            .find({"user_id": user_id, "status": {"$ne": TradeStatus.OPEN}})
            .sort("closed_at", 1)
            .limit(limit)
        )
        trades = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            trades.append(Trade(**doc))
        return trades

    async def get_open_trades(self, user_id: str = "default", limit: int = 1000) -> list[Trade]:
        """Return currently open trades."""
        cursor = (
            paper_trades_col()
            .find({"user_id": user_id, "status": TradeStatus.OPEN})
            .sort("opened_at", -1)
            .limit(limit)
        )
        trades = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            trades.append(Trade(**doc))
        return trades

    async def update(self, trade_id: str, updates: dict) -> bool:
        """Update trade fields."""
        result = await paper_trades_col().update_one(
            {"_id": ObjectId(trade_id)},
            {"$set": updates},
        )
        return result.modified_count > 0

    async def close_trade(self, trade_id: str, exit_price: float, exit_reason: str, pnl: float, pnl_pct: float) -> bool:
        """Close a trade manually."""
        updates = {
            "status": TradeStatus.CLOSED,
            "exit_price": exit_price,
            "exit_reason": exit_reason,
            "realized_pnl": pnl,
            "pnl_pct": pnl_pct,
            "closed_at": datetime.utcnow()
        }
        return await self.update(trade_id, updates)
