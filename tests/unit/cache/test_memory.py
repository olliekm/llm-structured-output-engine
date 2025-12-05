"""Tests for InMemoryCache class."""

import pytest
import time

from parsec.cache.memory import InMemoryCache


class TestInMemoryCacheBasics:
    """Test basic cache functionality."""

    def test_create_cache(self):
        """Test creating a cache."""
        cache = InMemoryCache(max_size=10, default_ttl=60)
        assert cache._max_size == 10
        assert cache._default_ttl == 60

    def test_set_and_get(self):
        """Test setting and getting values."""
        cache = InMemoryCache()
        cache.set("key1", "value1")

        result = cache.get("key1")
        assert result == "value1"

    def test_get_nonexistent(self):
        """Test getting nonexistent key returns None."""
        cache = InMemoryCache()
        result = cache.get("nonexistent")
        assert result is None

    def test_set_different_types(self):
        """Test caching different value types."""
        cache = InMemoryCache()

        cache.set("string", "hello")
        cache.set("int", 42)
        cache.set("float", 3.14)
        cache.set("list", [1, 2, 3])
        cache.set("dict", {"key": "value"})

        assert cache.get("string") == "hello"
        assert cache.get("int") == 42
        assert cache.get("float") == 3.14
        assert cache.get("list") == [1, 2, 3]
        assert cache.get("dict") == {"key": "value"}

    def test_overwrite_value(self):
        """Test overwriting existing value."""
        cache = InMemoryCache()

        cache.set("key", "value1")
        assert cache.get("key") == "value1"

        cache.set("key", "value2")
        assert cache.get("key") == "value2"


class TestInMemoryCacheTTL:
    """Test TTL (time-to-live) functionality."""

    def test_ttl_expiration(self):
        """Test that entries expire after TTL."""
        cache = InMemoryCache(default_ttl=1)  # 1 second TTL

        cache.set("key", "value")
        assert cache.get("key") == "value"

        # Wait for expiration
        time.sleep(1.1)

        assert cache.get("key") is None

    def test_custom_ttl(self):
        """Test setting custom TTL per entry."""
        cache = InMemoryCache(default_ttl=10)

        cache.set("key1", "value1", ttl=1)  # 1 second
        cache.set("key2", "value2", ttl=5)  # 5 seconds

        time.sleep(1.1)

        # key1 should be expired, key2 should still exist
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_ttl_zero_expires_immediately(self):
        """Test that TTL=0 expires immediately."""
        cache = InMemoryCache(default_ttl=10)

        cache.set("key", "value", ttl=0)

        time.sleep(0.1)

        # Should be expired
        assert cache.get("key") is None


class TestInMemoryCacheLRU:
    """Test LRU (Least Recently Used) eviction."""

    def test_lru_eviction(self):
        """Test that LRU entry is evicted when max_size is reached."""
        cache = InMemoryCache(max_size=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # All should exist
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

        # Add 4th item, should evict key1 (least recently used)
        cache.set("key4", "value4")

        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_get_updates_lru(self):
        """Test that getting a value updates its LRU position."""
        cache = InMemoryCache(max_size=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Access key1 to make it recently used
        cache.get("key1")

        # Add 4th item, should evict key2 (now least recently used)
        cache.set("key4", "value4")

        assert cache.get("key1") == "value1"  # Still exists
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"

    def test_set_updates_lru(self):
        """Test that setting an existing key updates its LRU position."""
        cache = InMemoryCache(max_size=3)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # Update key1
        cache.set("key1", "new_value1")

        # Add 4th item, should evict key2 (least recently used)
        cache.set("key4", "value4")

        assert cache.get("key1") == "new_value1"  # Still exists
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"


class TestInMemoryCacheStatistics:
    """Test cache statistics."""

    def test_stats_empty(self):
        """Test stats for empty cache."""
        cache = InMemoryCache()
        stats = cache.get_stats()

        assert stats["size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["hit_rate"] == "0.00%"

    def test_stats_hits(self):
        """Test hit statistics."""
        cache = InMemoryCache()
        cache.set("key", "value")

        cache.get("key")  # Hit
        cache.get("key")  # Hit

        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 0
        assert stats["hit_rate"] == "100.00%"

    def test_stats_misses(self):
        """Test miss statistics."""
        cache = InMemoryCache()

        cache.get("nonexistent1")  # Miss
        cache.get("nonexistent2")  # Miss

        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 2
        assert stats["hit_rate"] == "0.00%"

    def test_stats_mixed(self):
        """Test mixed hit/miss statistics."""
        cache = InMemoryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.get("key1")  # Hit
        cache.get("key2")  # Hit
        cache.get("nonexistent")  # Miss
        cache.get("key1")  # Hit

        stats = cache.get_stats()
        assert stats["hits"] == 3
        assert stats["misses"] == 1
        assert stats["hit_rate"] == "75.00%"
        assert stats["size"] == 2

    def test_stats_after_expiration(self):
        """Test that expired entries count as misses."""
        cache = InMemoryCache(default_ttl=1)
        cache.set("key", "value")

        cache.get("key")  # Hit

        time.sleep(1.1)

        cache.get("key")  # Miss (expired)

        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1


class TestInMemoryCacheClear:
    """Test cache clearing."""

    def test_clear_cache(self):
        """Test clearing all cache entries."""
        cache = InMemoryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        cache.clear()

        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") is None

        stats = cache.get_stats()
        assert stats["size"] == 0

    def test_clear_preserves_stats(self):
        """Test that clear preserves statistics (by design)."""
        cache = InMemoryCache()
        cache.set("key", "value")
        cache.get("key")
        cache.get("nonexistent")

        cache.clear()

        stats = cache.get_stats()
        # Stats are preserved even after clear (by design)
        assert stats["hits"] == 1
        assert stats["misses"] == 1


class TestInMemoryCacheDelete:
    """Test deleting specific entries."""

    def test_delete_entry(self):
        """Test deleting a specific entry."""
        cache = InMemoryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        cache.delete("key1")

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_delete_nonexistent(self):
        """Test deleting nonexistent key doesn't error."""
        cache = InMemoryCache()
        cache.delete("nonexistent")  # Should not raise

    def test_delete_updates_size(self):
        """Test that delete updates cache size."""
        cache = InMemoryCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        stats = cache.get_stats()
        assert stats["size"] == 2

        cache.delete("key1")

        stats = cache.get_stats()
        assert stats["size"] == 1


class TestInMemoryCacheEdgeCases:
    """Test edge cases and special scenarios."""

    def test_max_size_small(self):
        """Test cache with small max_size."""
        cache = InMemoryCache(max_size=2)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Both should exist
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"

        # Adding third should evict first
        cache.set("key3", "value3")
        assert cache.get("key1") is None

    def test_max_size_one(self):
        """Test cache with max_size=1."""
        cache = InMemoryCache(max_size=1)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        cache.set("key2", "value2")
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_large_cache(self):
        """Test cache with many entries."""
        cache = InMemoryCache(max_size=1000)

        # Add 500 entries
        for i in range(500):
            cache.set(f"key{i}", f"value{i}")

        # All should be retrievable
        for i in range(500):
            assert cache.get(f"key{i}") == f"value{i}"

        stats = cache.get_stats()
        assert stats["size"] == 500

    def test_none_value(self):
        """Test storing None as a value."""
        cache = InMemoryCache()
        cache.set("key", None)

        # Should be able to distinguish stored None from missing key
        # In current implementation, both return None
        # This is a known limitation
        result = cache.get("key")
        # Note: This will return None, which is ambiguous
        # Future improvement could use a sentinel value

    def test_empty_key(self):
        """Test using empty string as key."""
        cache = InMemoryCache()
        cache.set("", "empty_key_value")

        assert cache.get("") == "empty_key_value"
