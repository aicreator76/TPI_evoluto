from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, UploadFile, File, Body, HTTPException, Query
from fastapi.responses import PlainTextResponse

# === Path & storage ===
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CATALOGHI_DIR = DATA_DIR / "cataloghi"
IMPORTS_DIR = CATALOGHI_DIR / "imports"
for d in (DATA_DIR, CATALOGHI_DIR, IMPORTS_DIR):
    d.mkdir(parents=True, exist_ok=True)

CATALOGO_JSON = DATA_DIR / "dpi_items.json"

# === Router ===
router = APIRouter(prefix="/api/dpi/csv", tags=["csv"])

# === Helpers ===
_ALLOWED_FIELDS = ["codice", "descrizione", "prezzo", "gruppo"]


def _safe_decode(b: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return b.decode(enc)
        except Exception:
            pass
    return b.decode("utf-8", errors="replace")


def _load_json() -> List[Dict[str, str]]:
    if not CATALOGO_JSON.exists():
        return []
    try:
        return json.loads(CATALOGO_JSON.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_json(items: List[Dict[str, str]]) -> None:
    CATALOGO_JSON.write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _normalize_row(row: Dict[str, Any]) -> Dict[str, str]:
    def norm(v: Any) -> str:
        return (str(v) if v is not None else "").strip()

    return {
        "codice": norm(row.get("codice")),
        "descrizione": norm(row.get("descrizione")),
        "prezzo": norm(row.get("prezzo")),
        "gruppo": norm(row.get("gruppo")),
    }


def _validate_row(row: Dict[str, str]) -> Tuple[bool, List[str], List[str]]:
    """Ritorna (reject, errors, warnings). Scarto solo se manca 'codice'."""
    errors: List[str] = []
    warnings: List[str] = []

    if not row.get("codice"):
        errors.append("campo 'codice' mancante")
    if not row.get("descrizione"):
        warnings.append("campo 'descrizione' mancante")
    # prezzo: accetto vuoto; se presente, controllo forma semplice
    p = row.get("prezzo", "")
    if p and not _is_number_like(p):
        warnings.append("campo 'prezzo' non numerico (accettato come stringa)")

    return (len(errors) > 0, errors, warnings)


def _is_number_like(s: str) -> bool:
    # accetta "10", "10.5", "10,50"
    s2 = s.replace(",", ".")
    try:
        float(s2)
        return True
    except Exception:
        return False


def _merge_items(
    existing: List[Dict[str, str]], new_rows: List[Dict[str, str]]
) -> Tuple[int, int]:
    """Ritorna: (updated_existing, rows_parsed)"""
    index = {it.get("codice", ""): i for i, it in enumerate(existing)}
    updated = 0
    for r in new_rows:
        code = r.get("codice", "")
        if not code:
            continue
        if code in index:
            existing[index[code]].update(r)
            updated += 1
        else:
            existing.append(r)
    return updated, len(new_rows)


def _partition_with_validation(
    reader: csv.DictReader,
) -> Tuple[
    List[Dict[str, str]],
    List[Dict[str, str]],
    List[Dict[str, Any]],
    List[Dict[str, Any]],
]:
    accepted: List[Dict[str, str]] = []
    rejected: List[Dict[str, str]] = []
    errors_out: List[Dict[str, Any]] = []
    warnings_out: List[Dict[str, Any]] = []

    # il DictReader parte dalla riga2 (1 è intestazione)
    for idx, raw_row in enumerate(reader, start=2):
        row = _normalize_row(raw_row)
        reject, errs, warns = _validate_row(row)
        if reject:
            rejected.append(row)
            errors_out.append({"rownum": idx, "errors": errs, "row": row})
        else:
            accepted.append(row)
            if warns:
                warnings_out.append({"rownum": idx, "warnings": warns, "row": row})

    return accepted, rejected, errors_out, warnings_out


# === Endpoints ===
@router.get("/template", response_class=PlainTextResponse, summary="Intestazione CSV")
def template_csv() -> str:
    return "codice,descrizione,prezzo,gruppo\n"


@router.post(
    "/save",
    summary="Importa CSV dal body (text/csv) con validazioni soft e merge persistente",
)
async def import_and_save_csv(raw: bytes = Body(..., media_type="text/csv")):
    from datetime import datetime

    text = _safe_decode(raw)
    reader = csv.DictReader(io.StringIO(text))

    accepted, rejected, errors_out, warnings_out = _partition_with_validation(reader)

    items = _load_json()
    updated, parsed = _merge_items(items, accepted)
    _save_json(items)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = IMPORTS_DIR / f"catalogo_{ts}.csv"
    dest.write_bytes(raw)

    return {
        "status": "ok",
        "saved": True,
        "csv_path": str(dest.as_posix()),
        "rows_parsed": parsed,
        "updated_existing": updated,
        "accepted": len(accepted),
        "rejected": len(rejected),
        "errors": errors_out[:50],
        "warnings": warnings_out[:50],
        "total_items": len(items),
    }


@router.get("/catalogo", summary="Ritorna il catalogo DPI corrente (JSON)")
def get_catalogo():
    items = _load_json()
    return {"count": len(items), "items": items}


@router.get(
    "/export",
    response_class=PlainTextResponse,
    summary="Esporta catalogo completo o filtrato (gruppo, colonne)",
)
def export_catalogo_csv(
    gruppo: Optional[str] = Query(default=None, description="Filtro per gruppo"),
    columns: Optional[str] = Query(
        default=None, description="Colonne CSV, es: codice,prezzo (default: tutte)"
    ),
):
    items = _load_json()
    if gruppo:
        items = [it for it in items if it.get("gruppo") == gruppo]

    if columns:
        req_cols = [c.strip() for c in columns.split(",") if c.strip()]
        invalid = [c for c in req_cols if c not in _ALLOWED_FIELDS]
        if invalid:
            raise HTTPException(
                status_code=400,
                detail=f"Colonne non valide: {invalid}. Ammesse: {_ALLOWED_FIELDS}",
            )
        fieldnames = req_cols
    else:
        fieldnames = _ALLOWED_FIELDS

    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    for it in items:
        w.writerow({k: it.get(k, "") for k in fieldnames})
    return PlainTextResponse(buf.getvalue(), media_type="text/csv")


@router.post(
    "/import-file",
    summary="Importa CSV via multipart/form-data (UploadFile) con validazioni soft e merge",
)
async def import_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Atteso file .csv")

    raw = await file.read()
    text = _safe_decode(raw)
    reader = csv.DictReader(io.StringIO(text))

    accepted, rejected, errors_out, warnings_out = _partition_with_validation(reader)

    items = _load_json()
    updated, parsed = _merge_items(items, accepted)
    _save_json(items)

    # salva copia del file originale
    dest = IMPORTS_DIR / file.filename
    if dest.exists():
        from datetime import datetime

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = IMPORTS_DIR / f"{dest.stem}_{ts}{dest.suffix}"
    dest.write_bytes(raw)

    return {
        "status": "ok",
        "uploaded": file.filename,
        "stored_as": str(dest.as_posix()),
        "rows_parsed": parsed,
        "updated_existing": updated,
        "accepted": len(accepted),
        "rejected": len(rejected),
        "errors": errors_out[:50],
        "warnings": warnings_out[:50],
        "total_items": len(items),
    }


# === Metrics ===
def compute_metrics() -> Dict[str, Any]:
    items = _load_json()
    by_group: Dict[str, int] = {}
    price_filled = 0
    for it in items:
        g = (it.get("gruppo") or "").strip() or "_vuoto_"
        by_group[g] = by_group.get(g, 0) + 1
        if it.get("prezzo"):
            price_filled += 1

    return {
        "total_items": len(items),
        "by_group": by_group,
        "price_filled": price_filled,
        "price_missing": len(items) - price_filled,
    }


@router.get(
    "/metrics", summary="Metriche CSV (conteggi per gruppo, prezzi presenti/mancanti)"
)
def csv_metrics():
    return compute_metrics()
