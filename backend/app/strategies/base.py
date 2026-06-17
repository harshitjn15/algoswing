"""
AlgoSwing — Strategy Protocol + Base Classes
All strategies implement this protocol.

Design: Uses Protocol (structural subtyping) for duck-typing compatibility,
plus ABC for enforcing the contract in subclasses.
"""
from abc import ABC, abstractmethod
from typing import Optional, Protocol, runtime_checkable

from app.models.signal import Signal, SignalCreate
from app.models.watchlist import WatchlistEntry


@runtime_checkable
class StrategyProtocol(Protocol):
    """
    Structural protocol all strategies must satisfy.
    New strategies only need to implement these methods —
    no inheritance required if using Protocol.
    """

    @property
    def id(self) -> str:
        """Unique identifier for the strategy."""
        ...

    name: str
    version: str
    description: str

    async def scan(self, stocks: list[WatchlistEntry]) -> list[WatchlistEntry]:
        """Filter stocks that qualify for this strategy's initial criteria."""
        ...

    async def generate_signal(self, stock: WatchlistEntry) -> Optional[Signal]:
        """Analyze a qualifying stock and generate a trade signal if conditions met."""
        ...

    def build_overlays(self, signal: Signal) -> list[dict]:
        """Construct the visual overlays for the chart based on the generated signal."""
        ...

    def calculate_stoploss(
        self, symbol: str, entry: float, candles: list
    ) -> float:
        """Calculate stop loss price (nearest swing low, capped at max_sl_pct)."""
        ...

    def calculate_targets(
        self, entry: float, stop_loss: float
    ) -> list[float]:
        """Calculate TP1, TP2, TP3 from entry and stop loss."""
        ...


class BaseStrategy(ABC):
    """
    Abstract base class for strategies.
    Provides shared utilities for risk management.
    """

    name: str = "base"
    version: str = "1.0.0"
    description: str = ""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}

    def _get_config(self, key: str, default):
        """Get config value with fallback to default."""
        return self.config.get(key, default)

    def calculate_risk_pct(self, entry: float, stop_loss: float) -> float:
        """Risk percentage = (entry - SL) / entry * 100."""
        if entry <= 0:
            return 0.0
        return round(abs(entry - stop_loss) / entry * 100, 2)

    def calculate_rr_ratio(
        self, entry: float, stop_loss: float, targets: list[float]
    ) -> float:
        """Risk:Reward ratio using first target."""
        risk = abs(entry - stop_loss)
        if not targets or risk == 0:
            return 0.0
        reward = abs(targets[0] - entry)
        return round(reward / risk, 2)

    def validate_stoploss(self, risk_pct: float, max_sl_pct: float) -> bool:
        """Reject trade if risk exceeds max allowed SL percentage."""
        return risk_pct <= max_sl_pct

    @abstractmethod
    async def scan(self, stocks: list[WatchlistEntry]) -> list[WatchlistEntry]:
        ...

    @abstractmethod
    async def generate_signal(self, stock: WatchlistEntry) -> Optional[Signal]:
        ...

    @abstractmethod
    def calculate_stoploss(self, symbol: str, entry: float, candles: list) -> float:
        ...

    @abstractmethod
    def calculate_targets(self, entry: float, stop_loss: float) -> list[float]:
        ...

    @abstractmethod
    def build_overlays(self, signal: Signal) -> list[dict]:
        ...
