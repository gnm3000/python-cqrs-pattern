from __future__ import annotations

from sqlalchemy.orm import Session

from application.commands.employees import (
    CreateEmployeeCommand,
    CreateEmployeeCommandHandler,
    DeleteEmployeeCommand,
    DeleteEmployeeCommandHandler,
    UpdateEmployeeCommand,
    UpdateEmployeeCommandHandler,
)
from application.mediator.mediator import Mediator
from application.queries.employees import (
    GetEmployeeByIdQuery,
    GetEmployeeByIdQueryHandler,
    GetEmployeesQuery,
    GetEmployeesQueryHandler,
)


def create_mediator(db: Session) -> Mediator:
    """Create and wire a mediator with all command/query handlers."""
    mediator = Mediator()
    mediator.register_handler(GetEmployeesQuery, GetEmployeesQueryHandler(db).handle)
    mediator.register_handler(GetEmployeeByIdQuery, GetEmployeeByIdQueryHandler(db).handle)
    mediator.register_handler(CreateEmployeeCommand, CreateEmployeeCommandHandler(db).handle)
    mediator.register_handler(UpdateEmployeeCommand, UpdateEmployeeCommandHandler(db).handle)
    mediator.register_handler(DeleteEmployeeCommand, DeleteEmployeeCommandHandler(db).handle)
    return mediator
