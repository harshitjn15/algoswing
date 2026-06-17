"""
AlgoSwing — Abstract Market Data Provider
All market data providers implement this interface.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Candle:
    """OHLCV candle with timestamp."""
    timestamp: str   # ISO datetime string
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class InstrumentInfo:
    """Basic instrument metadata."""
    symbol: str
    isin: str
    instrument_key: str
    exchange: str = "NSE"
    listing_date: Optional[str] = None


class MarketDataProvider(ABC):
    """Abstract base class for all market data providers."""

    @abstractmethod
    async def get_historical_candles(
        self,
        instrument_key: str,
        from_date: str,
        to_date: str,
        interval: str = "1day",
    ) -> list[Candle]:
        """Fetch OHLCV candles for an instrument."""
        ...

    @abstractmethod
    async def get_quote(self, instrument_key: str) -> Optional[dict]:
        """Fetch real-time quote for an instrument."""
        ...

    @abstractmethod
    async def search_symbols(self, query: str) -> list[InstrumentInfo]:
        """Search for instruments matching the query."""
        ...

    @abstractmethod
    async def get_symbol_info(self, symbol: str) -> Optional[InstrumentInfo]:
        """Get instrument metadata by symbol."""
        ...

    def calculate_ath(self, candles: list[Candle]) -> tuple[float, str]:
        """Calculate all-time high from candle list. Returns (ath, date)."""
        if not candles:
            return 0.0, ""
        ath_candle = max(candles, key=lambda c: c.high)
        return ath_candle.high, ath_candle.timestamp[:10]

    def calculate_avg_volume(self, candles: list[Candle], days: int = 20) -> float:
        """Calculate N-day average volume."""
        if not candles:
            return 0.0
        recent = candles[:days]  # Assumes candles are newest-first
        return sum(c.volume for c in recent) / len(recent) if recent else 0.0
