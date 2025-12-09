from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypedDict

from sqlalchemy.engine import RowMapping


class EmployeeListDTO(TypedDict):
    """Lean, serializable DTO used for read-side responses and caching."""

    id: int
    name: str
    lastname: str
    salary: float
    address: str
    in_vacation: bool


def map_to_employee_dto(row: Mapping[str, Any] | RowMapping | Any) -> EmployeeListDTO:
    """Map a row or ORM object to the lean DTO without leaking domain entities."""

    def _get(key: str) -> Any:
        if isinstance(row, Mapping):
            return row[key]
        return getattr(row, key)

    return EmployeeListDTO(
        id=int(_get("id")),
        name=str(_get("name")),
        lastname=str(_get("lastname")),
        salary=float(_get("salary")),
        address=str(_get("address")),
        in_vacation=bool(_get("in_vacation")),
    )
