from __future__ import annotations

import logging

from config import REDIS_DB, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from domain.events.invalidation_service import InvalidationService
from infrastructure.cache.cache_provider import CacheBackend, CacheProvider
from infrastructure.cache.redis_cache_provider import RedisCacheProvider
from infrastructure.outbox.outbox_processor import OutboxProcessor
from infrastructure.outbox.outbox_repository import OutboxRepository
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
    CommandLoggingBehavior,
    LoggingBehavior,
    OutboxDispatchBehavior,
    TimingBehavior,
)
from application.mediator.mediator import Mediator
from application.queries.employees import (
    GetEmployeeByIdQuery,
    GetEmployeeByIdQueryHandler,
    GetEmployeesQuery,
    GetEmployeesQueryHandler,
)
from application.read_models.projectors.employees_projector import EmployeesProjector

logger = logging.getLogger(__name__)


def create_mediator(db: Session) -> Mediator:
    """Create and wire a mediator with all command/query handlers."""
    cache_provider = _create_cache_provider()
    invalidation_service = InvalidationService(cache_provider)
    read_repo = EmployeesReadRepository(db)
    projector = EmployeesProjector(read_repo)
    outbox_repository = OutboxRepository(db)
    outbox_processor = OutboxProcessor(
        outbox_repository,
        {
            "EmployeeCreated": projector.project_created,
            "EmployeeUpdated": projector.project_updated,
            "EmployeeDeleted": projector.project_deleted,
        },
    )
    mediator = Mediator(
        behaviors=[
            CacheBehavior(cache_provider),
            LoggingBehavior(),
            TimingBehavior(),
        ],
        command_behaviors=[
            CommandLoggingBehavior(),
            CommandInvalidationBehavior(invalidation_service),
            OutboxDispatchBehavior(outbox_processor),
        ],
    )
    mediator.register_handler(GetEmployeesQuery, GetEmployeesQueryHandler(read_repo).handle)
    mediator.register_handler(GetEmployeeByIdQuery, GetEmployeeByIdQueryHandler(read_repo).handle)
    mediator.register_handler(
        CreateEmployeeCommand, CreateEmployeeCommandHandler(db, outbox_repository).handle
    )
    mediator.register_handler(
        UpdateEmployeeCommand, UpdateEmployeeCommandHandler(db, outbox_repository).handle
    )
    mediator.register_handler(
        DeleteEmployeeCommand, DeleteEmployeeCommandHandler(db, outbox_repository).handle
    )
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
