from typing import Optional
from app.repositories.watchlist import WatchlistRepository
from app.market_data.base import InstrumentInfo

class SymbolMasterService:
    """
    Service responsible for maintaining the global symbol list,
    handling NSE/BSE lookups, sector mapping, and instrument tokens.
    """
    
    def __init__(self):
        self.watchlist_repo = WatchlistRepository()
    
    async def search_symbols(self, query: str) -> list[InstrumentInfo]:
        """Search for instruments across all known exchanges."""
        # For now, delegates to our local watchlist repository.
        # Future: querying a dedicated `instruments` MongoDB collection or Redis cache.
        stocks = await self.watchlist_repo.find_all(limit=1000)
        
        results = []
        query_upper = query.upper()
        for stock in stocks:
            if query_upper in stock.symbol.upper():
                results.append(InstrumentInfo(
                    symbol=stock.symbol,
                    isin=stock.isin or "",
                    instrument_key=f"NSE_EQ|{stock.isin}",
                    listing_date=stock.listing_date,
                    exchange="NSE"
                ))
        return results

    async def get_symbol_info(self, symbol: str) -> Optional[InstrumentInfo]:
        """Get instrument metadata by generic symbol name."""
        clean_symbol = symbol.split(":")[-1] if ":" in symbol else symbol
        stock = await self.watchlist_repo.find_by_symbol(clean_symbol)
        
        if stock:
            return InstrumentInfo(
                symbol=stock.symbol,
                isin=stock.isin or "",
                instrument_key=f"NSE_EQ|{stock.isin}",
                listing_date=stock.listing_date,
                exchange="NSE"
            )
        return None
