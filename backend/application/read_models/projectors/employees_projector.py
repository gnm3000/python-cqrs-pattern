from __future__ import annotations

from domain.events.employees import EmployeeCreated, EmployeeDeleted, EmployeeUpdated
from infrastructure.read_repository.employees_read_repository import EmployeesReadRepository


class EmployeesProjector:
    """Update the read model in reaction to domain events."""

    def __init__(self, read_repo: EmployeesReadRepository):
        self.read_repo = read_repo

    def project_created(self, event: EmployeeCreated) -> None:
        self.read_repo.upsert_employee(
            employee_id=event.id,
            name=event.name,
            lastname=event.lastname,
            salary=event.salary,
            address=event.address,
            in_vacation=event.in_vacation,
        )

    def project_updated(self, event: EmployeeUpdated) -> None:
        self.read_repo.apply_updates(event.id, event.fields_changed)

    def project_deleted(self, event: EmployeeDeleted) -> None:
        self.read_repo.delete_employee(event.id)
