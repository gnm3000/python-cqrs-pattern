from __future__ import annotations

from dataclasses import dataclass

from app import crud, models
from sqlalchemy.orm import Session

from application.queries.base import IQuery, IQueryHandler


@dataclass
class GetEmployeesQuery(IQuery):
    pass


class GetEmployeesQueryHandler(IQueryHandler[GetEmployeesQuery, list[models.Employee]]):
    def __init__(self, db: Session):
        self.db = db

    def handle(self, query: GetEmployeesQuery) -> list[models.Employee]:
        return crud.get_employees(self.db)


@dataclass
class GetEmployeeByIdQuery(IQuery):
    employee_id: int


class GetEmployeeByIdQueryHandler(IQueryHandler[GetEmployeeByIdQuery, models.Employee | None]):
    def __init__(self, db: Session):
        self.db = db

    def handle(self, query: GetEmployeeByIdQuery) -> models.Employee | None:
        return crud.get_employee(self.db, query.employee_id)
