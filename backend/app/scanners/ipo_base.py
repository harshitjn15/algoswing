"""
AlgoSwing — IPO Base Scanner
Migrated and improved from /Downloads/test/fetchData.py

Steps:
1. Fetch stocks from Chartink IPO Base Scan
2. Look up ISIN + listing date from NSE master data
3. Fetch Upstox OHLCV data for each stock
4. Return WatchlistEntry objects with ATH metrics

Improvements over prototype:
- Async instead of sync
- ISIN lookup from NSE API instead of local CSV
- Concurrent data fetching with rate limiting
- Proper logging and error handling
"""
import asyncio
from typing import Optional
from datetime import datetime

import httpx
from loguru import logger

from app.scanners.base import BaseScanner
from app.scanners.chartink import ChartinkScraper
from app.market_data.upstox import get_upstox_provider
from app.models.watchlist import WatchlistEntry

# NSE EQUITY master file URL (updated daily by NSE)
NSE_EQUITY_MASTER_URL = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"


class IPOBaseScanner(BaseScanner):
    """
    IPO Base Scanner — fetches IPO stocks from Chartink and enriches
    them with ATH, volume, and ISIN data from Upstox.
    """

    name = "ipo_base_scan"
    description = "IPO Base Scan — stocks near ATH post-IPO listing"

    def __init__(self):
        self._chartink = ChartinkScraper()
        self._upstox = get_upstox_provider()
        self._nse_master: Optional[dict[str, dict]] = None  # symbol → {isin, listing_date}

    async def _load_nse_master(self) -> dict[str, dict]:
        """Load NSE equity master from NSE archives. Cache in memory."""
        if self._nse_master is not None:
            return self._nse_master

        logger.info("📥 Loading NSE equity master...")

        try:
            async with httpx.AsyncClient(
                timeout=30.0,
                headers={"User-Agent": "Mozilla/5.0"},
            ) as client:
                resp = await client.get(NSE_EQUITY_MASTER_URL)

            if resp.status_code != 200:
                logger.error(f"❌ NSE master failed: {resp.status_code}")
                return {}

            # Parse CSV
            import io
            import csv
            reader = csv.DictReader(io.StringIO(resp.text))
            if reader.fieldnames:
                reader.fieldnames = [field.strip() for field in reader.fieldnames]
                
            master = {}
            for row in reader:
                symbol = row.get("SYMBOL", "").strip().upper()
                if not symbol:
                    continue
                master[symbol] = {
                    "isin": row.get("ISIN NUMBER", "").strip(),
                    "listing_date": row.get("DATE OF LISTING", "").strip(),
                    "series": row.get("SERIES", "").strip(),
                }

            self._nse_master = master
            logger.info(f"✅ NSE master loaded: {len(master)} symbols")
            return master

        except Exception as e:
            logger.error(f"❌ NSE master load failed: {e}", exc_info=True)
            return {}

    def _format_listing_date(self, date_str: str) -> Optional[str]:
        """Convert NSE date formats to YYYY-MM-DD."""
        for fmt in ("%d-%b-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        return None

    async def _enrich_stock(
        self,
        symbol: str,
        nse_info: dict,
        semaphore: asyncio.Semaphore,
    ) -> Optional[WatchlistEntry]:
        """Fetch Upstox data for one stock with rate-limit semaphore."""
        async with semaphore:
            isin = nse_info.get("isin", "")
            listing_date_raw = nse_info.get("listing_date", "")

            if not isin or not listing_date_raw:
                logger.warning(f"⚠️  {symbol}: Missing ISIN or listing date — skipping")
                return None

            listing_date = self._format_listing_date(listing_date_raw)
            if not listing_date:
                logger.warning(f"⚠️  {symbol}: Cannot parse listing date '{listing_date_raw}'")
                return None

            logger.debug(f"📊 Enriching {symbol} (ISIN: {isin})")

            try:
                data = await self._upstox.get_full_market_data(
                    isin=isin,
                    listing_date=listing_date,
                    rate_limit_delay=0.0,  # Semaphore handles rate limiting
                )

                return WatchlistEntry(
                    symbol=symbol,
                    exchange="NSE",
                    isin=isin,
                    scanner=self.name,
                    listing_date=listing_date,
                    ath=data["ath"],
                    ath_date=data["ath_date"],
                    last_close=data["last_close"],
                    ath_distance_pct=data["ath_distance_pct"],
                    near_ath=data["near_ath"],
                    volume_ratio=data["volume_ratio"],
                    avg_volume_20d=data["avg_volume_20d"],
                )

            except Exception as e:
                logger.error(f"❌ Failed to enrich {symbol}: {e}")
                return None

    async def scan(self) -> list[WatchlistEntry]:
        """
        Run the full IPO Base Scan pipeline:
        1. Fetch symbols from Chartink
        2. Load NSE master for ISIN/listing date
        3. Enrich each symbol with Upstox OHLCV data (concurrent, rate-limited)
        4. Return all successful WatchlistEntry objects
        """
        logger.info("🚀 Starting IPO Base Scan...")

        # Step 1: Chartink scan
        chartink_stocks = await self._chartink.fetch("ipo_base_scan")
        if not chartink_stocks:
            logger.warning("⚠️  No stocks from Chartink — aborting scan")
            return []

        symbols = [s.get("nsecode", "").strip().upper() for s in chartink_stocks]
        symbols = [s for s in symbols if s]
        logger.info(f"📋 Chartink returned {len(symbols)} symbols: {symbols[:10]}...")

        # Step 2: Load NSE master
        nse_master = await self._load_nse_master()

        # Step 3: Filter to symbols we have NSE data for
        enrichable = {
            symbol: nse_master[symbol]
            for symbol in symbols
            if symbol in nse_master
        }
        missing = set(symbols) - set(enrichable.keys())
        if missing:
            logger.warning(f"⚠️  {len(missing)} symbols not in NSE master: {list(missing)[:5]}")

        # Step 4: Concurrent enrichment with rate limiting (max 5 concurrent)
        semaphore = asyncio.Semaphore(5)
        tasks = [
            self._enrich_stock(symbol, info, semaphore)
            for symbol, info in enrichable.items()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        entries: list[WatchlistEntry] = []
        for r in results:
            if isinstance(r, WatchlistEntry):
                entries.append(r)
            elif isinstance(r, Exception):
                logger.error(f"❌ Enrichment task failed: {r}")

        logger.info(f"✅ IPO Base Scan complete: {len(entries)}/{len(symbols)} stocks enriched")
        return entries
