from __future__ import annotations

from collections.abc import Callable
from typing import Any

from application.commands.base import ICommand
from application.mediator.behaviors import CommandBehavior, QueryBehavior
from application.queries.base import IQuery


class Mediator:
    """Minimal mediator that routes commands and queries to their handlers."""

    def __init__(
        self,
        behaviors: list[QueryBehavior] | None = None,
        command_behaviors: list[CommandBehavior] | None = None,
    ) -> None:
        self._query_handlers: dict[type[Any], Callable[[Any], Any]] = {}
        self._command_handlers: dict[type[Any], Callable[[Any], Any]] = {}
        self._behaviors = behaviors or []
        self._command_behaviors = command_behaviors or []

    def register_handler(self, message_type: type[Any], handler: Callable[[Any], Any]) -> None:
        if issubclass(message_type, IQuery):
            self._query_handlers[message_type] = handler
            return
        if issubclass(message_type, ICommand):
            self._command_handlers[message_type] = handler
            return
        raise ValueError(f"Unknown message type {message_type}")

    def send(self, message: Any) -> Any:
        if isinstance(message, IQuery):
            return self._send_query(message)
        if isinstance(message, ICommand):
            return self._send_command(message)
        raise ValueError(f"Unsupported message type {type(message).__name__}")

    def _send_command(self, command: ICommand) -> Any:
        handler = self._command_handlers.get(type(command))
        if handler is None:
            raise ValueError(f"No handler registered for {type(command).__name__}")

        def execute_pipeline(index: int, current_command: ICommand) -> Any:
            if index >= len(self._command_behaviors):
                return handler(current_command)
            behavior = self._command_behaviors[index]
            return behavior.handle(current_command, lambda c: execute_pipeline(index + 1, c))

        return execute_pipeline(0, command)

    def _send_query(self, query: IQuery) -> Any:
        handler = self._query_handlers.get(type(query))
        if handler is None:
            raise ValueError(f"No handler registered for {type(query).__name__}")

        def execute_pipeline(index: int, current_query: IQuery) -> Any:
            if index >= len(self._behaviors):
                return handler(current_query)
            behavior = self._behaviors[index]
            return behavior.handle(current_query, lambda q: execute_pipeline(index + 1, q))

        return execute_pipeline(0, query)
