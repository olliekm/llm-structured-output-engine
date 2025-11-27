from abc import ABC, abstractmethod
from typing import Optional, Any

class BaseCache(ABC):
    """Abstract base class for caching LLM responses."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve a cached response by key."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a response in the cache."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a cached response by key."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear the entire cache."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        pass

    @abstractmethod
    def get_stats(self) -> dict:
        """Get cache statistics."""
        pass