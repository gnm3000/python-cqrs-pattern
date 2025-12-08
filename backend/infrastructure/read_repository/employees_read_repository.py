from __future__ import annotations

from app.models import ReadEmployee
from application.read_models.employees import EmployeeListDTO, map_to_employee_dto
from sqlalchemy.orm import Session


class EmployeesReadRepository:
    """Read-model access so queries stay decoupled and projectors can update the view."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[EmployeeListDTO]:
        """Return lightweight employees for listings using the read-model table."""
        employees = self.db.query(ReadEmployee).order_by(ReadEmployee.id).all()
        return [map_to_employee_dto(employee) for employee in employees]

    def get_by_id(self, employee_id: int) -> EmployeeListDTO | None:
        """Return a single employee DTO or None; mirrors the API payload shape."""
        employee = self.db.query(ReadEmployee).filter(ReadEmployee.id == employee_id).first()
        if not employee:
            return None
        return map_to_employee_dto(employee)

    def upsert_employee(
        self,
        employee_id: int,
        name: str,
        lastname: str,
        salary: float,
        address: str,
        in_vacation: bool,
    ) -> None:
        """Insert or update a row in the read model."""
        employee = self.db.query(ReadEmployee).filter(ReadEmployee.id == employee_id).first()
        if not employee:
            employee = ReadEmployee(
                id=employee_id,
                name=name,
                lastname=lastname,
                salary=salary,
                address=address,
                in_vacation=in_vacation,
            )
            self.db.add(employee)
            return

        employee.name = name
        employee.lastname = lastname
        employee.salary = salary
        employee.address = address
        employee.in_vacation = in_vacation

    def apply_updates(self, employee_id: int, fields_changed: dict[str, object]) -> None:
        """Patch only the fields provided by the event."""
        employee = self.db.query(ReadEmployee).filter(ReadEmployee.id == employee_id).first()
        if not employee:
            return

        allowed_fields = {"name", "lastname", "salary", "address", "in_vacation"}
        for field, value in fields_changed.items():
            if field in allowed_fields:
                setattr(employee, field, value)

    def delete_employee(self, employee_id: int) -> None:
        employee = self.db.query(ReadEmployee).filter(ReadEmployee.id == employee_id).first()
        if not employee:
            return
        self.db.delete(employee)
