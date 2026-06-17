from abc import ABC, abstractmethod
from typing import Any, Optional

class BaseCache(ABC):
    """Abstract interface for application caching."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        ...
        
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        ...


class InMemoryCache(BaseCache):
    """Simple in-memory dictionary cache for local development."""
    def __init__(self):
        self._store = {}
        
    async def get(self, key: str) -> Optional[Any]:
        return self._store.get(key)
        
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        self._store[key] = value
        
    async def delete(self, key: str) -> None:
        self._store.pop(key, None)


class RedisCache(BaseCache):
    """Redis-based caching for production (Stub)."""
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        # self.client = redis.Redis.from_url(redis_url)
        
    async def get(self, key: str) -> Optional[Any]:
        pass
        
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        pass
        
    async def delete(self, key: str) -> None:
        pass
