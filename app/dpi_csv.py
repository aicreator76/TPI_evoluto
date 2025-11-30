from __future__ import annotations

import csv
import io
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, List, Tuple

from fastapi import APIRouter, UploadFile, File, Body, Query, FastAPI
from fastapi.responses import PlainTextResponse, HTMLResponse, JSONResponse

# ============================================================
# Router Catalogo DPI
# - Template CSV stabile
# - Import CSV (raw + file)
# - Merge idempotente su "codice"
# - Export CSV
# - Catalogo JSON
# - Metrics + mini report HTML
# ============================================================

router = APIRouter(prefix="/api/dpi/csv", tags=["csv"])

# App FastAPI + health -------------------------------------------------

app = FastAPI(title="Catalogo DPI API", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    """
    Healthcheck semplice per smoke test / monitoraggio.
    """
    return {"status": "ok", "service": "catalogo_dpi_csv"}


# ---------- Helpers filesystem / dati ----------


def _base_dir() -> Path:
    """
    Directory base per i dati del catalogo.
    - Usa CATALOGHI_BASE_DIR se presente
    - Altrimenti: data/cataloghi
    """
    env = os.getenv("CATALOGHI_BASE_DIR")
    if env and env.strip():
        return Path(env).expanduser().resolve()
    return Path("data") / "cataloghi"


def _ensure_tree() -> Tuple[Path, Path, Path, Path]:
    base = _base_dir()
    inbox_dir = base / "inbox"
    clean_dir = base / "clean"
    imports_dir = base / "imports"
    reports_dir = base / "reports"

    for d in (inbox_dir, clean_dir, imports_dir, reports_dir):
        d.mkdir(parents=True, exist_ok=True)

    # File JSON "canonico" del catalogo
    items_path = clean_dir / "dpi_items.json"
    return base, imports_dir, items_path, reports_dir


def _load_json() -> List[dict[str, Any]]:
    _, _, items_path, _ = _ensure_tree()
    if not items_path.exists():
        return []
    try:
        return json.loads(items_path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_json(items: List[dict[str, Any]]) -> None:
    _, _, items_path, _ = _ensure_tree()
    items_path.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _normalize_row(row: dict[str, Any]) -> dict[str, str]:
    return {
        "codice": (row.get("codice") or "").strip(),
        "descrizione": (row.get("descrizione") or "").strip(),
        "prezzo": (row.get("prezzo") or "").strip(),
        "gruppo": (row.get("gruppo") or "").strip(),
    }


def _merge_items(
    items: List[dict[str, Any]], rows: List[dict[str, Any]]
) -> Tuple[int, int]:
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


def _parse_csv_bytes(raw: bytes) -> Tuple[list[dict[str, Any]], int]:
    text = raw.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    rows = [_normalize_row(row) for row in reader]
    return rows, len(rows)


# ---------- Routes principali ----------


@router.get("/template", response_class=PlainTextResponse)
def template_csv() -> PlainTextResponse:
    """
    Template CSV v1 — header stabile.
    """
    header = "codice,descrizione,prezzo,gruppo\n"
    return PlainTextResponse(header, media_type="text/csv")


@router.post("/save")
async def import_and_save_csv(
    raw: bytes = Body(..., media_type="text/csv")
) -> JSONResponse:
    """
    Import CSV da raw text/csv (es. pipeline CI, automazioni).
    - Salva il file in data/cataloghi/imports
    - Merge idempotente su JSON canonico in data/cataloghi/clean/dpi_items.json
    """
    _, imports_dir, _, _ = _ensure_tree()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = imports_dir / f"catalogo_{ts}.csv"
    dest.write_bytes(raw)

    rows, parsed = _parse_csv_bytes(raw)
    items = _load_json()
    updated, _ = _merge_items(items, rows)
    _save_json(items)

    payload = {
        "status": "ok",
        "mode": "raw-save",
        "csv_path": str(dest),
        "rows_parsed": parsed,
        "updated_existing": updated,
        "total_items": len(items),
    }
    return JSONResponse(payload)


@router.get("/catalogo")
def get_catalogo() -> dict[str, Any]:
    """
    Catalogo DPI corrente in JSON.
    """
    items = _load_json()
    return {"count": len(items), "items": items}


@router.get("/export", response_class=PlainTextResponse)
def export_catalogo_csv(
    columns: str = Query("short", description="short|full (placeholder)"),
) -> PlainTextResponse:
    """
    Export CSV del catalogo corrente.
    - columns=short|full (per ora identici, ma l'API è stabile).
    """
    items = _load_json()
    fieldnames = ["codice", "descrizione", "prezzo", "gruppo"]
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for it in items:
        writer.writerow({k: (it.get(k) or "") for k in fieldnames})
    return PlainTextResponse(buf.getvalue(), media_type="text/csv")


@router.post("/import-file")
async def import_file(file: UploadFile = File(...)) -> JSONResponse:
    """
    Import CSV via multipart/form-data (upload file).
    - Salva il file in data/cataloghi/imports con timestamp
    - Merge su JSON canonico come /save
    """
    raw = await file.read()
    _, imports_dir, _, _ = _ensure_tree()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = Path(file.filename or f"upload_{ts}.csv").name
    dest = imports_dir / f"{ts}_{safe_name}"
    dest.write_bytes(raw)

    rows, parsed = _parse_csv_bytes(raw)
    items = _load_json()
    updated, _ = _merge_items(items, rows)
    _save_json(items)

    payload = {
        "status": "ok",
        "mode": "upload",
        "filename": safe_name,
        "csv_path": str(dest),
        "rows_parsed": parsed,
        "updated_existing": updated,
        "total_items": len(items),
    }
    return JSONResponse(payload)


@router.post("/import")
async def import_alias(file: UploadFile = File(...)) -> JSONResponse:
    """
    Alias backwards-compatible per /import-file.
    """
    return await import_file(file)


# ---------- Metrics + Report ----------


@router.get("/metrics")
def catalogo_metrics() -> dict[str, Any]:
    """
    Metriche di base del Catalogo DPI (per smoke/monitoring).
    """
    _, imports_dir, _, reports_dir = _ensure_tree()
    items = _load_json()
    imports = sorted(imports_dir.glob("*.csv"))
    last_import = imports[-1].stat().st_mtime if imports else None

    return {
        "total_items": len(items),
        "imports_count": len(imports),
        "last_import_at": (
            datetime.fromtimestamp(last_import).isoformat() if last_import else None
        ),
        "reports_dir": str(reports_dir),
    }


@router.get("/report.html", response_class=HTMLResponse)
def catalogo_report_html() -> HTMLResponse:
    """
    Mini report HTML — pensato per ispezione veloce in browser.
    """
    metrics = catalogo_metrics()
    items = _load_json()
    preview = items[:50]

    rows_html = "\n".join(
        f"<tr><td>{i+1}</td><td>{it.get('codice','')}</td>"
        f"<td>{it.get('descrizione','')}</td><td>{it.get('prezzo','')}</td>"
        f"<td>{it.get('gruppo','')}</td></tr>"
        for i, it in enumerate(preview)
    )

    html = f"""
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="utf-8" />
  <title>Catalogo DPI – Report</title>
  <style>
    body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 1.5rem; }}
    h1 {{ font-size: 1.4rem; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
    th, td {{ border: 1px solid #ddd; padding: 0.4rem; font-size: 0.85rem; }}
    th {{ background: #f5f5f5; text-align: left; }}
    caption {{ text-align: left; font-weight: bold; margin-bottom: 0.5rem; }}
    .metrics {{ margin-top: 0.5rem; font-size: 0.85rem; color: #555; }}
  </style>
</head>
<body>
  <h1>Catalogo DPI – Report</h1>
  <div class="metrics">
    <div><strong>Totale items:</strong> {metrics["total_items"]}</div>
    <div><strong>Import CSV:</strong> {metrics["imports_count"]}</div>
    <div><strong>Ultimo import:</strong> {metrics["last_import_at"] or "-"} </div>
  </div>
  <table>
    <caption>Preview (max 50 righe)</caption>
    <thead>
      <tr>
        <th>#</th>
        <th>Codice</th>
        <th>Descrizione</th>
        <th>Prezzo</th>
        <th>Gruppo</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</body>
</html>
"""
    return HTMLResponse(html)


# Monta il router sull'app FastAPI
app.include_router(router)
