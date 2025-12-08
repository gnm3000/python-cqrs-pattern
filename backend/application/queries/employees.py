from __future__ import annotations

from dataclasses import dataclass

from infrastructure.read_repository.employees_read_repository import EmployeesReadRepository

from application.queries.base import IQuery, IQueryHandler
from application.read_models.employees import EmployeeListDTO


@dataclass
class GetEmployeesQuery(IQuery):
    @property
    def cache_key(self) -> str:
        return "employees:list"

    @property
    def cache_ttl_seconds(self) -> int:
        return 5


class GetEmployeesQueryHandler(IQueryHandler[GetEmployeesQuery, list[EmployeeListDTO]]):
    def __init__(self, read_repo: EmployeesReadRepository):
        self.read_repo = read_repo

    def handle(self, query: GetEmployeesQuery) -> list[EmployeeListDTO]:
        # Pull lightweight DTOs instead of domain entities to keep reads decoupled.
        return self.read_repo.get_all()


@dataclass
class GetEmployeeByIdQuery(IQuery):
    employee_id: int

    @property
    def cache_key(self) -> str:
        return f"employees:{self.employee_id}"

    @property
    def cache_ttl_seconds(self) -> int:
        return 5


class GetEmployeeByIdQueryHandler(IQueryHandler[GetEmployeeByIdQuery, EmployeeListDTO | None]):
    def __init__(self, read_repo: EmployeesReadRepository):
        self.read_repo = read_repo

    def handle(self, query: GetEmployeeByIdQuery) -> EmployeeListDTO | None:
        # Read side stays isolated from the write model to enable future optimizations.
        return self.read_repo.get_by_id(query.employee_id)
