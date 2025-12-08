from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

QueryType = TypeVar("QueryType", bound="IQuery")
ResultType = TypeVar("ResultType")


class IQuery:
    """Marker interface for queries."""

    pass


class IQueryHandler(Generic[QueryType, ResultType], ABC):
    """Interface for query handlers."""

    @abstractmethod
    def handle(self, query: QueryType) -> ResultType:
        """Handle a query instance."""
        raise NotImplementedError
