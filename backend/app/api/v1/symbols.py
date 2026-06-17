from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.services.symbol_master_service import SymbolMasterService

router = APIRouter(prefix="/symbols", tags=["Symbols"])

class SymbolSearchResponse(BaseModel):
    symbol: str
    full_name: str
    description: str
    exchange: str
    type: str

class SymbolInfoResponse(BaseModel):
    name: str
    ticker: str
    description: str
    type: str
    exchange: str
    timezone: str = "Asia/Kolkata"

@router.get("/search", response_model=list[SymbolSearchResponse])
async def search_symbols(query: str = Query("", description="Search term")):
    """Generic symbol search service."""
    service = SymbolMasterService()
    results = await service.search_symbols(query)
    
    return [
        SymbolSearchResponse(
            symbol=info.symbol,
            full_name=info.symbol,
            description=f"{info.symbol} ({info.exchange})",
            exchange=info.exchange,
            type="stock"
        )
        for info in results[:20]  # Return max 20 matches
    ]

@router.get("/{symbol}", response_model=SymbolInfoResponse)
async def get_symbol(symbol: str):
    """Get metadata for a specific symbol."""
    service = SymbolMasterService()
    info = await service.get_symbol_info(symbol)
    if not info:
        raise HTTPException(status_code=404, detail="Symbol not found")
        
    return SymbolInfoResponse(
        name=info.symbol,
        ticker=f"{info.exchange}:{info.symbol}",
        description=info.symbol,
        type="stock",
        exchange=info.exchange
    )
