from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OrchestratorEvent(Base):
    """
    Coda eventi per orchestratore (notifiche scadenze 30/15/1 ecc).
    Idempotente via unique constraint su (tenant, ref_type, ref_id, threshold_days, event_date).
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    tenant: Mapped[str] = mapped_column(String(64), index=True)
    ref_type: Mapped[str] = mapped_column(String(32), index=True)  # dpi | impianto | altro
    ref_id: Mapped[str] = mapped_column(String(64), index=True)

    threshold_days: Mapped[int] = mapped_column(Integer)  # 30/15/1
    event_date: Mapped[date] = mapped_column(Date, index=True)

    status: Mapped[str] = mapped_column(
        String(16), default="pending", index=True
    )  # pending/sent/ack
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
