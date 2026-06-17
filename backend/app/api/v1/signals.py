"""
AlgoSwing — Signals API Router
GET /api/v1/signals — list active signals
GET /api/v1/signals/today — signals generated today
GET /api/v1/signals/{id} — single signal
PATCH /api/v1/signals/{id}/status — update status
"""
from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from app.models.signal import Signal, SignalStatus
from app.repositories.signals import SignalsRepository

router = APIRouter(prefix="/signals", tags=["signals"])
_repo = SignalsRepository()


@router.get("/", response_model=list[Signal])
async def get_active_signals(
    limit: int = Query(50, ge=1, le=200),
):
    """Return all active signals, newest first."""
    return await _repo.find_active(limit=limit)


@router.get("/today", response_model=list[Signal])
async def get_today_signals():
    """Return signals generated today."""
    return await _repo.find_today()


@router.get("/recent", response_model=list[Signal])
async def get_recent_signals(
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(100, ge=1, le=500),
):
    """Return signals from last N days."""
    return await _repo.get_recent(days=days, limit=limit)


@router.get("/{signal_id}", response_model=Signal)
async def get_signal(signal_id: str):
    """Return a single signal by ID."""
    signal = await _repo.find_by_id(signal_id)
    if not signal:
        raise HTTPException(status_code=404, detail=f"Signal {signal_id} not found")
    return signal


@router.patch("/{signal_id}/status")
async def update_signal_status(signal_id: str, status: SignalStatus):
    """Update signal status (ACTIVE → TRIGGERED, EXPIRED, etc.)."""
    updated = await _repo.update_status(signal_id, status)
    if not updated:
        raise HTTPException(status_code=404, detail="Signal not found")
    return {"message": f"Signal {signal_id} status updated to {status}"}
