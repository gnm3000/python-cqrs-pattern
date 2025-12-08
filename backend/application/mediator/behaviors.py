from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable

from domain.events.invalidation_service import InvalidationService
from infrastructure.cache.cache_provider import CacheBackend
from infrastructure.outbox.outbox_processor import OutboxProcessor

from application.queries.base import IQuery

QueryHandler = Callable[[IQuery], Any]
CommandHandler = Callable[[Any], Any]


class QueryBehavior(Protocol):
    """Middleware-style behavior that wraps query handlers."""

    def handle(self, query: IQuery, next_handler: QueryHandler) -> Any: ...


@runtime_checkable
class CacheableQuery(Protocol):
    """Queries that can be cached expose a key and TTL."""

    @property
    def cache_key(self) -> str: ...

    @property
    def cache_ttl_seconds(self) -> int: ...


class CacheBehavior:
    """Intercept cacheable queries to serve hot responses without hitting the DB."""

    def __init__(self, cache: CacheBackend, logger: logging.Logger | None = None):
        self.cache = cache
        self.logger = logger or logging.getLogger("mediator.cache")

    def handle(self, query: IQuery, next_handler: QueryHandler) -> Any:
        if not isinstance(query, CacheableQuery):
            return next_handler(query)

        cached = self.cache.get(query.cache_key)
        if cached is not None:
            self.logger.info("cache_hit query=%s key=%s", type(query).__name__, query.cache_key)
            return cached

        result = next_handler(query)
        if query.cache_ttl_seconds > 0:
            self.cache.set(query.cache_key, result, query.cache_ttl_seconds)
            self.logger.info(
                "cache_set query=%s key=%s ttl=%s",
                type(query).__name__,
                query.cache_key,
                query.cache_ttl_seconds,
            )
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


class CommandBehavior(Protocol):
    """Middleware-style behavior that wraps command handlers."""

    def handle(self, command: Any, next_handler: CommandHandler) -> Any: ...


class CommandInvalidationBehavior:
    """After a successful command, invalidate read-side cache entries."""

    def __init__(
        self, invalidation_service: InvalidationService, logger: logging.Logger | None = None
    ):
        self.invalidation_service = invalidation_service
        self.logger = logger or logging.getLogger("mediator.invalidation")

    def handle(self, command: Any, next_handler: CommandHandler) -> Any:
        result = next_handler(command)
        self.invalidation_service.invalidate_for(command)
        self.logger.info("cache_invalidate command=%s", type(command).__name__)
        return result


class OutboxDispatchBehavior:
    """After the write transaction commits, fan out domain events to projectors."""

    def __init__(self, processor: OutboxProcessor):
        self.processor = processor

    def handle(self, command: Any, next_handler: CommandHandler) -> Any:
        result = next_handler(command)
        self.processor.process_pending_events()
        return result


class CommandLoggingBehavior:
    """Structured logging around commands to expose duration and outcomes."""

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger("mediator.command")

    def handle(self, command: Any, next_handler: CommandHandler) -> Any:
        start = time.perf_counter()
        result = next_handler(command)
        duration_ms = (time.perf_counter() - start) * 1000
        self.logger.info("command=%s duration_ms=%.2f", type(command).__name__, duration_ms)
        return result
