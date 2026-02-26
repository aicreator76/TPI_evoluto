from __future__ import annotations

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Index
from sqlalchemy.sql import func

from app.db.base import Base


class RadarEntry(Base):
    __tablename__ = "radar_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant = Column(String(64), nullable=False, default="default")

    source = Column(String(128), nullable=True)  # es: nome file excel / batch
    dpi_code = Column(String(64), nullable=True)
    description = Column(String(256), nullable=True)

    expiry_date = Column(Date, nullable=True)
    status = Column(String(16), nullable=True)  # OK / DUE / EXPIRED
    days_to_expiry = Column(Integer, nullable=True)

    raw = Column(Text, nullable=True)  # JSON string

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


Index("ix_radar_entries_tenant_expiry", RadarEntry.tenant, RadarEntry.expiry_date)
