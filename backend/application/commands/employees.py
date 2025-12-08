from __future__ import annotations

from dataclasses import dataclass

from app import models, schemas
from domain.events.employees import EmployeeCreated, EmployeeDeleted, EmployeeUpdated
from infrastructure.outbox.outbox_repository import OutboxRepository
from sqlalchemy.orm import Session

from application.commands.base import ICommand, ICommandHandler


@dataclass
class CreateEmployeeCommand(ICommand):
    payload: schemas.EmployeeCreate


class CreateEmployeeCommandHandler(ICommandHandler[CreateEmployeeCommand, models.Employee]):
    def __init__(self, db: Session, outbox_repository: OutboxRepository):
        self.db = db
        self.outbox_repository = outbox_repository

    def handle(self, command: CreateEmployeeCommand) -> models.Employee:
        db_employee = models.Employee(**command.payload.dict())
        self.db.add(db_employee)
        self.db.flush()

        event = EmployeeCreated(
            id=db_employee.id,
            name=db_employee.name,
            lastname=db_employee.lastname,
            salary=db_employee.salary,
            address=db_employee.address,
            in_vacation=db_employee.in_vacation,
        )
        self.outbox_repository.add_event(event)
        self.db.commit()
        self.db.refresh(db_employee)
        return db_employee


@dataclass
class UpdateEmployeeCommand(ICommand):
    employee_id: int
    payload: schemas.EmployeeUpdate


class UpdateEmployeeCommandHandler(ICommandHandler[UpdateEmployeeCommand, models.Employee | None]):
    def __init__(self, db: Session, outbox_repository: OutboxRepository):
        self.db = db
        self.outbox_repository = outbox_repository

    def handle(self, command: UpdateEmployeeCommand) -> models.Employee | None:
        employee = (
            self.db.query(models.Employee).filter(models.Employee.id == command.employee_id).first()
        )
        if not employee:
            return None

        payload = command.payload.dict()
        fields_changed: dict[str, object] = {}
        for field, value in payload.items():
            if getattr(employee, field) != value:
                fields_changed[field] = value
                setattr(employee, field, value)

        if fields_changed:
            event = EmployeeUpdated(id=employee.id, fields_changed=fields_changed)
            self.outbox_repository.add_event(event)

        self.db.commit()
        self.db.refresh(employee)
        return employee


@dataclass
class DeleteEmployeeCommand(ICommand):
    employee_id: int


class DeleteEmployeeCommandHandler(ICommandHandler[DeleteEmployeeCommand, models.Employee | None]):
    def __init__(self, db: Session, outbox_repository: OutboxRepository):
        self.db = db
        self.outbox_repository = outbox_repository

    def handle(self, command: DeleteEmployeeCommand) -> models.Employee | None:
        employee = (
            self.db.query(models.Employee).filter(models.Employee.id == command.employee_id).first()
        )
        if not employee:
            return None

        self.db.delete(employee)
        event = EmployeeDeleted(id=employee.id)
        self.outbox_repository.add_event(event)
        self.db.commit()
        return employee
