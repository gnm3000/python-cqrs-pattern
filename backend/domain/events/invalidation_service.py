from __future__ import annotations

import logging
from collections.abc import Iterable

from application.commands.employees import (
    CreateEmployeeCommand,
    DeleteEmployeeCommand,
    UpdateEmployeeCommand,
)
from application.read_models.ttl_config import EMPLOYEE_LIST_CACHE_KEY, employee_detail_cache_key
from infrastructure.cache.cache_provider import CacheBackend


class InvalidationService:
    """Centralized cache invalidation keyed by Command type."""

    def __init__(self, cache: CacheBackend, logger: logging.Logger | None = None):
        self.cache = cache
        self.logger = logger or logging.getLogger("mediator.invalidation")

    def invalidate_for(self, command: object) -> None:
        keys = list(self._keys_for(command))
        for key in keys:
            self.cache.delete(key)
        if keys:
            self.logger.info(
                "cache_invalidate command=%s keys=%s", type(command).__name__, ",".join(keys)
            )

    def _keys_for(self, command: object) -> Iterable[str]:
        if isinstance(command, CreateEmployeeCommand):
            yield EMPLOYEE_LIST_CACHE_KEY
        elif isinstance(command, UpdateEmployeeCommand):
            yield EMPLOYEE_LIST_CACHE_KEY
            yield employee_detail_cache_key(command.employee_id)
        elif isinstance(command, DeleteEmployeeCommand):
            yield EMPLOYEE_LIST_CACHE_KEY
            yield employee_detail_cache_key(command.employee_id)
