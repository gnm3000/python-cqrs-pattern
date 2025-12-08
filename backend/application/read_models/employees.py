from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class EmployeeRow(Protocol):
    id: int
    name: str
    lastname: str
    salary: float
    address: str
    in_vacation: bool


@dataclass(frozen=True)
class EmployeeListDTO:
    """Flattened read model returned to the API for employee list/detail queries."""

    id: int
    name: str
    lastname: str
    salary: float
    address: str
    in_vacation: bool


def map_to_employee_dto(row: EmployeeRow) -> EmployeeListDTO:
    """Map a lightweight ORM row to the read-side DTO without leaking domain entities."""
    return EmployeeListDTO(
        id=row.id,
        name=row.name,
        lastname=row.lastname,
        salary=row.salary,
        address=row.address,
        in_vacation=row.in_vacation,
    )
