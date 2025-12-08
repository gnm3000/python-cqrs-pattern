from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from sqlalchemy.engine import RowMapping


@dataclass(frozen=True)
class EmployeeListDTO:
    """Flattened read model returned to the API for employee list/detail queries."""

    id: int
    name: str
    lastname: str
    salary: float
    address: str
    in_vacation: bool


def map_to_employee_dto(row: Mapping[str, Any] | RowMapping | Any) -> EmployeeListDTO:
    """Map a row or ORM object to the read-side DTO without leaking domain entities."""

    def _get(key: str) -> Any:
        if isinstance(row, Mapping):
            return row[key]
        return getattr(row, key)

    return EmployeeListDTO(
        id=_get("id"),
        name=_get("name"),
        lastname=_get("lastname"),
        salary=_get("salary"),
        address=_get("address"),
        in_vacation=_get("in_vacation"),
    )
