from __future__ import annotations

from collections.abc import Callable
from typing import Any


class Mediator:
    """Minimal mediator that routes commands and queries to their handlers."""

    def __init__(self) -> None:
        self._handlers: dict[type[Any], Callable[[Any], Any]] = {}

    def register_handler(self, message_type: type[Any], handler: Callable[[Any], Any]) -> None:
        self._handlers[message_type] = handler

    def send(self, message: Any) -> Any:
        handler = self._handlers.get(type(message))
        if handler is None:
            raise ValueError(f"No handler registered for {type(message).__name__}")
        return handler(message)
