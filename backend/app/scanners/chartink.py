"""
AlgoSwing — Chartink HTTP Scraper
Fetches stocks from Chartink scanner endpoints.

Chartink does not provide a public API. This uses the internal
POST endpoint that powers their screener results table.
"""
import asyncio
from typing import Optional

import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Chartink scanner URL → scan_clause mapping
CHARTINK_SCANNERS = {
    "ipo_base_scan": {
        "url": "https://chartink.com/screener/ipo-base-scan-4",
        "scan_clause": "( {cash} (  market cap >  100 and( {cash} not(  daily max( 252 ,  daily close ) >  0 ) ) and  daily volume >  5000 ) )",
        "description": "IPO Base Scan — stocks near ATH post-IPO",
    },
    # Future scanners:
    # "ath_breakout": { ... },
    # "darvas_box": { ... },
}

CHARTINK_PROCESS_URL = "https://chartink.com/screener/process"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://chartink.com/screener/",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}


class ChartinkScraper:
    """
    Scrapes stock lists from Chartink screener endpoints.

    Usage:
        scraper = ChartinkScraper()
        stocks = await scraper.fetch("ipo_base_scan")
        # returns list of dicts with 'nsecode', 'bsecode', 'per_chg', etc.
    """

    def __init__(self):
        self._session_token: Optional[str] = None

    async def _get_csrf_token(self, client: httpx.AsyncClient, referer_url: str) -> Optional[str]:
        """Fetch Chartink page to extract CSRF token from meta tag."""
        try:
            resp = await client.get(referer_url, headers=HEADERS, timeout=15.0, follow_redirects=True)
            
            # Primary: parse from meta tag (X-CSRF-TOKEN requires this)
            if '<meta name="csrf-token"' in resp.text:
                start = resp.text.index('content="', resp.text.index('csrf-token')) + 9
                end = resp.text.index('"', start)
                csrf = resp.text[start:end]
                logger.debug("✅ Got CSRF token from meta tag")
                return csrf

            # Fallback: Extract from cookie if meta tag fails
            csrf_cookie = client.cookies.get("XSRF-TOKEN")
            if csrf_cookie:
                logger.debug("✅ Got CSRF token from cookie")
                return csrf_cookie

            return None
        except Exception as e:
            logger.warning(f"⚠️  CSRF fetch failed: {e}")
            return None

    @retry(
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=15),
    )
    async def fetch(self, scanner_id: str = "ipo_base_scan") -> list[dict]:
        """
        Fetch stocks from a Chartink scanner.

        Returns list of dicts:
        [
            {
                "nsecode": "SYMBOL",
                "bsecode": "500000",
                "per_chg": "1.23",
                "close": "1234.50",
                "volume": "100000",
                ...
            }
        ]
        """
        config = CHARTINK_SCANNERS.get(scanner_id)
        if not config:
            logger.error(f"❌ Unknown scanner: {scanner_id}")
            return []

        logger.info(f"🔍 Fetching Chartink scanner: {scanner_id}")

        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
        ) as client:
            # Step 1: Get CSRF token
            csrf = await self._get_csrf_token(client, config["url"])

            request_headers = dict(HEADERS)
            request_headers["Referer"] = config["url"]
            if csrf:
                request_headers["X-CSRF-TOKEN"] = csrf

            # Step 2: POST to process endpoint
            payload = {"scan_clause": config["scan_clause"]}

            resp = await client.post(
                CHARTINK_PROCESS_URL,
                data=payload,
                headers=request_headers,
            )

            if resp.status_code != 200:
                logger.error(
                    f"❌ Chartink returned {resp.status_code} for {scanner_id}: {resp.text[:300]}"
                )
                return []

            try:
                data = resp.json()
                stocks = data.get("data", [])
                logger.info(f"✅ Chartink {scanner_id}: {len(stocks)} stocks found")
                return stocks
            except Exception as e:
                logger.error(f"❌ Failed to parse Chartink JSON: {e} - Response snippet: {resp.text[:200]}")
                return []

    async def fetch_all(self) -> dict[str, list[dict]]:
        """Fetch all configured scanners concurrently."""
        tasks = {
            scanner_id: asyncio.create_task(self.fetch(scanner_id))
            for scanner_id in CHARTINK_SCANNERS
        }
        results = {}
        for scanner_id, task in tasks.items():
            try:
                results[scanner_id] = await task
            except Exception as e:
                logger.error(f"❌ Scanner {scanner_id} failed: {e}")
                results[scanner_id] = []
        return results
