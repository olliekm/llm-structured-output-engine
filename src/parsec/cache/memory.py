"""In-memory LRU cache implementation."""
from typing import Any, Optional
from collections import OrderedDict
from .base import BaseCache
import time


class InMemoryCache(BaseCache):
    """
    In-memory LRU (Least Recently Used) cache with TTL support.

    This cache implementation uses an OrderedDict to maintain insertion/access order
    and automatically evicts the least recently used items when the cache is full.
    Each cached item has an optional TTL (time-to-live) after which it expires.

    Attributes:
        _max_size: Maximum number of items the cache can hold
        _cache: OrderedDict storing cached entries with metadata
        _hits: Counter for cache hits (successful retrievals)
        _misses: Counter for cache misses (failed retrievals)
        _default_ttl: Default time-to-live in seconds for cache entries

    Example:
        >>> cache = InMemoryCache(max_size=100, default_ttl=3600)
        >>> cache.set("key1", {"data": "value"})
        >>> cache.get("key1")
        {'data': 'value'}
        >>> cache.get_stats()
        {'size': 1, 'hits': 1, 'misses': 0, 'hit_rate': '100.00%'}
    """

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize the in-memory cache.

        Args:
            max_size: Maximum number of entries to store (default: 1000)
            default_ttl: Default time-to-live in seconds (default: 3600 = 1 hour)
        """
        self._max_size = max_size
        self._cache = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.

        Automatically handles TTL expiration and updates LRU ordering.

        Args:
            key: Cache key to retrieve

        Returns:
            Optional[Any]: Cached value if found and not expired, None otherwise

        Side effects:
            - Increments hit counter if found and valid
            - Increments miss counter if not found or expired
            - Moves accessed key to end (most recently used)
            - Deletes expired entries
        """
        if key in self._cache:
            entry = self._cache[key]
            if entry["timestamp"] + entry["ttl"] < time.time():
                self.delete(key)
                self._misses += 1
                return None
            self._hits += 1
            self._cache.move_to_end(key)  # Mark as recently used
            return entry["value"]
        self._misses += 1
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store a value in the cache.

        If cache is full, evicts the least recently used item before insertion.

        Args:
            key: Cache key
            value: Value to cache (can be any Python object)
            ttl: Optional time-to-live in seconds (uses default_ttl if None)

        Side effects:
            - May evict LRU item if cache is at max_size
            - Updates existing entries if key already exists
        """
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
        """
        Remove an entry from the cache.

        Args:
            key: Cache key to delete

        Note:
            No-op if key doesn't exist (won't raise KeyError)
        """
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """
        Remove all entries from the cache.

        Note:
            Does not reset hit/miss counters
        """
        self._cache.clear()

    def exists(self, key: str) -> bool:
        """
        Check if a key exists in the cache.

        Args:
            key: Cache key to check

        Returns:
            bool: True if key exists, False otherwise

        Note:
            Does not check TTL expiration or update LRU ordering
        """
        return key in self._cache

    def get_stats(self) -> dict:
        """
        Get cache performance statistics.

        Returns:
            dict: Statistics including:
                - size: Current number of cached items
                - hits: Total number of successful retrievals
                - misses: Total number of failed retrievals
                - hit_rate: Percentage of requests that were hits (formatted string)

        Example:
            >>> cache.get_stats()
            {'size': 42, 'hits': 100, 'misses': 10, 'hit_rate': '90.91%'}
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total) * 100 if total > 0 else 0.0

        return {
            "size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.2f}%"
        }