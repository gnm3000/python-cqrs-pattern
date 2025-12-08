from __future__ import annotations

from collections.abc import Sequence

from application.read_models.employees import EmployeeListDTO, map_to_employee_dto
from sqlalchemy import text
from sqlalchemy.engine import RowMapping
from sqlalchemy.orm import Session


class EmployeesReadRepository:
    """Read-only access optimized for queries so handlers avoid the write-side repo."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[EmployeeListDTO]:
        """Return lightweight employees for listings using tuned SQL instead of ORM."""
        result = self.db.execute(
            text(
                """
                SELECT id, name, lastname, salary, address, in_vacation
                FROM employees
                ORDER BY id
                """
            )
        )
        rows: Sequence[RowMapping] = result.mappings().all()
        return [map_to_employee_dto(row) for row in rows]

    def get_by_id(self, employee_id: int) -> EmployeeListDTO | None:
        """Return a single employee DTO or None; mirrors the API payload shape."""
        result = self.db.execute(
            text(
                """
                SELECT id, name, lastname, salary, address, in_vacation
                FROM employees
                WHERE id = :employee_id
                """
            ),
            {"employee_id": employee_id},
        )
        employee: RowMapping | None = result.mappings().first()
        if not employee:
            return None
        return map_to_employee_dto(employee)
