from __future__ import annotations

from dataclasses import dataclass

from domain.events.base import DomainEvent


@dataclass(frozen=True)
class EmployeeCreated(DomainEvent):
    id: int
    name: str
    lastname: str
    salary: float
    address: str
    in_vacation: bool


@dataclass(frozen=True)
class EmployeeUpdated(DomainEvent):
    id: int
    fields_changed: dict[str, object]


@dataclass(frozen=True)
class EmployeeDeleted(DomainEvent):
    id: int
