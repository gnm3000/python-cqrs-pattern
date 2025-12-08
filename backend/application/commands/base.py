from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

CommandType = TypeVar("CommandType", bound="ICommand")
ResultType = TypeVar("ResultType")


class ICommand(ABC):
    """Marker interface for commands."""

    pass


class ICommandHandler(Generic[CommandType, ResultType], ABC):
    """Interface for command handlers."""

    @abstractmethod
    def handle(self, command: CommandType) -> ResultType:
        """Handle a command instance."""
        raise NotImplementedError
