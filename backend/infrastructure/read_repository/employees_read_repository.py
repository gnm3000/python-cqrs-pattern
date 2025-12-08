from __future__ import annotations

from typing import Any, cast

from app import models
from application.read_models.employees import EmployeeListDTO, map_to_employee_dto
from sqlalchemy.orm import Session, load_only
from sqlalchemy.orm.attributes import QueryableAttribute


class EmployeesReadRepository:
    """Read-only access optimized for queries so handlers avoid the write-side repo."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[EmployeeListDTO]:
        """Return lightweight employees for listings without materializing full entities."""
        employees = (
            self.db.query(models.Employee)
            .options(
                load_only(
                    cast(QueryableAttribute[Any], models.Employee.id),
                    cast(QueryableAttribute[Any], models.Employee.name),
                    cast(QueryableAttribute[Any], models.Employee.lastname),
                    cast(QueryableAttribute[Any], models.Employee.salary),
                    cast(QueryableAttribute[Any], models.Employee.address),
                    cast(QueryableAttribute[Any], models.Employee.in_vacation),
                )
            )
            .order_by(models.Employee.id)
            .all()
        )
        return [map_to_employee_dto(employee) for employee in employees]

    def get_by_id(self, employee_id: int) -> EmployeeListDTO | None:
        """Return a single employee DTO or None; mirrors the API payload shape."""
        employee = (
            self.db.query(models.Employee)
            .options(
                load_only(
                    cast(QueryableAttribute[Any], models.Employee.id),
                    cast(QueryableAttribute[Any], models.Employee.name),
                    cast(QueryableAttribute[Any], models.Employee.lastname),
                    cast(QueryableAttribute[Any], models.Employee.salary),
                    cast(QueryableAttribute[Any], models.Employee.address),
                    cast(QueryableAttribute[Any], models.Employee.in_vacation),
                )
            )
            .filter(models.Employee.id == employee_id)
            .first()
        )
        if not employee:
            return None
        return map_to_employee_dto(employee)
