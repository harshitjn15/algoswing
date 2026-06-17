import asyncio
from typing import Callable, Dict, List, Any
from loguru import logger

class EventBus:
    """
    Naive in-memory Pub/Sub event bus.
    In the future, this can be swapped with Redis Pub/Sub, Kafka, or RabbitMQ.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type}")

    async def publish(self, event_type: str, payload: Any):
        logger.info(f"Event published: {event_type}")
        if event_type in self._subscribers:
            # Dispatch all callbacks concurrently
            tasks = []
            for callback in self._subscribers[event_type]:
                if asyncio.iscoroutinefunction(callback):
                    tasks.append(asyncio.create_task(callback(payload)))
                else:
                    # Run sync callbacks in thread pool if needed, 
                    # but simple direct call for now.
                    try:
                        callback(payload)
                    except Exception as e:
                        logger.error(f"Error in sync event callback: {e}")
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

# Global singleton instance for the monolith
event_bus = EventBus()

# Predefined Event Types
EVENT_SIGNAL_CREATED = "signal_created"
EVENT_SIGNAL_TRIGGERED = "signal_triggered"
EVENT_SIGNAL_EXPIRED = "signal_expired"
EVENT_TRADE_OPENED = "trade_opened"
EVENT_TRADE_CLOSED = "trade_closed"
EVENT_TP1_HIT = "tp1_hit"
EVENT_TP2_HIT = "tp2_hit"
EVENT_TP3_HIT = "tp3_hit"
EVENT_SL_HIT = "sl_hit"
EVENT_MARKET_TICK = "market_tick"
