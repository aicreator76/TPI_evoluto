from __future__ import annotations

import json
from datetime import date, datetime, timezone
from typing import Any, ClassVar

from sqlalchemy import Date, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OrchestratorEvent(Base):
    """
    Coda eventi orchestratore (notifiche scadenze 30/15/1 ecc).

    Idempotenza: unique su (tenant, ref_type, ref_id, threshold_days, event_date).

    payload_json resta TEXT per compatibilità SQLite/Postgres senza migrazioni immediate.
    """

    __tablename__ = "orchestrator_events"
    __table_args__ = (
        UniqueConstraint(
            "tenant",
            "ref_type",
            "ref_id",
            "threshold_days",
            "event_date",
            name="uq_orchestrator_event",
        ),
        Index("ix_orch_tenant_status_date", "tenant", "status", "event_date"),
        Index("ix_orch_ref", "tenant", "ref_type", "ref_id"),
    )

    # Status canonici (job/router/n8n)
    STATUS_PENDING: ClassVar[str] = "pending"
    STATUS_SENT: ClassVar[str] = "sent"
    STATUS_ACK: ClassVar[str] = "ack"
    STATUS_ERROR: ClassVar[str] = "error"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    tenant: Mapped[str] = mapped_column(String(64), index=True)
    ref_type: Mapped[str] = mapped_column(String(32), index=True)  # dpi | impianto | altro
    ref_id: Mapped[str] = mapped_column(String(64), index=True)

    threshold_days: Mapped[int] = mapped_column(Integer)  # 30/15/1
    event_date: Mapped[date] = mapped_column(Date, index=True)

    status: Mapped[str] = mapped_column(String(16), default=STATUS_PENDING, index=True)

    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # --- payload API (compat: job.py usa .payload) ---
    @property
    def payload(self) -> Any:
        return self.get_payload()

    @payload.setter
    def payload(self, value: dict[str, Any] | list[Any] | None) -> None:
        self.set_payload(value)

    def set_payload(self, payload: dict[str, Any] | list[Any] | None) -> None:
        self.payload_json = None if payload is None else json.dumps(payload, ensure_ascii=False)

    def get_payload(self) -> Any:
        if not self.payload_json:
            return None
        try:
            return json.loads(self.payload_json)
        except Exception:
            return self.payload_json  # fallback grezzo

    def mark_sent(self) -> None:
        self.status = self.STATUS_SENT

    def mark_ack(self) -> None:
        self.status = self.STATUS_ACK

    def mark_error(self, message: str) -> None:
        self.status = self.STATUS_ERROR
        self.last_error = message
        self.attempts += 1

    def __repr__(self) -> str:
        return (
            "OrchestratorEvent("
            f"id={self.id}, tenant={self.tenant}, ref={self.ref_type}:{self.ref_id}, "
            f"th={self.threshold_days}, date={self.event_date}, status={self.status}"
            ")"
        )
