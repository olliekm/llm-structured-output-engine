from typing import Any, Optional
from collections import OrderedDict
from .base import BaseCache
import time

class InMemoryCache(BaseCache):
    """In-memory cache implementation of BaseCache."""

    def __init__(self, max_size: int = 1000, default_ttl=3600):
        self._max_size = max_size
        self._cache = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            entry = self._cache[key]
            if entry[key]["timestamp"] + entry[key]["ttl"] < time.time():
                self.delete(key)
                self._misses += 1
                return None
            self._hits += 1
            self._cache.move_to_end(key)  # Mark as recently used
            return entry[key]["value"]
        self._misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)  # Remove least recently used item
        
        if ttl is None:
            ttl = self._default_ttl

        self._cache[key] = {
            "value": value,
            "timestamp": time.time(),
            "ttl": ttl
        }

    def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        self._cache.clear()

    def exists(self, key: str) -> bool:
        return key in self._cache
    
    def get_stats(self) -> dict:

        total = self._hits + self._misses
        hit_rate = (self._hits / total) * 100 if total > 0 else 0.0

        return {
            "size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.2f}%"
        }