from domain.events.base import DomainEvent
from domain.events.employees import EmployeeCreated, EmployeeDeleted, EmployeeUpdated

__all__ = ["DomainEvent", "EmployeeCreated", "EmployeeDeleted", "EmployeeUpdated"]
