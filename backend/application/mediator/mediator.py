from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

MessageType = TypeVar("MessageType")
ResultType = TypeVar("ResultType")


class Mediator:
    """Minimal mediator that routes commands and queries to their handlers."""

    def __init__(self) -> None:
        self._handlers: dict[type[Any], Callable[[Any], Any]] = {}

    def register_handler(
        self, message_type: type[MessageType], handler: Callable[[MessageType], ResultType]
    ) -> None:
        self._handlers[message_type] = handler

    def send(self, message: MessageType) -> ResultType:
        handler = self._handlers.get(type(message))
        if handler is None:
            raise ValueError(f"No handler registered for {type(message).__name__}")
        return handler(message)
