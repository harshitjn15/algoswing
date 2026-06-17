from loguru import logger
from app.events.bus import EVENT_SIGNAL_CREATED, EVENT_TRADE_OPENED, event_bus
from app.models.signal import Signal

class NotificationService:
    """
    Listens to EventBus events and dispatches notifications via external channels
    (Telegram, Email, Push). Strategies should NEVER call Telegram directly.
    """
    
    def __init__(self):
        # Subscribe to events on initialization
        event_bus.subscribe(EVENT_SIGNAL_CREATED, self.handle_signal_created)
        event_bus.subscribe(EVENT_TRADE_OPENED, self.handle_trade_opened)
        
    async def handle_signal_created(self, payload: Signal):
        """Handle new signal notifications."""
        logger.info(f"NotificationService: Signal created for {payload.symbol}")
        # TODO: Await telegram_bot.send_message(...)

    async def handle_trade_opened(self, payload: dict):
        """Handle new trade notifications."""
        logger.info(f"NotificationService: Trade opened. {payload}")
        # TODO: Await telegram_bot.send_message(...)

# Global instance
notification_service = NotificationService()
