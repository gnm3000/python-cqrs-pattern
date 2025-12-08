from __future__ import annotations

from typing import Iterable

from application.commands.employees import (
    CreateEmployeeCommand,
    DeleteEmployeeCommand,
    UpdateEmployeeCommand,
)
from application.read_models.ttl_config import EMPLOYEE_LIST_CACHE_KEY, employee_detail_cache_key
from infrastructure.cache.cache_provider import CacheBackend


class InvalidationService:
    """Centralized cache invalidation keyed by Command type."""

    def __init__(self, cache: CacheBackend):
        self.cache = cache

    def invalidate_for(self, command: object) -> None:
        for key in self._keys_for(command):
            self.cache.delete(key)

    def _keys_for(self, command: object) -> Iterable[str]:
        if isinstance(command, CreateEmployeeCommand):
            yield EMPLOYEE_LIST_CACHE_KEY
        elif isinstance(command, UpdateEmployeeCommand):
            yield EMPLOYEE_LIST_CACHE_KEY
            yield employee_detail_cache_key(command.employee_id)
        elif isinstance(command, DeleteEmployeeCommand):
            yield EMPLOYEE_LIST_CACHE_KEY
            yield employee_detail_cache_key(command.employee_id)
