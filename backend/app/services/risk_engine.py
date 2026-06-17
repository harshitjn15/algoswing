from app.models.signal import Signal
from app.repositories.trades import TradesRepository
from app.core.config import get_settings
from loguru import logger

class RiskEngine:
    """
    Evaluates incoming raw signals from strategies against global risk rules.
    Responsibilities:
    - Position sizing
    - SL validation (e.g. SL max 15%)
    - RR validation (e.g. RR min 1:1.5)
    - Portfolio exposure
    - Capital checks
    """
    
    async def evaluate_signal(self, signal: Signal) -> bool:
        """
        Evaluate if a signal is safe to execute.
        Returns True if approved, False if rejected.
        """
        settings = get_settings()
        
        # 1. Stop Loss Validation
        if signal.risk_pct > settings.default_max_sl_pct:
            logger.info(f"RiskEngine rejected {signal.symbol}: SL ({signal.risk_pct:.2f}%) > Max ({settings.default_max_sl_pct}%)")
            return False
            
        # 2. Reward-to-Risk Validation (Minimum 1:1.5)
        if signal.reward_risk_ratio < 1.5:
            logger.info(f"RiskEngine rejected {signal.symbol}: RR ({signal.reward_risk_ratio:.2f}) < 1.5")
            return False
            
        # 3. Capital Exposure Check
        repo = TradesRepository()
        open_trades = await repo.get_open_trades()
        # Max open trades limit - keeping at 10 for standard diversified portfolio
        if len(open_trades) >= 10: 
            logger.info(f"RiskEngine rejected {signal.symbol}: Max open trades limit reached ({len(open_trades)})")
            return False
            
        return True
