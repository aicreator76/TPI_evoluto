from __future__ import annotations

import csv
import io
import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.radar_models import RadarEntry
from app.db.session import get_db

router = APIRouter(prefix="/radar", tags=["radar"])


def _base_dir() -> Path:
    env = os.getenv("RADAR_BASE_DIR")
    if env and env.strip():
        return Path(env).expanduser().resolve()
    return Path("data") / "radar"


def _ensure_tree() -> tuple[Path, Path]:
    base = _base_dir()
    imports_dir = base / "imports"
    imports_dir.mkdir(parents=True, exist_ok=True)
    return base, imports_dir


def _pick_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    # priorità: candidates (ordine) -> colonne
    cols = [str(c) for c in df.columns]
    low = [c.strip().lower() for c in cols]
    for k in candidates:
        kk = k.strip().lower()
        for i, lc in enumerate(low):
            if kk and kk in lc:
                return cols[i]
    return None


def _to_date(v: Any) -> date | None:
    if v is None:
        return None
    ts = pd.to_datetime(v, errors="coerce", dayfirst=True)
    if pd.isna(ts):
        return None
    d = ts.date()
    # Excel "0"/celle vuote formattate data -> 1899/1900
    if d.year < 2000:
        return None
    return d


def _status(days_to_expiry: int | None) -> str | None:
    if days_to_expiry is None:
        return None
    if days_to_expiry < 0:
        return "EXPIRED"
    if days_to_expiry <= 30:
        return "DUE"
    return "OK"


def _latest_source(db: Session, tenant: str) -> str | None:
    row = (
        db.query(RadarEntry.source)
        .filter(RadarEntry.tenant == tenant)
        .order_by(desc(RadarEntry.source))
        .first()
    )
    return row[0] if row and row[0] else None


def _detect_header_row(xlsx_path: Path, sheet_name: str | int) -> int:
    # scansione prime 20 righe: prende quella con più keyword
    df = pd.read_excel(xlsx_path, sheet_name=sheet_name, header=None, nrows=20, engine="openpyxl")
    keys = [
        "posizione",
        "data scad",
        "scad",
        "verifica",
        "articolo",
        "marca",
        "model",
        "matric",
        "dpi",
    ]
    best_r = 0
    best_score = -1
    for r in range(min(20, len(df))):
        row = df.iloc[r].tolist()
        score = 0
        for v in row:
            if v is None or (isinstance(v, float) and pd.isna(v)):
                continue
            s = str(v).strip().lower()
            if not s:
                continue
            if any(k in s for k in keys):
                score += 1
        if score > best_score:
            best_score = score
            best_r = r
    return best_r


@router.get("/metrics")
def metrics(tenant: str = Query("default"), db: Session = Depends(get_db)) -> dict[str, Any]:
    total = db.query(RadarEntry).filter(RadarEntry.tenant == tenant).count()
    latest = _latest_source(db, tenant)
    return {"tenant": tenant, "total_rows": total, "latest_source": latest}


@router.post("/import-excel")
async def import_excel(
    file: UploadFile = File(...),
    tenant: str = Query("default"),
    sheet: str | None = Query(None),
    header_row: int | None = Query(None, ge=0, le=50),
    source_id: str | None = Query(None),
    db: Session = Depends(get_db),
) -> JSONResponse:
    _, imports_dir = _ensure_tree()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = Path(file.filename or f"upload_{ts}.xlsx").name
    dest = imports_dir / f"{ts}_{safe_name}"

    raw_bytes = await file.read()
    dest.write_bytes(raw_bytes)

    sheet_name = sheet if sheet else 0
    hr = header_row if header_row is not None else _detect_header_row(dest, sheet_name)

    df = pd.read_excel(dest, sheet_name=sheet_name, header=hr, engine="openpyxl")
    df = df.dropna(how="all")

    # colonne chiave (questa è la tua tabella)
    col_exp = _pick_col(df, ["data scad verifica", "scad verifica", "scaden", "expiry", "valid"])
    col_art = _pick_col(df, ["articolo"])
    col_brand = _pick_col(df, ["marca", "brand"])
    col_model = _pick_col(df, ["model", "modello"])
    col_code = _pick_col(df, ["matric", "cod", "code", "id", "seriale", "articolo", "model"])

    src = source_id.strip() if source_id and source_id.strip() else f"{ts}_{safe_name}"

    # reimport pulito (idempotente su tenant+source)
    db.query(RadarEntry).filter(RadarEntry.tenant == tenant, RadarEntry.source == src).delete(
        synchronize_session=False
    )
    db.commit()

    inserted = 0
    today = date.today()

    for _, r in df.iterrows():
        exp = _to_date(r.get(col_exp) if col_exp else None)
        days = (exp - today).days if exp else None
        st = _status(days)

        code = str(r.get(col_code)).strip() if col_code and r.get(col_code) is not None else None

        # descr: Articolo + Marca + Model (se ci sono)
        parts = []
        for c in [col_art, col_brand, col_model]:
            if c and r.get(c) is not None and not pd.isna(r.get(c)):
                parts.append(str(r.get(c)).strip())
        desc_txt = " ".join([p for p in parts if p]) or None

        entry = RadarEntry(
            tenant=tenant,
            source=src,
            dpi_code=code,
            description=desc_txt,
            expiry_date=exp,
            status=st,
            days_to_expiry=days,
            raw=json.dumps(
                {k: (None if pd.isna(v) else v) for k, v in r.to_dict().items()},
                ensure_ascii=False,
                default=str,
            ),
        )
        db.add(entry)
        inserted += 1

    db.commit()

    return JSONResponse(
        {
            "status": "ok",
            "tenant": tenant,
            "source": src,
            "rows_inserted": inserted,
            "saved_file": str(dest),
            "sheet": sheet_name,
            "header_row_used": hr,
            "detected_columns": {
                "expiry": col_exp,
                "code": col_code,
                "articolo": col_art,
                "marca": col_brand,
                "model": col_model,
            },
        }
    )


@router.get("/scadenze")
def scadenze(
    tenant: str = Query("default"),
    source: str | None = Query(None),
    status: str | None = Query(None),
    days_max: int | None = Query(None),
    limit: int = Query(200, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    src = source or _latest_source(db, tenant)
    if not src:
        return {"tenant": tenant, "source": None, "count": 0, "items": []}

    q = db.query(RadarEntry).filter(RadarEntry.tenant == tenant, RadarEntry.source == src)
    if status:
        q = q.filter(RadarEntry.status == status)
    if days_max is not None:
        q = q.filter(RadarEntry.days_to_expiry <= days_max)

    q = q.order_by(RadarEntry.expiry_date.asc().nulls_last(), RadarEntry.id.asc())
    items = q.limit(limit).all()

    out = [
        {
            "id": it.id,
            "tenant": it.tenant,
            "source": it.source,
            "dpi_code": it.dpi_code,
            "description": it.description,
            "expiry_date": it.expiry_date.isoformat() if it.expiry_date else None,
            "status": it.status,
            "days_to_expiry": it.days_to_expiry,
            "created_at": it.created_at.isoformat() if it.created_at else None,
        }
        for it in items
    ]
    return {"tenant": tenant, "source": src, "count": len(out), "items": out}


@router.get("/report.csv", response_class=PlainTextResponse)
def report_csv(
    tenant: str = Query("default"),
    source: str | None = Query(None),
    status: str | None = Query(None),
    days_max: int | None = Query(None),
    db: Session = Depends(get_db),
) -> PlainTextResponse:
    data = scadenze(
        tenant=tenant, source=source, status=status, days_max=days_max, limit=2000, db=db
    )
    items = data.get("items", [])

    buf = io.StringIO()
    fieldnames = [
        "tenant",
        "source",
        "dpi_code",
        "description",
        "expiry_date",
        "status",
        "days_to_expiry",
    ]
    w = csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    for it in items:
        w.writerow({k: it.get(k) for k in fieldnames})

    return PlainTextResponse(buf.getvalue(), media_type="text/csv")
