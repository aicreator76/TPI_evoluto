from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class OrchestratorEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant: str
    ref_type: str
    ref_id: str
    threshold_days: int
    event_date: date
    status: str

    payload: Any | None = None

    attempts: int = 0
    last_error: str | None = None

    created_at: datetime
    updated_at: datetime


class AckIn(BaseModel):
    status: Literal["pending", "sent", "ack", "error"] = Field(...)
    error: str | None = None
