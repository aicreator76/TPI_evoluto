from datetime import datetime
from pathlib import Path
import csv
import io
import json

from fastapi import APIRouter, Body
from fastapi.responses import PlainTextResponse

# Router unico e con prefisso stabile
router = APIRouter(prefix="/api/dpi/csv", tags=["csv"])

# Paths base
BASE = Path("data")
IMPORTS_DIR = BASE / "cataloghi" / "imports"
CAT_JSON = BASE / "dpi_items.json"
IMPORTS_DIR.mkdir(parents=True, exist_ok=True)
BASE.mkdir(parents=True, exist_ok=True)

# --- Helpers ---------------------------------------------------------------


def _load_json() -> list[dict]:
    if CAT_JSON.exists():
        try:
            return json.loads(CAT_JSON.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save_json(items: list[dict]) -> None:
    CAT_JSON.write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _merge_items(existing: list[dict], new_rows: list[dict]) -> tuple[int, int]:
    idx = {x.get("codice"): i for i, x in enumerate(existing) if x.get("codice")}
    updated = 0
    for r in new_rows:
        code = (r.get("codice") or "").strip()
        if not code:
            continue
        if code in idx:
            existing[idx[code]].update(r)
            updated += 1
        else:
            existing.append(r)
    return updated, len(new_rows)


# --- Endpoints -------------------------------------------------------------


@router.get("/template", response_class=PlainTextResponse, summary="CSV template")
def csv_template():
    return "codice,descrizione,prezzo,gruppo\n"


@router.post("/save", summary="Importa CSV e salva/merge nel catalogo")
async def import_and_save_csv(raw: bytes = Body(..., media_type="text/csv")):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = IMPORTS_DIR / f"catalogo_{ts}.csv"
    dest.write_bytes(raw)

    text = raw.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    rows = [
        {
            "codice": (row.get("codice") or "").strip(),
            "descrizione": (row.get("descrizione") or "").strip(),
            "prezzo": (row.get("prezzo") or "").strip(),
            "gruppo": (row.get("gruppo") or "").strip(),
        }
        for row in reader
    ]

    items = _load_json()
    updated, parsed = _merge_items(items, rows)
    _save_json(items)

    return {
        "status": "ok",
        "saved": True,
        "csv_path": str(dest),
        "rows_parsed": parsed,
        "updated_existing": updated,
        "total_items": len(items),
    }


@router.get("/catalogo", summary="Ritorna il catalogo DPI corrente (JSON)")
async def get_catalogo():
    items = _load_json()
    return {"items": items, "count": len(items)}
