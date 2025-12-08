from __future__ import annotations

import logging

from config import REDIS_DB, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from domain.events.invalidation_service import InvalidationService
from infrastructure.cache.cache_provider import CacheBackend, CacheProvider
from infrastructure.cache.redis_cache_provider import RedisCacheProvider
from infrastructure.read_repository.employees_read_repository import EmployeesReadRepository
from redis import Redis
from sqlalchemy.orm import Session

from application.commands.employees import (
    CreateEmployeeCommand,
    CreateEmployeeCommandHandler,
    DeleteEmployeeCommand,
    DeleteEmployeeCommandHandler,
    UpdateEmployeeCommand,
    UpdateEmployeeCommandHandler,
)
from application.mediator.behaviors import (
    CacheBehavior,
    CommandInvalidationBehavior,
    LoggingBehavior,
    TimingBehavior,
)
from application.mediator.mediator import Mediator
from application.queries.employees import (
    GetEmployeeByIdQuery,
    GetEmployeeByIdQueryHandler,
    GetEmployeesQuery,
    GetEmployeesQueryHandler,
)

logger = logging.getLogger(__name__)


def create_mediator(db: Session) -> Mediator:
    """Create and wire a mediator with all command/query handlers."""
    cache_provider = _create_cache_provider()
    invalidation_service = InvalidationService(cache_provider)
    mediator = Mediator(
        behaviors=[
            CacheBehavior(cache_provider),
            LoggingBehavior(),
            TimingBehavior(),
        ],
        command_behaviors=[
            CommandInvalidationBehavior(invalidation_service),
        ],
    )
    read_repo = EmployeesReadRepository(db)
    mediator.register_handler(GetEmployeesQuery, GetEmployeesQueryHandler(read_repo).handle)
    mediator.register_handler(GetEmployeeByIdQuery, GetEmployeeByIdQueryHandler(read_repo).handle)
    mediator.register_handler(CreateEmployeeCommand, CreateEmployeeCommandHandler(db).handle)
    mediator.register_handler(UpdateEmployeeCommand, UpdateEmployeeCommandHandler(db).handle)
    mediator.register_handler(DeleteEmployeeCommand, DeleteEmployeeCommandHandler(db).handle)
    return mediator


def _create_cache_provider() -> CacheBackend:
    """Create Redis cache provider; fall back to in-memory if Redis is unavailable."""
    redis_client = Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        socket_timeout=1.0,
    )
    try:
        redis_client.ping()
    except Exception as exc:  # pragma: no cover - best-effort fallback for dev/test
        logger.warning("Redis not reachable, using in-memory cache. error=%s", exc)
        return CacheProvider()
    return RedisCacheProvider(redis_client)
