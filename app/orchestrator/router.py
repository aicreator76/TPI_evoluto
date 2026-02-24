from __future__ import annotations

import os
import socket
from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.orchestrator_models.orchestrator_event import OrchestratorEvent
from app.db.session import get_db, init_db
from app.orchestrator.lock_service import acquire_lock, lock_status, release_lock
from app.orchestrator.schemas import AckIn, OrchestratorEventOut
from app.orchestrator.service import RunRequest, run_orchestrator

router: APIRouter = APIRouter(tags=["orchestrator"])


@router.get("/events", response_model=list[OrchestratorEventOut], summary="List Events")
def list_events(
    tenant: Annotated[str, Query(min_length=1, max_length=64)],
    status_filter: Annotated[str | None, Query(alias="status")] = OrchestratorEvent.STATUS_PENDING,
    due_before: Annotated[date | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 200,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
) -> list[OrchestratorEvent]:
    stmt = select(OrchestratorEvent).where(OrchestratorEvent.tenant == tenant)

    if status_filter:
        stmt = stmt.where(OrchestratorEvent.status == status_filter)

    if due_before:
        stmt = stmt.where(OrchestratorEvent.event_date <= due_before)

    stmt = (
        stmt.order_by(OrchestratorEvent.event_date.asc(), OrchestratorEvent.id.asc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())


@router.post("/events/{event_id}/ack", response_model=OrchestratorEventOut, summary="Ack Event")
def ack_event(event_id: int, body: AckIn, db: Session = Depends(get_db)) -> OrchestratorEvent:
    ev = db.get(OrchestratorEvent, event_id)
    if ev is None:
        raise HTTPException(status_code=404, detail="event_not_found")

    ev.status = body.status
    try:
        db.add(ev)
        db.commit()
        db.refresh(ev)
        return ev
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"db_error:{type(e).__name__}") from e


class LockAcquireIn(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    ttl_seconds: int = Field(default=600, ge=1, le=86400)
    owner: str | None = None


class LockReleaseIn(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    token: str = Field(min_length=8, max_length=128)


@router.get("/lock", summary="Lock Status")
def get_lock_status(
    name: Annotated[str, Query(min_length=1, max_length=64)] = "orchestrator0",
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    st = lock_status(db, name)
    return {
        "ok": True,
        "lock": {
            "name": st.name,
            "exists": st.exists,
            "locked": st.locked,
            "owner": st.owner,
            "locked_until": st.locked_until.isoformat() if st.locked_until else None,
        },
    }


@router.post("/lock/acquire", summary="Acquire Lock")
def lock_acquire(body: LockAcquireIn, db: Session = Depends(get_db)) -> dict[str, Any]:
    owner = (body.owner or os.getenv("ORCH_OWNER") or socket.gethostname() or "Camelot").strip()
    ok, st = acquire_lock(db, name=body.name, ttl_seconds=body.ttl_seconds, owner=owner)

    if not ok:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "ok": False,
                "reason": "locked",
                "name": st.name,
                "owner": st.owner,
                "locked_until": st.locked_until.isoformat() if st.locked_until else None,
            },
        )

    return {
        "ok": True,
        "lock": {
            "name": st.name,
            "owner": st.owner,
            "token": st.token,
            "locked_until": st.locked_until.isoformat() if st.locked_until else None,
        },
    }


@router.post("/lock/release", summary="Release Lock")
def lock_release(body: LockReleaseIn, db: Session = Depends(get_db)) -> dict[str, Any]:
    ok = release_lock(db, name=body.name, token=body.token)
    if not ok:
        raise HTTPException(status_code=403, detail="forbidden_or_bad_token")
    return {"ok": True}


class RunBody(BaseModel):
    dpi_csv: str | None = None
    impianti_csv: str | None = None
    horizon_days: int = 31
    backfill_days: int = 2
    thresholds: list[int] = Field(default_factory=lambda: [30, 15, 1])
    dry_run: bool = False
    init_db: bool = False
    lock_name: str = "orchestrator0"
    lock_ttl_seconds: int = 900
    owner: str | None = None


@router.post("/run", summary="Run Orchestrator (admin)")
def run(
    body: RunBody,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    expected = os.getenv("ORCH_API_KEY", "").strip()
    if expected and (x_api_key or "").strip() != expected:
        raise HTTPException(status_code=403, detail="forbidden")

    if body.init_db:
        init_db()

    owner = (body.owner or os.getenv("ORCH_OWNER") or socket.gethostname() or "Camelot").strip()

    token: str | None = None
    try:
        ok, st = acquire_lock(
            db, name=body.lock_name, ttl_seconds=body.lock_ttl_seconds, owner=owner
        )
        if not ok:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="locked")

        token = st.token
        # mypy-safe: dopo acquire token deve esserci
        if token is None:
            raise HTTPException(status_code=500, detail="lock_token_missing")

        summary = run_orchestrator(
            RunRequest(
                dpi_csv=body.dpi_csv,
                impianti_csv=body.impianti_csv,
                horizon_days=body.horizon_days,
                backfill_days=body.backfill_days,
                thresholds=body.thresholds,
                dry_run=body.dry_run,
                init_db_flag=body.init_db,
            ),
            db=db,
        )
        return {"ok": True, "summary": summary}

    except HTTPException:
        # giÃ  formattata
        raise
    except Exception as e:
        db.rollback()
        if os.getenv("ORCH_DEBUG_ERRORS", "").strip() == "1":
            raise HTTPException(status_code=500, detail=f"run_error:{type(e).__name__}:{e}") from e
        raise HTTPException(status_code=500, detail="internal_server_error") from e
    finally:
        if token is not None:
            try:
                release_lock(db, name=body.lock_name, token=token)
            except Exception:
                db.rollback()
