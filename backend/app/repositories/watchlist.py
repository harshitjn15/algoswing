"""
AlgoSwing — Watchlist Repository
MongoDB data access layer for watchlist entries.
"""
from datetime import datetime
from typing import Optional

from bson import ObjectId
from loguru import logger

from app.core.database import watchlist_col
from app.models.watchlist import WatchlistEntry


class WatchlistRepository:
    """CRUD operations for the watchlists collection."""

    async def upsert(self, entry: WatchlistEntry) -> WatchlistEntry:
        """Insert or update a watchlist entry (upsert on symbol + scanner)."""
        doc = entry.model_dump(exclude={"id"})
        doc["updated_at"] = datetime.utcnow()

        result = await watchlist_col().find_one_and_update(
            {"symbol": entry.symbol, "scanner": entry.scanner},
            {"$set": doc},
            upsert=True,
            return_document=True,
        )

        if result:
            result["_id"] = str(result["_id"])
            return WatchlistEntry(**result)
        return entry

    async def upsert_many(self, entries: list[WatchlistEntry], clear_obsolete: bool = True) -> int:
        """Bulk upsert multiple watchlist entries. Returns count upserted."""
        if not entries:
            return 0

        scanner_name = entries[0].scanner
        symbols = [e.symbol for e in entries]

        if clear_obsolete:
            delete_result = await watchlist_col().delete_many({
                "scanner": scanner_name,
                "symbol": {"$nin": symbols}
            })
            if delete_result.deleted_count > 0:
                logger.info(f"🧹 Cleared {delete_result.deleted_count} obsolete stocks from {scanner_name}")

        count = 0
        for entry in entries:
            try:
                await self.upsert(entry)
                count += 1
            except Exception as e:
                logger.error(f"❌ Watchlist upsert failed for {entry.symbol}: {e}")

        logger.info(f"✅ Watchlist updated: {count}/{len(entries)} entries")
        return count

    async def find_all(
        self,
        scanner: Optional[str] = None,
        near_ath_only: bool = False,
        limit: int = 100,
    ) -> list[WatchlistEntry]:
        """Return watchlist entries with optional filters."""
        query: dict = {}
        if scanner:
            query["scanner"] = scanner
        if near_ath_only:
            query["near_ath"] = True

        cursor = (
            watchlist_col()
            .find(query)
            .sort("ath_distance_pct", 1)  # Closest to ATH first (least negative)
            .limit(limit)
        )

        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(WatchlistEntry(**doc))
        return results

    async def find_by_symbol(self, symbol: str) -> Optional[WatchlistEntry]:
        """Find a single watchlist entry by symbol."""
        doc = await watchlist_col().find_one({"symbol": symbol.upper()})
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return WatchlistEntry(**doc)

    async def count(self, near_ath_only: bool = False) -> int:
        """Count watchlist entries."""
        query = {"near_ath": True} if near_ath_only else {}
        return await watchlist_col().count_documents(query)
