from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from loguru import logger

from app.market_data.upstox import get_upstox_provider
from app.repositories.watchlist import WatchlistRepository

router = APIRouter(prefix="/market-data", tags=["Market Data"])

class TVCandle(BaseModel):
    time: int
    open: float
    high: float
    low: float
    close: float
    volume: float

class TVSymbolInfo(BaseModel):
    name: str
    ticker: str
    description: str
    type: str
    exchange: str
    timezone: str = "Asia/Kolkata"
    minmov: int = 1
    pricescale: int = 100
    session: str = "0915-1530"
    has_intraday: bool = False
    has_daily: bool = True
    has_weekly_and_monthly: bool = True
    supported_resolutions: list[str] = ["1D", "1W", "1M"]
    volume_precision: int = 0
    data_status: str = "streaming"

@router.get("/candles", response_model=list[TVCandle])
async def get_candles(
    symbol: str = Query(..., description="Symbol format like NSE:RELIANCE or RELIANCE"),
    resolution: str = Query("D", description="TradingView resolution string"),
    from_date: int = Query(..., alias="from", description="Unix timestamp from"),
    to_date: int = Query(..., alias="to", description="Unix timestamp to"),
):
    """
    Fetch historical candles for TradingView DataFeed.
    """
    try:
        # Strip prefix if present (e.g. NSE:RELIANCE -> RELIANCE)
        clean_symbol = symbol.split(":")[-1] if ":" in symbol else symbol
        
        # 1. We need the ISIN for Upstox. We can lookup in Watchlist Repo
        repo = WatchlistRepository()
        stock = await repo.find_by_symbol(clean_symbol)
        
        # If not in watchlist, we would ideally search a global NSE master, 
        # but for now we require it to be scanned at least once or we can't find its ISIN.
        if not stock or not stock.isin:
            raise HTTPException(status_code=404, detail="Symbol not found in local database")

        instrument_key = f"NSE_EQ|{stock.isin}"
        
        # Convert unix timestamps to YYYY-MM-DD
        dt_from = datetime.fromtimestamp(from_date, tz=timezone.utc).strftime("%Y-%m-%d")
        dt_to = datetime.fromtimestamp(to_date, tz=timezone.utc).strftime("%Y-%m-%d")

        # Map resolution
        interval_map = {"D": "day", "1D": "day", "1W": "week", "1M": "month"}
        interval = interval_map.get(resolution, "day")

        upstox = get_upstox_provider()
        candles = await upstox.get_historical_candles(
            instrument_key=instrument_key,
            from_date=dt_from,
            to_date=dt_to,
            interval=interval
        )

        # Map to TV format
        tv_candles = []
        for c in candles:
            # Upstox returns ISO timestamps string like '2024-05-15T00:00:00+05:30'
            try:
                # remove timezone info and parse to timestamp
                dt = datetime.fromisoformat(c.timestamp)
                # TV expects Unix timestamp in seconds
                unix_time = int(dt.timestamp())
                tv_candles.append(TVCandle(
                    time=unix_time,
                    open=c.open,
                    high=c.high,
                    low=c.low,
                    close=c.close,
                    volume=c.volume
                ))
            except Exception as e:
                logger.warning(f"Error parsing date {c.timestamp}: {e}")
                continue

        # TV expects oldest to newest
        tv_candles.reverse()
        return tv_candles

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching candles for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

from fastapi import WebSocket, WebSocketDisconnect

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Placeholder for future real-time market data streaming.
    Upstox WebSocket -> FastAPI -> TradingView
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # In a real implementation, we would subscribe to the Upstox broker
            # websocket stream and forward updates.
            logger.info(f"Received WS message: {data}")
            # Echo back a heartbeat
            await websocket.send_json({"status": "connected", "echo": data})
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
