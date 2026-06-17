"""
AlgoSwing — Watchlist API Router
GET /api/v1/watchlist — list all watched stocks
GET /api/v1/watchlist/near-ath — stocks near ATH only
GET /api/v1/watchlist/{symbol} — single stock details
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models.watchlist import WatchlistEntry
from app.repositories.watchlist import WatchlistRepository

router = APIRouter(prefix="/watchlist", tags=["watchlist"])
_repo = WatchlistRepository()


@router.get("/", response_model=list[WatchlistEntry])
async def get_watchlist(
    scanner: Optional[str] = Query(None),
    near_ath_only: bool = Query(False),
    limit: int = Query(100, ge=1, le=500),
):
    """Return watchlist with optional filters."""
    return await _repo.find_all(
        scanner=scanner,
        near_ath_only=near_ath_only,
        limit=limit,
    )


@router.get("/near-ath", response_model=list[WatchlistEntry])
async def get_near_ath():
    """Return only stocks within ATH range."""
    return await _repo.find_all(near_ath_only=True)


@router.get("/stats")
async def get_watchlist_stats():
    """Return summary stats for the watchlist."""
    total = await _repo.count()
    near_ath = await _repo.count(near_ath_only=True)
    return {
        "total": total,
        "near_ath": near_ath,
        "pct_near_ath": round((near_ath / total * 100) if total > 0 else 0, 1),
    }


@router.get("/{symbol}", response_model=WatchlistEntry)
async def get_stock(symbol: str):
    """Return a single watchlist entry by symbol."""
    entry = await _repo.find_by_symbol(symbol.upper())
    if not entry:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not in watchlist")
    return entry
