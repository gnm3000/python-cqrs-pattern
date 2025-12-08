from __future__ import annotations

import json
from datetime import UTC, datetime

from app.database import Base
from domain.events.base import DomainEvent
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.orm import Session


class OutboxRecord(Base):
    __tablename__ = "outbox_events"

    id = Column(String(36), primary_key=True)
    event_type = Column(String(150), nullable=False)
    payload = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    processed_at = Column(DateTime, nullable=True)


class OutboxRepository:
    """Persist domain events inside the write transaction for guaranteed delivery."""

    def __init__(self, db: Session):
        self.db: Session = db

    def add_event(self, event: DomainEvent) -> None:
        record = OutboxRecord(
            id=str(event.event_id),
            event_type=event.event_type,
            payload=json.dumps(event.serialize()),
        )
        self.db.add(record)

    def get_unprocessed_events(self, limit: int = 50) -> list[OutboxRecord]:
        return (
            self.db.query(OutboxRecord)
            .filter(OutboxRecord.processed_at.is_(None))
            .order_by(OutboxRecord.created_at)
            .limit(limit)
            .all()
        )

    def mark_as_processed(self, record: OutboxRecord) -> None:
        record.processed_at = datetime.now(UTC)

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
