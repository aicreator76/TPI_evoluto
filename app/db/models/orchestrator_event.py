from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

from sqlalchemy import Date, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OrchestratorEvent(Base):
    """
    Coda eventi per orchestratore (notifiche scadenze 30/15/1 ecc).

    IDempotenza:
      unique(tenant, ref_type, ref_id, threshold_days, event_date)

    Convenzioni:
      - ref_type: "dpi" | "impianto" | "altro"
      - status:   "pending" | "sent" | "ack" | "error" | "cancelled"
      - event_date: data in cui l'evento deve "scattare" (expiry - soglia)
      - payload_json: JSON string con dettagli (es: expiry_date originale, metadati, ecc.)
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
    )

    STATUS_PENDING = "pending"
    STATUS_SENT = "sent"
    STATUS_ACK = "ack"
    STATUS_ERROR = "error"
    STATUS_CANCELLED = "cancelled"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    tenant: Mapped[str] = mapped_column(String(64), index=True)
    ref_type: Mapped[str] = mapped_column(String(32), index=True)  # dpi | impianto | altro
    ref_id: Mapped[str] = mapped_column(String(64), index=True)

    threshold_days: Mapped[int] = mapped_column(Integer)  # 30/15/1
    event_date: Mapped[date] = mapped_column(Date, index=True)

    status: Mapped[str] = mapped_column(String(16), default=STATUS_PENDING, index=True)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    @property
    def payload(self) -> dict[str, Any] | None:
        """Payload come dict (per API)."""
        if not self.payload_json:
            return None
        try:
            v = json.loads(self.payload_json)
            return v if isinstance(v, dict) else {"value": v}
        except Exception:
            # payload sporco: non rompiamo l'API
            return {"_raw": self.payload_json}

    @payload.setter
    def payload(self, value: dict[str, Any] | None) -> None:
        self.payload_json = None if value is None else json.dumps(value, ensure_ascii=False)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            "OrchestratorEvent("
            f"id={self.id}, tenant={self.tenant!r}, ref_type={self.ref_type!r}, ref_id={self.ref_id!r}, "
            f"threshold_days={self.threshold_days}, event_date={self.event_date}, status={self.status!r})"
        )
