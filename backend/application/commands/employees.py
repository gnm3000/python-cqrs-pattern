from __future__ import annotations

from dataclasses import dataclass

from app import crud, models, schemas
from sqlalchemy.orm import Session

from application.commands.base import ICommand, ICommandHandler


@dataclass
class CreateEmployeeCommand(ICommand):
    payload: schemas.EmployeeCreate


class CreateEmployeeCommandHandler(ICommandHandler[CreateEmployeeCommand, models.Employee]):
    def __init__(self, db: Session):
        self.db = db

    def handle(self, command: CreateEmployeeCommand) -> models.Employee:
        return crud.create_employee(self.db, command.payload)


@dataclass
class UpdateEmployeeCommand(ICommand):
    employee_id: int
    payload: schemas.EmployeeUpdate


class UpdateEmployeeCommandHandler(ICommandHandler[UpdateEmployeeCommand, models.Employee | None]):
    def __init__(self, db: Session):
        self.db = db

    def handle(self, command: UpdateEmployeeCommand) -> models.Employee | None:
        return crud.update_employee(self.db, command.employee_id, command.payload)


@dataclass
class DeleteEmployeeCommand(ICommand):
    employee_id: int


class DeleteEmployeeCommandHandler(ICommandHandler[DeleteEmployeeCommand, models.Employee | None]):
    def __init__(self, db: Session):
        self.db = db

    def handle(self, command: DeleteEmployeeCommand) -> models.Employee | None:
        return crud.delete_employee(self.db, command.employee_id)
