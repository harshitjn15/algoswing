import asyncio
from loguru import logger
from app.services.market_session_service import MarketSessionService

class ScannerScheduler:
    """
    Manages the cron-like scheduling of market scanners.
    Extracts scheduling logic away from the core services.
    """
    
    def __init__(self):
        self.session_service = MarketSessionService()
        self._is_running = False
        
    async def start(self):
        """Start the background scheduling loop."""
        self._is_running = True
        logger.info("ScannerScheduler started.")
        asyncio.create_task(self._loop())
        
    def stop(self):
        """Stop the background scheduling loop."""
        self._is_running = False
        logger.info("ScannerScheduler stopped.")

    async def _loop(self):
        while self._is_running:
            if self.session_service.is_market_open():
                # TODO: Trigger scanners (e.g. IPO ATH)
                logger.debug("Market is open. Scanners running...")
            else:
                logger.debug("Market is closed. Scanners idle.")
                
            # Sleep for X minutes before next check
            await asyncio.sleep(300) # 5 minutes
