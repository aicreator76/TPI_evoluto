from __future__ import annotations

from fastapi import APIRouter, Body
from fastapi.responses import PlainTextResponse
from pathlib import Path
import csv, io, json
from datetime import datetime

router = APIRouter(prefix="/api/dpi/csv", tags=["csv"])

# --- paths & storage helpers -------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]  # repo root
DATA_DIR = ROOT / "data"
IMPORTS_DIR = DATA_DIR / "cataloghi" / "imports"
IMPORTS_DIR.mkdir(parents=True, exist_ok=True)

DPI_JSON = DATA_DIR / "dpi_items.json"


def _load_json() -> list[dict]:
    if not DPI_JSON.exists():
        return []
    return json.loads(DPI_JSON.read_text(encoding="utf-8"))


def _save_json(items: list[dict]) -> None:
    DPI_JSON.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _merge_items(items: list[dict], rows: list[dict]) -> tuple[int, int]:
    """Merge su chiave 'codice': aggiorna se esiste, altrimenti aggiunge."""
    index = {it.get("codice", ""): i for i, it in enumerate(items)}
    updated = 0
    for row in rows:
        code = (row.get("codice") or "").strip()
        if not code:
            continue
        if code in index:
            items[index[code]] = {**items[index[code]], **row}
            updated += 1
        else:
            items.append(row)
    return updated, len(rows)


# --- endpoints ---------------------------------------------------------------

@router.get("/template", response_class=PlainTextResponse, summary="Header CSV di esempio")
def template() -> str:
    return "codice,descrizione,prezzo,gruppo\n"


@router.post("/save", summary="Importa CSV e salva/aggiorna il catalogo")
async def save_csv(raw: bytes = Body(..., media_type="text/csv")):
    # 1) salva copia grezza del CSV importato
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = IMPORTS_DIR / f"catalogo_{ts}.csv"
    dest.write_bytes(raw)

    # 2) parse CSV (utf-8 con fallback)
    text = raw.decode("utf-8", errors="replace")
    rdr = csv.DictReader(io.StringIO(text))
    rows = [
        {
            "codice": (r.get("codice") or "").strip(),
            "descrizione": (r.get("descrizione") or "").strip(),
            "prezzo": (r.get("prezzo") or "").strip(),
            "gruppo": (r.get("gruppo") or "").strip(),
        }
        for r in rdr
    ]

    # 3) merge su JSON persistente
    items = _load_json()
    updated, parsed = _merge_items(items, rows)
    _save_json(items)

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
    summary="Esporta il catalogo DPI in CSV",
    response_class=PlainTextResponse,
)
def export_catalogo_csv():
    items = _load_json()
    fieldnames = ["codice", "descrizione", "prezzo", "gruppo"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    w.writeheader()
    for it in items:
        w.writerow({k: it.get(k, "") for k in fieldnames})
    return PlainTextResponse(buf.getvalue(), media_type="text/csv")


# Compat: vecchio+nuovo path
router.include_router(_csv_router("/v1/cataloghi/csv"))
router.include_router(_csv_router("/api/dpi/csv"))
