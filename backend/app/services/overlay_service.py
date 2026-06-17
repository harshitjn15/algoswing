from typing import Optional, Dict, Any
from pydantic import BaseModel
from app.repositories.signals import SignalsRepository
from app.repositories.watchlist import WatchlistRepository
from app.strategies.registry import get_strategy

class OverlayData(BaseModel):
    id: str
    type: str
    price: float
    label: str
    color: str = "#2962FF"
    visible: bool = True
    metadata: Dict[str, Any] = {}

class ChartOverlaysResponse(BaseModel):
    ath: Optional[OverlayData] = None
    breakout: Optional[OverlayData] = None
    retest: Optional[OverlayData] = None
    entry: Optional[OverlayData] = None
    sl: Optional[OverlayData] = None
    targets: list[OverlayData] = []

class OverlayService:
    """
    Business logic layer that maps database states (Signals, Watchlist ATH, etc)
    into visual chart overlay instructions.
    """
    def __init__(self):
        self.signals_repo = SignalsRepository()
        self.watchlist_repo = WatchlistRepository()

    async def get_overlays(self, symbol: str) -> ChartOverlaysResponse:
        clean_symbol = symbol.split(":")[-1] if ":" in symbol else symbol
        
        # 1. Fetch signal
        signals = await self.signals_repo.find_recent(days=30)
        signal = next((s for s in signals if s.symbol == clean_symbol), None)

        # 2. Fetch watchlist entry for ATH
        stock = await self.watchlist_repo.find_by_symbol(clean_symbol)

        response = ChartOverlaysResponse()

        # Add ATH if known (universal overlay)
        if stock and stock.ath:
            response.ath = OverlayData(
                id=f"ath_{clean_symbol}",
                type="ATH", 
                price=stock.ath, 
                label="ATH Resistance", 
                color="#ef5350",
                visible=True,
                metadata={"source": "watchlist"}
            )

        # Add Strategy overlays if a signal exists, delegated to the specific strategy class
        if signal:
            strategy_impl = get_strategy(signal.strategy_id)
            if strategy_impl:
                overlays_dicts = strategy_impl.build_overlays(signal)
                for o_dict in overlays_dicts:
                    o_data = OverlayData(**o_dict)
                    if o_data.type == "ENTRY": response.entry = o_data
                    elif o_data.type == "SL": response.sl = o_data
                    elif o_data.type == "BREAKOUT": response.breakout = o_data
                    elif o_data.type == "TARGET": response.targets.append(o_data)

        return response
