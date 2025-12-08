from __future__ import annotations

import json
import logging
from collections.abc import Callable, Mapping

from domain.events.base import DomainEvent
from domain.events.employees import EmployeeCreated, EmployeeDeleted, EmployeeUpdated

from infrastructure.outbox.outbox_repository import OutboxRecord, OutboxRepository

EventHandler = Callable[[DomainEvent], None]
EVENT_CLASS_REGISTRY: Mapping[str, type[DomainEvent]] = {
    EmployeeCreated.__name__: EmployeeCreated,
    EmployeeUpdated.__name__: EmployeeUpdated,
    EmployeeDeleted.__name__: EmployeeDeleted,
}


class OutboxProcessor:
    """Pull pending events from the outbox and fan them out to projectors."""

    def __init__(
        self,
        repository: OutboxRepository,
        handlers: Mapping[str, EventHandler],
        logger: logging.Logger | None = None,
    ):
        self.repository = repository
        self.handlers = handlers
        self.logger = logger or logging.getLogger("outbox.processor")

    def process_pending_events(self, limit: int = 50) -> None:
        pending = self.repository.get_unprocessed_events(limit)
        if not pending:
            return

        self.logger.info("outbox_batch size=%s", len(pending))
        for record in pending:
            event = self._deserialize_event(record)
            if not event:
                self.repository.mark_as_processed(record)
                self.repository.commit()
                continue

            handler = self.handlers.get(record.event_type)
            if not handler:
                self.logger.warning("No projector registered for event_type=%s", record.event_type)
                self.repository.mark_as_processed(record)
                self.repository.commit()
                continue

            try:
                handler(event)
                self.repository.mark_as_processed(record)
                self.repository.commit()
                self.logger.info("outbox_processed event_type=%s event_id=%s", record.event_type, record.id)
            except Exception as exc:  # pragma: no cover - defensive guardrail
                self.repository.rollback()
                self.logger.error(
                    "Failed to project event_id=%s type=%s error=%s",
                    record.id,
                    record.event_type,
                    exc,
                )

    def _deserialize_event(self, record: OutboxRecord) -> DomainEvent | None:
        event_class = EVENT_CLASS_REGISTRY.get(record.event_type)
        if not event_class:
            self.logger.error("Unknown event_type=%s payload=%s", record.event_type, record.payload)
            return None

        try:
            payload = json.loads(record.payload)
        except json.JSONDecodeError as exc:
            self.logger.error("Failed to decode payload for event_id=%s error=%s", record.id, exc)
            return None

        try:
            return event_class.deserialize(payload)
        except Exception as exc:  # pragma: no cover - defensive guardrail
            self.logger.error(
                "Failed to deserialize event type=%s error=%s payload=%s",
                record.event_type,
                exc,
                payload,
            )
            return None
