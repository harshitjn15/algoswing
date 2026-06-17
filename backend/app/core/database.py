"""
AlgoSwing Backend — MongoDB Motor Async Connection
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from loguru import logger

from app.core.config import get_settings

settings = get_settings()

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    """Create MongoDB connection on app startup."""
    global _client, _db
    logger.info("🔌 Connecting to MongoDB...")
    _client = AsyncIOMotorClient(
        settings.mongodb_url,
        serverSelectionTimeoutMS=5000,
        maxPoolSize=20,
        minPoolSize=5,
    )
    _db = _client[settings.mongodb_db_name]

    # Verify connection
    await _client.admin.command("ping")
    logger.info(f"✅ MongoDB connected — DB: {settings.mongodb_db_name}")


async def close_db() -> None:
    """Close MongoDB connection on app shutdown."""
    global _client
    if _client:
        _client.close()
        logger.info("🔌 MongoDB connection closed")


def get_db() -> AsyncIOMotorDatabase:
    """Return the active database instance."""
    if _db is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return _db


# ─── Collection Accessors ──────────────────────────────────
def get_collection(name: str):
    return get_db()[name]


# Named collection accessors for type safety
def signals_col():
    return get_collection("signals")

def watchlist_col():
    return get_collection("watchlists")

def paper_trades_col():
    return get_collection("paper_trades")

def users_col():
    return get_collection("users")

def backtests_col():
    return get_collection("backtests")

def alerts_col():
    return get_collection("alerts")

def trade_logs_col():
    return get_collection("trade_logs")
