from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from sqlalchemy.orm import Session

from app.db.session import db_session, init_db
from app.orchestrator.job import generate, read_csv


@dataclass(frozen=True)
class RunRequest:
    dpi_csv: str | None = None
    impianti_csv: str | None = None
    horizon_days: int = 31
    backfill_days: int = 2
    thresholds: Sequence[int] = field(default_factory=lambda: (30, 15, 1))
    dry_run: bool = False
    init_db_flag: bool = False


def run_orchestrator(req: RunRequest, *, db: Session | None = None) -> dict[str, int]:
    """
    Vendibile:
    - opzionale riuso sessione DB (API /run può passare db=db)
    - thresholds Sequence -> no guerra tuple/list
    """
    if req.init_db_flag:
        init_db()

    rows = []
    if req.dpi_csv:
        rows.extend(list(read_csv(Path(req.dpi_csv), "dpi")))
    if req.impianti_csv:
        rows.extend(list(read_csv(Path(req.impianti_csv), "impianto")))

    if not rows:
        return {"created": 0, "skipped_existing": 0, "invalid": 0, "candidates": 0}

    thresholds = list(req.thresholds)

    if db is not None:
        return generate(
            db=db,
            items=rows,
            thresholds=thresholds,
            horizon_days=req.horizon_days,
            backfill_days=req.backfill_days,
            dry_run=req.dry_run,
        )

    with db_session() as s:
        return generate(
            db=s,
            items=rows,
            thresholds=thresholds,
            horizon_days=req.horizon_days,
            backfill_days=req.backfill_days,
            dry_run=req.dry_run,
        )
