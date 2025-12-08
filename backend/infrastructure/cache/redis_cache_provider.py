from __future__ import annotations

import logging
import pickle
from typing import Any

from redis import Redis

logger = logging.getLogger(__name__)


def _serialize(value: Any) -> bytes:
    return pickle.dumps(value)


def _deserialize(raw: bytes) -> Any:
    return pickle.loads(raw)


class RedisCacheProvider:
    """Redis-backed cache provider with simple pickle serialization."""

    def __init__(self, client: Redis):
        self.client = client

    def get(self, key: str) -> Any | None:
        try:
            raw = self.client.get(key)
        except Exception as exc:  # pragma: no cover - defensive guardrail
            logger.error("redis.get failed for key=%s error=%s", key, exc)
            return None
        if raw is None:
            return None
        try:
            return _deserialize(raw)
        except Exception as exc:  # pragma: no cover - corrupted cache entries
            logger.error("redis.deserialize failed for key=%s error=%s", key, exc)
            return None

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        try:
            self.client.set(name=key, value=_serialize(value), ex=ttl_seconds)
        except Exception as exc:  # pragma: no cover - defensive guardrail
            logger.error("redis.set failed for key=%s error=%s", key, exc)

    def delete(self, key: str) -> None:
        try:
            self.client.delete(key)
        except Exception as exc:  # pragma: no cover - defensive guardrail
            logger.error("redis.delete failed for key=%s error=%s", key, exc)

    def exists(self, key: str) -> bool:
        try:
            return bool(self.client.exists(key))
        except Exception as exc:  # pragma: no cover - defensive guardrail
            logger.error("redis.exists failed for key=%s error=%s", key, exc)
            return False
