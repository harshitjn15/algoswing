"""
AlgoSwing — Paper Trading API Router
"""
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, HTTPException
from loguru import logger

from app.models.trade import Trade, TradeCreate, TradeCloseRequest, TradeStatus
from app.repositories.trades import TradesRepository
from app.repositories.signals import SignalsRepository

router = APIRouter(prefix="/paper-trading", tags=["paper-trading"])


@router.get("/", response_model=List[Trade])
async def list_trades():
    """List all paper trades."""
    repo = TradesRepository()
    return await repo.list_trades()


@router.post("/", response_model=Trade)
async def create_trade(trade_in: TradeCreate):
    """Open a new paper trade."""
    repo = TradesRepository()
    signals_repo = SignalsRepository()
    
    # Optional: fetch current price if entry_price isn't exactly current. 
    # For paper trading, we assume filled at entry_price immediately.
    
    risk_amount = (trade_in.entry_price - trade_in.stop_loss) * trade_in.qty
    position_value = trade_in.entry_price * trade_in.qty
    
    trade = Trade(
        signal_id=trade_in.signal_id,
        user_id=trade_in.user_id,
        symbol=trade_in.symbol,
        strategy_id=trade_in.strategy_id,
        entry_price=trade_in.entry_price,
        qty=trade_in.qty,
        position_value=position_value,
        stop_loss=trade_in.stop_loss,
        targets=trade_in.targets,
        risk_amount=risk_amount,
        risk_pct=trade_in.risk_pct,
        current_price=trade_in.entry_price, # Starts at entry
        status=TradeStatus.OPEN
    )
    
    saved = await repo.create(trade)
    return saved


@router.post("/{trade_id}/close")
async def close_trade(trade_id: str, req: TradeCloseRequest):
    """Manually close a paper trade."""
    repo = TradesRepository()
    trade = await repo.find_by_id(trade_id)
    
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
        
    if trade.status != TradeStatus.OPEN:
        raise HTTPException(status_code=400, detail="Trade is already closed")
        
    pnl = (req.exit_price - trade.entry_price) * trade.qty
    pnl_pct = ((req.exit_price - trade.entry_price) / trade.entry_price) * 100
    
    success = await repo.close_trade(trade_id, req.exit_price, req.exit_reason, pnl, pnl_pct)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to close trade")
        
    return {"message": "Trade closed", "pnl": pnl, "pnl_pct": pnl_pct}


@router.get("/equity")
async def get_equity_curve():
    """Calculate daily equity curve from closed trades for the last 30 days."""
    repo = TradesRepository()
    closed_trades = await repo.get_closed_trades()
    
    base_value = 100000
    current_value = base_value
    
    # We want a 30 day history
    today = datetime.utcnow().date()
    days = [today - timedelta(days=29 - i) for i in range(30)]
    
    equity_data = []
    
    # Process day by day
    for day in days:
        # Add any PnL realized on this day
        daily_pnl = 0
        for t in closed_trades:
            if t.closed_at and t.closed_at.date() == day:
                daily_pnl += t.realized_pnl
                
        current_value += daily_pnl
        equity_data.append({
            "date": day.strftime("%d %b"),
            "value": round(current_value, 2)
        })
        
    return equity_data
