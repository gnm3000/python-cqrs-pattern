from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Lock
from typing import Any, Protocol


@dataclass
class CacheEntry:
    expires_at: float
    value: Any


class CacheBackend(Protocol):
    """Shared contract implemented by any cache provider (Redis or in-memory)."""

    def get(self, key: str) -> Any | None: ...

    def set(self, key: str, value: Any, ttl_seconds: int) -> None: ...

    def delete(self, key: str) -> None: ...

    def exists(self, key: str) -> bool: ...


class CacheProvider:
    """Minimal in-memory cache with TTL; designed to be swapped with Redis later."""

    def __init__(self) -> None:
        self._store: dict[str, CacheEntry] = {}
        self._lock = Lock()

    def get(self, key: str) -> Any | None:
        """Return cached value if it is still fresh; otherwise drop and miss."""
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            if entry.expires_at < time.monotonic():
                self._store.pop(key, None)
                return None
            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Store a value with a short TTL; designed for read-side responses."""
        expires_at = time.monotonic() + max(ttl_seconds, 0)
        with self._lock:
            self._store[key] = CacheEntry(expires_at=expires_at, value=value)

    def delete(self, key: str) -> None:
        """Remove a cached entry if present."""
        with self._lock:
            self._store.pop(key, None)

    def exists(self, key: str) -> bool:
        """Check whether a non-expired entry exists for the given key."""
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return False
            if entry.expires_at < time.monotonic():
                self._store.pop(key, None)
                return False
            return True
