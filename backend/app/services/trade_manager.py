"""
AlgoSwing — Paper Trade Manager
Evaluates open paper trades against live market prices and automatically closes them
if Stop Loss or Take Profit targets are hit.
"""
from loguru import logger
import yfinance as yf
from app.repositories.trades import TradesRepository

class TradeManager:
    async def manage_active_trades(self):
        repo = TradesRepository()
        open_trades = await repo.get_open_trades()
        if not open_trades:
            return
            
        logger.info(f"🔄 TradeManager: Evaluating {len(open_trades)} open paper trades")
        
        # Batch fetch prices using yfinance
        symbols = [f"{t.symbol}.NS" for t in open_trades]
        
        try:
            tickers = yf.Tickers(" ".join(symbols))
            
            for trade in open_trades:
                ticker = tickers.tickers.get(f"{trade.symbol}.NS")
                if not ticker:
                    continue
                    
                try:
                    # Get the current live price
                    current_price = ticker.fast_info.last_price
                    if not current_price:
                        continue
                        
                    # Update current price in DB (optional, but good for tracking)
                    await repo.update(trade.id, {"current_price": current_price})
                    
                    exit_price = None
                    exit_reason = None
                    
                    # Check Stop Loss
                    if current_price <= trade.stop_loss:
                        exit_price = current_price
                        exit_reason = "Stop Loss Hit"
                    # Check Take Profit
                    elif current_price >= trade.targets[-1]:  # Using final target for simplicity
                        exit_price = current_price
                        exit_reason = "Target Hit"
                    
                    # Close the trade if criteria met
                    if exit_price:
                        pnl = (exit_price - trade.entry_price) * trade.qty
                        pnl_pct = ((exit_price - trade.entry_price) / trade.entry_price) * 100
                        await repo.close_trade(
                            trade_id=trade.id,
                            exit_price=exit_price,
                            exit_reason=exit_reason,
                            pnl=pnl,
                            pnl_pct=pnl_pct
                        )
                        logger.info(f"💰 TradeManager: Closed {trade.symbol} at {exit_price:.2f} ({exit_reason}) | PnL: {pnl_pct:.2f}%")
                        
                except Exception as e:
                    logger.error(f"❌ TradeManager failed to process {trade.symbol}: {e}")
        except Exception as e:
            logger.error(f"❌ TradeManager failed to fetch batch prices: {e}")
