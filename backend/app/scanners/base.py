"""
AlgoSwing — Abstract Scanner Base Class
All scanners return a list of WatchlistEntry objects.
"""
from abc import ABC, abstractmethod

from app.models.watchlist import WatchlistEntry


class BaseScanner(ABC):
    """Abstract base for all stock scanners."""

    name: str = "base"
    description: str = ""

    @abstractmethod
    async def scan(self) -> list[WatchlistEntry]:
        """
        Run the scanner and return qualifying stocks as WatchlistEntry list.
        Each entry has symbol, ISIN, listing_date, and any pre-computed metrics.
        """
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
