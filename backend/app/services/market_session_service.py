from datetime import datetime
import pytz

class MarketSessionService:
    """
    Evaluates market hours for the Indian Stock Market (NSE/BSE).
    Market hours: 09:15 AM to 03:30 PM IST.
    Pre-market: 09:00 AM to 09:15 AM IST.
    """
    
    def __init__(self):
        self.tz = pytz.timezone("Asia/Kolkata")
        
    def get_current_time(self) -> datetime:
        return datetime.now(self.tz)

    def is_market_open(self) -> bool:
        """Returns True if the current time is between 09:15 AM and 03:30 PM IST on a weekday."""
        now = self.get_current_time()
        
        # Weekend check
        if now.weekday() >= 5:
            return False
            
        market_start = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return market_start <= now <= market_end

    def is_pre_market(self) -> bool:
        """Returns True if the current time is between 09:00 AM and 09:15 AM IST."""
        now = self.get_current_time()
        
        if now.weekday() >= 5:
            return False
            
        pre_start = now.replace(hour=9, minute=0, second=0, microsecond=0)
        pre_end = now.replace(hour=9, minute=15, second=0, microsecond=0)
        
        return pre_start <= now < pre_end

    def is_post_market(self) -> bool:
        """Returns True if the current time is after 03:30 PM IST."""
        now = self.get_current_time()
        market_end = now.replace(hour=15, minute=30, second=0, microsecond=0)
        return now > market_end
