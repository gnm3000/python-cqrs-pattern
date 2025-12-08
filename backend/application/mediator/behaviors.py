from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable

from application.queries.base import IQuery
from infrastructure.cache.cache_provider import CacheProvider

QueryHandler = Callable[[IQuery], Any]


class QueryBehavior(Protocol):
    """Middleware-style behavior that wraps query handlers."""

    def handle(self, query: IQuery, next_handler: QueryHandler) -> Any:
        ...


@runtime_checkable
class CacheableQuery(Protocol):
    """Queries that can be cached expose a key and TTL."""

    @property
    def cache_key(self) -> str:
        ...

    @property
    def cache_ttl_seconds(self) -> int:
        ...


class CacheBehavior:
    """Intercept cacheable queries to serve hot responses without hitting the DB."""

    def __init__(self, cache: CacheProvider):
        self.cache = cache

    def handle(self, query: IQuery, next_handler: QueryHandler) -> Any:
        if not isinstance(query, CacheableQuery):
            return next_handler(query)

        cached = self.cache.get(query.cache_key)
        if cached is not None:
            return cached

        result = next_handler(query)
        if query.cache_ttl_seconds > 0:
            self.cache.set(query.cache_key, result, query.cache_ttl_seconds)
        return result


class LoggingBehavior:
    """Structured logging around queries to expose duration and payload size."""

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("mediator.logging")

    def handle(self, query: IQuery, next_handler: QueryHandler) -> Any:
        start = time.perf_counter()
        result = next_handler(query)
        duration_ms = (time.perf_counter() - start) * 1000
        result_count = len(result) if isinstance(result, list) else (1 if result is not None else 0)
        self.logger.info(
            "query=%s duration_ms=%.2f items=%s",
            type(query).__name__,
            duration_ms,
            result_count,
        )
        return result


class TimingBehavior:
    """Fine-grained timing metrics to feed synthetic tests (k6) and dashboards."""

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("mediator.timing")

    def handle(self, query: IQuery, next_handler: QueryHandler) -> Any:
        start = time.perf_counter()
        result = next_handler(query)
        latency_ms = (time.perf_counter() - start) * 1000
        self.logger.debug("timing query=%s latency_ms=%.2f", type(query).__name__, latency_ms)
        return result
