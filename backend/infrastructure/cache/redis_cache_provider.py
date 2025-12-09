from __future__ import annotations

import logging
import time
from dataclasses import asdict, is_dataclass
from typing import Any

import msgpack
from redis import Redis

from infrastructure.cache.cache_provider import CacheMetrics

logger = logging.getLogger(__name__)


def _encode_unknown(value: Any) -> Any:
    """Convert unsupported objects into msgpack-friendly structures."""
    if is_dataclass(value):
        return asdict(value)
    raise TypeError(f"Object of type {type(value).__name__} is not serializable")


def _serialize(value: Any, metrics: CacheMetrics) -> bytes:
    start = time.perf_counter()
    packed = msgpack.packb(value, use_bin_type=True, default=_encode_unknown)
    metrics.serialization_time_ms += (time.perf_counter() - start) * 1000
    metrics.dto_size_bytes = len(packed)
    return packed


def _deserialize(raw: bytes, metrics: CacheMetrics) -> Any:
    start = time.perf_counter()
    value = msgpack.unpackb(raw, raw=False)
    metrics.deserialization_time_ms += (time.perf_counter() - start) * 1000
    return value


class RedisCacheProvider:
    """Redis-backed cache provider using fast msgpack serialization."""

    def __init__(self, client: Redis):
        self.client = client
        self.metrics = CacheMetrics()

    def get(self, key: str) -> Any | None:
        try:
            raw = self.client.get(key)
        except Exception as exc:  # pragma: no cover - defensive guardrail
            logger.error("redis.get failed for key=%s error=%s", key, exc)
            return None
        if raw is None:
            self.metrics.cache_miss_count += 1
            return None
        try:
            value = _deserialize(raw, self.metrics)
            self.metrics.cache_hit_count += 1
            return value
        except Exception as exc:  # pragma: no cover - corrupted cache entries
            logger.error("redis.deserialize failed for key=%s error=%s", key, exc)
            self.metrics.cache_miss_count += 1
            return None

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        try:
            packed = _serialize(value, self.metrics)
            self.client.set(name=key, value=packed, ex=ttl_seconds)
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
