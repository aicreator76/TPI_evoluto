from fastapi import APIRouter, UploadFile, File, Body
from fastapi.responses import PlainTextResponse
from pathlib import Path
import csv, io, json
from datetime import datetime

router = APIRouter(prefix="/api/dpi/csv", tags=["csv"])

# ---------- Helpers ----------
def _paths():
    base = Path("data")
    imports_dir = base / "cataloghi" / "imports"
    imports_dir.mkdir(parents=True, exist_ok=True)
    items_path = base / "dpi_items.json"
    items_path.parent.mkdir(parents=True, exist_ok=True)
    return base, imports_dir, items_path

def _load_json():
    _, _, items_path = _paths()
    if not items_path.exists():
        return []
    try:
        return json.loads(items_path.read_text(encoding="utf-8"))
    except Exception:
        return []

def _save_json(items):
    _, _, items_path = _paths()
    items_path.write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )

def _normalize_row(row: dict) -> dict:
    return {
        "codice": (row.get("codice") or "").strip(),
        "descrizione": (row.get("descrizione") or "").strip(),
        "prezzo": (row.get("prezzo") or "").strip(),
        "gruppo": (row.get("gruppo") or "").strip(),
    }

def _merge_items(items: list[dict], rows: list[dict]) -> tuple[int, int]:
    idx = {(it.get("codice") or "").strip(): i for i, it in enumerate(items)}
    updated = 0
    for r in rows:
        k = (r.get("codice") or "").strip()
        if not k:
            continue
        if k in idx:
            i = idx[k]
            before = items[i].copy()
            # aggiorna solo campi valorizzati
            items[i].update({k2: v for k2, v in r.items() if v != ""})
            if items[i] != before:
                updated += 1
        else:
            items.append(r)
            idx[k] = len(items) - 1
    return updated, len(rows)

# ---------- Routes ----------
@router.get("/template", response_class=PlainTextResponse)
def template_csv():
    return "codice,descrizione,prezzo,gruppo\n"

@router.post("/save")
async def import_and_save_csv(raw: bytes = Body(..., media_type="text/csv")):
    base, imports_dir, _ = _paths()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = imports_dir / f"catalogo_{ts}.csv"
    dest.write_bytes(raw)

    text = raw.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    rows = [_normalize_row(row) for row in reader]

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

@router.get("/catalogo")
def get_catalogo():
    items = _load_json()
    return {"count": len(items), "items": items}

@router.get("/export", response_class=PlainTextResponse)
def export_catalogo_csv():
    items = _load_json()
    fieldnames = ["codice", "descrizione", "prezzo", "gruppo"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fieldnames)
    w.writeheader()
    for it in items:
        w.writerow({k: it.get(k, "") for k in fieldnames})
    return PlainTextResponse(buf.getvalue(), media_type="text/csv")

@router.post("/import-file")
async def import_file(file: UploadFile = File(...)):
    raw = await file.read()
    _, imports_dir, _ = _paths()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = Path(file.filename or f"upload_{ts}.csv").name
    dest = imports_dir / f"{ts}_{safe_name}"
    dest.write_bytes(raw)

    text = raw.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    rows = [_normalize_row(row) for row in reader]

    items = _load_json()
    updated, parsed = _merge_items(items, rows)
    _save_json(items)
    return {
        "status": "ok",
        "saved": True,
        "filename": safe_name,
        "csv_path": str(dest),
        "rows_parsed": parsed,
        "updated_existing": updated,
        "total_items": len(items),
    }

    w.writeheader()
    for it in items:
        w.writerow({k: (it.get(k) or "") for k in FIELDS})
    return PlainTextResponse(buf.getvalue(), media_type="text/csv")
