from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, UploadFile, File, Body, HTTPException, Query
from fastapi.responses import PlainTextResponse, HTMLResponse

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
_COLUMN_ALIASES: Dict[str, List[str]] = {
    "*": _ALLOWED_FIELDS,
    "full": _ALLOWED_FIELDS,
    "short": ["codice", "prezzo"],
    "id": ["codice"],
    "listino": ["codice", "descrizione", "prezzo"],
}


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


def _validate_row(
    row: Dict[str, str],
) -> Tuple[bool, List[Dict[str, str]], List[Dict[str, str]]]:
    """Ritorna (reject, errors[], warnings[]), con codici e hint."""
    errors: List[Dict[str, str]] = []
    warnings: List[Dict[str, str]] = []

    if not row.get("codice"):
        errors.append(
            {
                "code": "ERR_MISSING_CODE",
                "msg": "campo 'codice' mancante",
                "hint": "Compila la colonna 'codice' (es. IKAR-ABC123).",
            }
        )
    if not row.get("descrizione"):
        warnings.append(
            {
                "code": "WARN_DESC_MISSING",
                "msg": "campo 'descrizione' mancante",
                "hint": "Aggiungi una descrizione breve e chiara.",
            }
        )
    p = row.get("prezzo", "")
    if p and not _is_number_like(p):
        warnings.append(
            {
                "code": "WARN_PRICE_NON_NUMERIC",
                "msg": "campo 'prezzo' non numerico",
                "hint": "Usa 19.90 o 19,90 senza simboli.",
            }
        )

    return (len(errors) > 0, errors, warnings)


def _is_number_like(s: str) -> bool:
    s2 = s.replace(",", ".")
    try:
        float(s2)
        return True
    except Exception:
        return False


def _merge_items(
    existing: List[Dict[str, str]], new_rows: List[Dict[str, str]]
) -> Tuple[int, int]:
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


def _resolve_columns(columns: Optional[str]) -> List[str]:
    if not columns:
        return _ALLOWED_FIELDS
    key = columns.strip().lower()
    if key in _COLUMN_ALIASES:
        return _COLUMN_ALIASES[key]
    req_cols = [c.strip() for c in columns.split(",") if c.strip()]
    invalid = [c for c in req_cols if c not in _ALLOWED_FIELDS]
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Colonne non valide: {invalid}. Ammesse: {_ALLOWED_FIELDS} o alias {list(_COLUMN_ALIASES.keys())}",
        )
    return req_cols


# === Endpoints ===
@router.get("/template", response_class=PlainTextResponse, summary="Intestazione CSV")
def template_csv() -> str:
    return "codice,descrizione,prezzo,gruppo\n"


@router.post(
    "/save", summary="Importa CSV (text/csv) con validazioni soft e merge persistente"
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
        default=None,
        description="Colonne CSV: alias (short, listino, full) o lista es. codice,prezzo",
    ),
):
    items = _load_json()
    if gruppo:
        items = [it for it in items if it.get("gruppo") == gruppo]

    fieldnames = _resolve_columns(columns)

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


# === Report HTML ===
@router.get(
    "/report.html",
    response_class=HTMLResponse,
    summary="Mini dashboard HTML del catalogo",
)
def report_html(
    gruppo: Optional[str] = Query(default=None, description="Filtro per gruppo"),
    columns: Optional[str] = Query(
        default="listino", description="Alias o lista colonne"
    ),
    limit: int = Query(default=200, ge=1, le=5000, description="Limite righe tabella"),
):
    metrics = compute_metrics()
    cols = _resolve_columns(columns)
    items = _load_json()
    if gruppo:
        items = [it for it in items if it.get("gruppo") == gruppo]
    rows = items[:limit]

    def esc(s: str) -> str:
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    thead = "".join(f"<th>{esc(c)}</th>" for c in cols)
    tbody = "".join(
        "<tr>" + "".join(f"<td>{esc(r.get(c, ''))}</td>" for c in cols) + "</tr>"
        for r in rows
    )
    by_group_html = "".join(
        f"<li><strong>{esc(g)}</strong>: {n}</li>"
        for g, n in sorted(metrics["by_group"].items())
    )

    html = f"""<!doctype html>
<html lang="it"><meta charset="utf-8">
<title>Catalogo DPI – Report</title>
<style>
body{{font-family:system-ui,Segoe UI,Arial,sans-serif;margin:24px}}
.card{{border:1px solid #e5e7eb;border-radius:12px;padding:16px;margin-bottom:16px}}
h1{{margin:0 0 12px 0}}
table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #e5e7eb;padding:8px;text-align:left}}
th{{background:#f8fafc}}
.badge{{display:inline-block;padding:2px 8px;border-radius:999px;background:#e0f2fe}}
.small{{color:#6b7280;font-size:12px}}
</style>
<div class="card">
  <h1>Report Catalogo DPI <span class="badge">{len(items)} elementi</span></h1>
  <div class="small">Colonne: {", ".join(cols)}{(" · Filtro gruppo: " + esc(gruppo)) if gruppo else ""}</div>
</div>
<div class="card">
  <h2>Metriche</h2>
  <ul>
    <li>Totale: {metrics["total_items"]}</li>
    <li>Con prezzo: {metrics["price_filled"]} · Senza prezzo: {metrics["price_missing"]}</li>
    <li>Per gruppo:</li>
  </ul>
  <ul>{by_group_html}</ul>
</div>
<div class="card">
  <h2>Anteprima</h2>
  <table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>
  <div class="small">Visualizzate prime {min(limit, len(items))} righe.</div>
</div>
</html>"""
    return HTMLResponse(html, media_type="text/html")
