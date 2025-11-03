from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

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
def _safe_decode(b: bytes) -> str:
    # tollerante a BOM/encoding locali
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


# === Endpoints ===
@router.get("/template", response_class=PlainTextResponse, summary="Intestazione CSV")
def template_csv() -> str:
    return "codice,descrizione,prezzo,gruppo\n"


@router.post(
    "/save", summary="Importa CSV dal body (text/csv) e salva/merge nel catalogo"
)
async def import_and_save_csv(raw: bytes = Body(..., media_type="text/csv")):
    from datetime import datetime

    text = _safe_decode(raw)
    reader = csv.DictReader(io.StringIO(text))
    rows = [_normalize_row(r) for r in reader]

    items = _load_json()
    updated, parsed = _merge_items(items, rows)
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
        "total_items": len(items),
    }


@router.get("/catalogo", summary="Ritorna il catalogo DPI corrente (JSON)")
def get_catalogo():
    items = _load_json()
    return {"count": len(items), "items": items}


@router.get(
    "/export",
    response_class=PlainTextResponse,
    summary="Esporta catalogo completo o filtrato per gruppo",
)
def export_catalogo_csv(
    gruppo: Optional[str] = Query(default=None, description="Filtro per gruppo")
):
    items = _load_json()
    if gruppo:
        items = [it for it in items if it.get("gruppo") == gruppo]

    fieldnames = ["codice", "descrizione", "prezzo", "gruppo"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    for it in items:
        w.writerow({k: it.get(k, "") for k in fieldnames})
    return PlainTextResponse(buf.getvalue(), media_type="text/csv")


@router.post(
    "/import-file",
    summary="Importa CSV via multipart/form-data (UploadFile) e salva/merge",
)
async def import_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Atteso file .csv")

    raw = await file.read()
    text = _safe_decode(raw)
    reader = csv.DictReader(io.StringIO(text))
    rows = [_normalize_row(r) for r in reader]

    items = _load_json()
    updated, parsed = _merge_items(items, rows)
    _save_json(items)

    # salva copia del file originale
    dest = IMPORTS_DIR / file.filename
    # evita overwrite
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
        "total_items": len(items),
    }
