from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Base class for immutable domain events."""

    event_id: UUID = field(default_factory=uuid4)
    occurred_on: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def event_type(self) -> str:
        return type(self).__name__

    def serialize(self) -> dict[str, Any]:
        """Return a JSON-serializable payload to persist in the outbox."""
        payload = asdict(self)
        payload["event_id"] = str(self.event_id)
        payload["occurred_on"] = self.occurred_on.isoformat()
        return payload

    @classmethod
    def deserialize(cls, payload: dict[str, Any]) -> DomainEvent:
        """Rebuild an event from a serialized payload."""
        data = payload.copy()
        if "event_id" in data:
            data["event_id"] = UUID(str(data["event_id"]))
        if "occurred_on" in data:
            data["occurred_on"] = datetime.fromisoformat(str(data["occurred_on"]))
        return cls(**data)  # type: ignore[arg-type]
