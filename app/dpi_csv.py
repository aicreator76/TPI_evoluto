from fastapi import APIRouter, Body
from fastapi.responses import PlainTextResponse
import csv
import io
from pathlib import Path

router = APIRouter(prefix="/api/dpi/csv", tags=["csv"])


def _paths():
    base = Path("data")
    imports_dir = base / "cataloghi" / "imports"
    imports_dir.mkdir(parents=True, exist_ok=True)
    return base, imports_dir, base / "dpi_items.json"


def _load_json():
    import json

    _, _, cat_json = _paths()
    if cat_json.exists():
        try:
            return json.loads(cat_json.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save_json(items):
    import json

    _, _, cat_json = _paths()
    cat_json.write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _merge_items(existing, new_rows):
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


@router.get("/template", response_class=PlainTextResponse)
def template():
    return PlainTextResponse("codice,descrizione,prezzo,gruppo", media_type="text/csv")


@router.post("/save", summary="Importa CSV e salva nel catalogo")
async def import_and_save_csv(raw: bytes = Body(..., media_type="text/csv")):
    from datetime import datetime

    _, imports_dir, _ = _paths()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = imports_dir / f"catalogo_{ts}.csv"
    dest.write_bytes(raw)
    text = raw.decode("utf-8", errors="replace")
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
def get_catalogo():
    items = _load_json()
    return {"items": items, "count": len(items)}


@router.get(
    "/export",
    response_class=PlainTextResponse,
    summary="Esporta l'intero catalogo come CSV",
)
def export_catalogo_csv() -> PlainTextResponse:
    items = _load_json()
    fieldnames = ["codice", "descrizione", "prezzo", "gruppo"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    for it in items:
        w.writerow({k: it.get(k, "") for k in fieldnames})
    return PlainTextResponse(buf.getvalue(), media_type="text/csv")
