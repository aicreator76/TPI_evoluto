from __future__ import annotations

from datetime import datetime, timezone
from typing import ClassVar

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OrchestratorLock(Base):
    """
    Lease lock DB (anti doppia run).

    - name: chiave lock (es. orchestrator0)
    - locked_until: scadenza lease (UTC)
    - owner: chi ha preso il lock
    - token: segreto per release sicura
    """

    __tablename__ = "orchestrator_locks"

    DEFAULT_NAME: ClassVar[str] = "orchestrator0"

    name: Mapped[str] = mapped_column(String(64), primary_key=True)

    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    owner: Mapped[str | None] = mapped_column(String(128), nullable=True)

    token: Mapped[str | None] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (Index("ix_orch_lock_until", "locked_until"),)
