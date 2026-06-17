"""
AlgoSwing — Pydantic models for watchlist entries
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WatchlistEntry(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    symbol: str
    exchange: str = "NSE"
    isin: Optional[str] = None
    scanner: str  # e.g. "ipo_base_scan"
    listing_date: Optional[str] = None

    # Price metrics
    ath: Optional[float] = None
    ath_date: Optional[str] = None
    last_close: Optional[float] = None
    ath_distance_pct: Optional[float] = None  # negative = below ATH
    near_ath: bool = False

    # Volume metrics
    volume_ratio: Optional[float] = None  # current / 20d avg
    avg_volume_20d: Optional[float] = None

    # Timestamps
    scanned_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class WatchlistEntryCreate(BaseModel):
    symbol: str
    exchange: str = "NSE"
    isin: Optional[str] = None
    scanner: str
    listing_date: Optional[str] = None
    ath: Optional[float] = None
    ath_date: Optional[str] = None
    last_close: Optional[float] = None
    ath_distance_pct: Optional[float] = None
    near_ath: bool = False
    volume_ratio: Optional[float] = None
    avg_volume_20d: Optional[float] = None
