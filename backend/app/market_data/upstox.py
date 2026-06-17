"""
AlgoSwing — Upstox Market Data Provider
Migrated and improved from /Downloads/test/calculateAllTimeHigh.py

Improvements over prototype:
- Async HTTP (httpx) instead of sync requests
- Token loaded from env (not hardcoded)
- Retry logic with exponential backoff (tenacity)
- Full Candle dataclass instead of raw list indexing
- Proper error handling + structured logging
"""
import asyncio
from datetime import date, timedelta
from typing import Optional

import httpx
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from app.core.config import get_settings
from app.market_data.base import MarketDataProvider, Candle, InstrumentInfo

settings = get_settings()

UPSTOX_BASE_URL = "https://api.upstox.com/v3"
UPSTOX_V2_URL = "https://api.upstox.com/v2"


class UpstoxProvider(MarketDataProvider):
    """
    Upstox v3 historical candle data provider.
    Uses NSE_EQ|<ISIN> as instrument_key format.
    """

    def __init__(self, access_token: Optional[str] = None):
        self._token = access_token or settings.upstox_access_token
        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self._token}",
        }

    def set_token(self, token: str) -> None:
        """Update access token (called after OAuth refresh)."""
        self._token = token
        self._headers["Authorization"] = f"Bearer {token}"

    async def search_symbols(self, query: str) -> list[InstrumentInfo]:
        """Search for instruments (falling back to local WatchlistRepository)."""
        from app.repositories.watchlist import WatchlistRepository
        repo = WatchlistRepository()
        stocks = await repo.find_all(limit=1000)
        
        results = []
        query_upper = query.upper()
        for stock in stocks:
            if query_upper in stock.symbol.upper():
                results.append(InstrumentInfo(
                    symbol=stock.symbol,
                    isin=stock.isin or "",
                    instrument_key=f"NSE_EQ|{stock.isin}",
                    listing_date=stock.listing_date
                ))
        return results

    async def get_symbol_info(self, symbol: str) -> Optional[InstrumentInfo]:
        """Get instrument metadata by symbol."""
        from app.repositories.watchlist import WatchlistRepository
        repo = WatchlistRepository()
        clean_symbol = symbol.split(":")[-1] if ":" in symbol else symbol
        stock = await repo.find_by_symbol(clean_symbol)
        if stock:
            return InstrumentInfo(
                symbol=stock.symbol,
                isin=stock.isin or "",
                instrument_key=f"NSE_EQ|{stock.isin}",
                listing_date=stock.listing_date
            )
        return None

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=False,
    )
    async def get_historical_candles(
        self,
        instrument_key: str,
        from_date: str,
        to_date: str,
        interval: str = "day",
    ) -> list[Candle]:
        """
        Fetch daily OHLCV candles from Upstox v2.

        Args:
            instrument_key: Format "NSE_EQ|<ISIN>" e.g. "NSE_EQ|INE009A01021"
            from_date: "YYYY-MM-DD"
            to_date: "YYYY-MM-DD"
            interval: "day" (default)

        Returns:
            List of Candle objects, newest-first (as returned by Upstox).
        """
        url = f"{UPSTOX_V2_URL}/historical-candle/{instrument_key}/{interval}/{to_date}/{from_date}"

        logger.debug(f"📊 Fetching candles: {instrument_key} [{from_date} → {to_date}]")

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, headers=self._headers)

        if resp.status_code == 401:
            logger.error(f"❌ Upstox: Unauthorized — access token may be expired")
            return []

        if resp.status_code == 400 and "UDAPI1148" in resp.text:
            # Upstox returns Invalid Date Range if the from_date is before their data history for this stock.
            # We walk the date forward by 3 years and try again until we find data.
            try:
                from datetime import datetime, timedelta
                fd = datetime.strptime(from_date, "%Y-%m-%d")
                td = datetime.strptime(to_date, "%Y-%m-%d")
                fd += timedelta(days=1095) # shift 3 years forward
                if fd < td:
                    new_from = fd.strftime("%Y-%m-%d")
                    logger.debug(f"🔄 Retrying {instrument_key} with newer from_date: {new_from}")
                    return await self.get_historical_candles(instrument_key, new_from, to_date, interval)
            except Exception as e:
                logger.warning(f"Failed to auto-adjust date for {instrument_key}: {e}")

        if resp.status_code != 200:
            logger.warning(
                f"⚠️  Upstox {resp.status_code} for {instrument_key}: {resp.text[:200]}"
            )
            return []

        data = resp.json()
        raw_candles = data.get("data", {}).get("candles", [])

        candles = [
            Candle(
                timestamp=c[0],
                open=float(c[1]),
                high=float(c[2]),
                low=float(c[3]),
                close=float(c[4]),
                volume=float(c[5]),
            )
            for c in raw_candles
        ]

        logger.debug(f"✅ {instrument_key}: {len(candles)} candles fetched")
        return candles

    async def get_quote(self, instrument_key: str) -> Optional[dict]:
        """Fetch real-time quote (LTP, volume, etc.)."""
        url = f"{UPSTOX_V2_URL}/market-quote/ltp"
        params = {"instrument_key": instrument_key}

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=self._headers, params=params)

        if resp.status_code != 200:
            logger.warning(f"⚠️  Quote failed for {instrument_key}: {resp.status_code}")
            return None

        return resp.json().get("data", {})

    async def get_full_market_data(
        self,
        isin: str,
        listing_date: str,
        rate_limit_delay: float = 0.25,
    ) -> dict:
        """
        Convenience method: fetches all candles from listing date to today.
        Returns enriched dict with ath, last_close, volume_ratio, near_ath.

        This is the core logic migrated from calculateAllTimeHigh.py.
        """
        today = date.today()
        to_date = today.strftime("%Y-%m-%d")

        instrument_key = f"NSE_EQ|{isin}"

        await asyncio.sleep(rate_limit_delay)  # Rate limit guard

        candles = await self.get_historical_candles(
            instrument_key=instrument_key,
            from_date=listing_date,
            to_date=to_date,
        )

        if not candles:
            return {
                "isin": isin,
                "instrument_key": instrument_key,
                "ath": None,
                "ath_date": None,
                "last_close": None,
                "ath_distance_pct": None,
                "near_ath": False,
                "avg_volume_20d": None,
                "volume_ratio": None,
                "candles": [],
            }

        # ATH = max HIGH across all candles
        ath, ath_date = self.calculate_ath(candles)

        # Last close = most recent candle's close (index 0, newest-first)
        last_close = candles[0].close

        # ATH distance
        ath_distance_pct = ((last_close - ath) / ath) * 100  # negative = below ATH

        # Near ATH = within ±5%
        near_ath = abs(ath_distance_pct) <= 5.0

        # 20-day average volume
        avg_volume_20d = self.calculate_avg_volume(candles, days=20)

        # Volume ratio = today's volume / 20-day avg
        current_volume = candles[0].volume
        volume_ratio = (current_volume / avg_volume_20d) if avg_volume_20d > 0 else 0.0

        return {
            "isin": isin,
            "instrument_key": instrument_key,
            "ath": ath,
            "ath_date": ath_date,
            "last_close": last_close,
            "ath_distance_pct": round(ath_distance_pct, 2),
            "near_ath": near_ath,
            "avg_volume_20d": round(avg_volume_20d, 0),
            "volume_ratio": round(volume_ratio, 2),
            "candles": candles,
        }


# Singleton provider instance
_upstox_provider: Optional[UpstoxProvider] = None


def get_upstox_provider() -> UpstoxProvider:
    global _upstox_provider
    if _upstox_provider is None:
        _upstox_provider = UpstoxProvider()
    return _upstox_provider
