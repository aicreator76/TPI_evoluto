# app/dpi_csv.py
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from fastapi import APIRouter, Body
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/api/dpi/csv", tags=["csv"])

# --- percorsi e util ---
BASE = Path("data")
CATALOGHI_DIR = BASE / "cataloghi"
IMPORTS_DIR = CATALOGHI_DIR / "imports"
ITEMS_JSON = BASE / "dpi_items.json"

for d in (BASE, CATALOGHI_DIR, IMPORTS_DIR):
    d.mkdir(parents=True, exist_ok=True)
if not ITEMS_JSON.exists():
    ITEMS_JSON.write_text("[]", encoding="utf-8")

FIELDS = ["codice", "descrizione", "prezzo", "gruppo"]


def _load_json() -> List[Dict[str, str]]:
    try:
        return json.loads(ITEMS_JSON.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_json(items: List[Dict[str, str]]) -> None:
    ITEMS_JSON.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def _merge_items(
    existing: List[Dict[str, str]], incoming: List[Dict[str, str]]
) -> Tuple[int, int]:
    """
    Merge by 'codice' (case-insensitive). Aggiorna se esiste, altrimenti append.
    Ritorna: (updated_count, parsed_count)
    """
    index = { (it.get("codice") or "").strip().lower(): i for i, it in enumerate(existing) }

    updated = 0
    parsed = 0
    for row in incoming:
        parsed += 1
        codice = (row.get("codice") or "").strip()
        if not codice:
            continue  # salta righe senza codice

        key = codice.lower()
        normalized = {
            "codice": codice,
            "descrizione": (row.get("descrizione") or "").strip(),
            "prezzo": (row.get("prezzo") or "").strip(),
            "gruppo": (row.get("gruppo") or "").strip(),
        }

        if key in index:
            existing[index[key]].update(normalized)
            updated += 1
        else:
            existing.append(normalized)
            index[key] = len(existing) - 1

    return updated, parsed


# ---- Endpoints ----

@router.get("/template", response_class=PlainTextResponse, summary="Restituisce l'header CSV")
def template_csv() -> str:
    return ",".join(FIELDS) + "\n"


@router.post("/save", summary="Importa CSV e salva nel catalogo")
async def import_and_save_csv(raw: bytes = Body(..., media_type="text/csv")) -> Dict[str, Any]:
    # salva anche una copia grezza in /data/cataloghi/imports/
    from datetime import datetime

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = IMPORTS_DIR / f"catalogo_{ts}.csv"
    dest.write_bytes(raw)

    # parse CSV in memoria (tollerante a BOM e fallback encoding)
    try:
        text = raw.decode("utf-8-sig")
    except Exception:
        text = raw.decode("latin-1", errors="replace")

    rdr = csv.DictReader(io.StringIO(text))
    rows: List[Dict[str, str]] = []
    for r in rdr:
        rows.append({
            "codice": (r.get("codice") or "").strip(),
            "descrizione": (r.get("descrizione") or "").strip(),
            "prezzo": (r.get("prezzo") or "").strip(),
            "gruppo": (r.get("gruppo") or "").strip(),
        })

    items = _load_json()
    updated, parsed = _merge_items(items, rows)
    _save_json(items)

    return {
        "status": "ok",
        "saved": True,
        "csv_path": str(dest).replace("\\", "/"),
        "rows_parsed": parsed,
        "updated_existing": updated,
        "total_items": len(items),
    }


@router.get("/catalogo", summary="Ritorna il catalogo DPI corrente (JSON)")
def get_catalogo() -> Dict[str, Any]:
    items = _load_json()
    return {"count": len(items), "items": items}


@router.get(
    "/export",
    response_class=PlainTextResponse,
    summary="Esporta catalogo corrente in CSV (text/csv)",
)
def export_catalogo_csv() -> PlainTextResponse:
    items = _load_json()
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS)
    w.writeheader()
    for it in items:
        w.writerow({k: (it.get(k) or "") for k in FIELDS})
    return PlainTextResponse(buf.getvalue(), media_type="text/csv")
