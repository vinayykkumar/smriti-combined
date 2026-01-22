"""
Simple caching utilities (in-memory cache).
"""
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import threading


class SimpleCache:
    """
    Simple thread-safe in-memory cache.
    """
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            expires_at = entry.get('expires_at')
            
            # Check if expired
            if expires_at and datetime.utcnow() > expires_at:
                del self._cache[key]
                return None
            
            return entry.get('value')
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
        """
        with self._lock:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            self._cache[key] = {
                'value': value,
                'expires_at': expires_at
            }
    
    def delete(self, key: str):
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """Get number of cache entries."""
        with self._lock:
            return len(self._cache)


# Global cache instance
cache = SimpleCache()
