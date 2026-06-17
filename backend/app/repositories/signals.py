"""
AlgoSwing — Signals Repository
MongoDB data access layer for trading signals.
"""
from datetime import datetime, timedelta
from typing import Optional

from bson import ObjectId
from loguru import logger

from app.core.database import signals_col
from app.models.signal import Signal, SignalStatus


class SignalsRepository:
    """CRUD operations for the signals collection."""

    async def create(self, signal: Signal) -> Signal:
        """Insert a new signal. Returns signal with generated _id."""
        doc = signal.model_dump(exclude={"id"})
        doc["generated_at"] = signal.generated_at

        result = await signals_col().insert_one(doc)
        signal.id = str(result.inserted_id)
        logger.info(f"✅ Signal saved: {signal.symbol} [{signal.id}]")
        return signal

    async def find_by_id(self, signal_id: str) -> Optional[Signal]:
        """Find a signal by MongoDB ObjectId."""
        try:
            doc = await signals_col().find_one({"_id": ObjectId(signal_id)})
            if not doc:
                return None
            doc["_id"] = str(doc["_id"])
            return Signal(**doc)
        except Exception as e:
            logger.error(f"❌ find_by_id failed: {e}")
            return None

    async def find_active(self, limit: int = 50) -> list[Signal]:
        """Return all ACTIVE signals, newest first."""
        cursor = (
            signals_col()
            .find({"status": SignalStatus.ACTIVE})
            .sort("generated_at", -1)
            .limit(limit)
        )
        signals = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            signals.append(Signal(**doc))
        return signals

    async def find_by_symbol(self, symbol: str, limit: int = 10) -> list[Signal]:
        """Return signals for a specific symbol."""
        cursor = (
            signals_col()
            .find({"symbol": symbol.upper()})
            .sort("generated_at", -1)
            .limit(limit)
        )
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(Signal(**doc))
        return results

    async def find_today(self) -> list[Signal]:
        """Return signals generated today."""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        cursor = (
            signals_col()
            .find({"generated_at": {"$gte": today_start}})
            .sort("generated_at", -1)
        )
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(Signal(**doc))
        return results

    async def exists_today(self, symbol: str, strategy: str) -> bool:
        """Check if a signal already exists for this symbol+strategy today."""
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        count = await signals_col().count_documents({
            "symbol": symbol.upper(),
            "strategy": strategy,
            "generated_at": {"$gte": today_start},
        })
        return count > 0

    async def update_status(self, signal_id: str, status: SignalStatus) -> bool:
        """Update signal status."""
        result = await signals_col().update_one(
            {"_id": ObjectId(signal_id)},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}},
        )
        return result.modified_count > 0

    async def get_recent(self, days: int = 7, limit: int = 100) -> list[Signal]:
        """Return signals from the last N days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        cursor = (
            signals_col()
            .find({"generated_at": {"$gte": cutoff}})
            .sort("generated_at", -1)
            .limit(limit)
        )
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(Signal(**doc))
        return results
