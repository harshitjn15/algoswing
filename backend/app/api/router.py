"""
AlgoSwing — API Router (v1)
Aggregates all v1 route modules.
"""
from fastapi import APIRouter

from app.api.v1 import (
    health,
    watchlist,
    signals,
    scanner,
    paper_trading,
    market_data,
    symbols,
    chart_overlays,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)
api_router.include_router(signals.router)
api_router.include_router(watchlist.router)
api_router.include_router(scanner.router)
api_router.include_router(paper_trading.router)
api_router.include_router(market_data.router)
api_router.include_router(symbols.router)
api_router.include_router(chart_overlays.router)

# Future Phase routes — uncomment when ready:
# from app.api.v1 import backtesting, strategies, brokers
# api_router.include_router(backtesting.router)
# api_router.include_router(strategies.router)
# api_router.include_router(brokers.router)
