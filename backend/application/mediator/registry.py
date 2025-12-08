from __future__ import annotations

from infrastructure.cache.cache_provider import CacheProvider
from infrastructure.read_repository.employees_read_repository import EmployeesReadRepository
from sqlalchemy.orm import Session

from application.commands.employees import (
    CreateEmployeeCommand,
    CreateEmployeeCommandHandler,
    DeleteEmployeeCommand,
    DeleteEmployeeCommandHandler,
    UpdateEmployeeCommand,
    UpdateEmployeeCommandHandler,
)
from application.mediator.behaviors import CacheBehavior, LoggingBehavior, TimingBehavior
from application.mediator.mediator import Mediator
from application.queries.employees import (
    GetEmployeeByIdQuery,
    GetEmployeeByIdQueryHandler,
    GetEmployeesQuery,
    GetEmployeesQueryHandler,
)


def create_mediator(db: Session) -> Mediator:
    """Create and wire a mediator with all command/query handlers."""
    cache_provider = CacheProvider()
    mediator = Mediator(
        behaviors=[
            CacheBehavior(cache_provider),
            LoggingBehavior(),
            TimingBehavior(),
        ]
    )
    read_repo = EmployeesReadRepository(db)
    mediator.register_handler(GetEmployeesQuery, GetEmployeesQueryHandler(read_repo).handle)
    mediator.register_handler(GetEmployeeByIdQuery, GetEmployeeByIdQueryHandler(read_repo).handle)
    mediator.register_handler(CreateEmployeeCommand, CreateEmployeeCommandHandler(db).handle)
    mediator.register_handler(UpdateEmployeeCommand, UpdateEmployeeCommandHandler(db).handle)
    mediator.register_handler(DeleteEmployeeCommand, DeleteEmployeeCommandHandler(db).handle)
    return mediator
