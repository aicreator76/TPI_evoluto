from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Optional
from pathlib import Path
import csv
import io

router = APIRouter(tags=["CSV"])

CATALOGO_PATH = Path("data/catalogo.csv")

# Campi personalizzabili
REQUIRED = {"codice", "descrizione"}
OPTIONAL = {"gruppo", "nota", "marca", "modello"}
ALLOWED = REQUIRED | OPTIONAL

MAX_SIZE_MB = 8


def _decode_bytes(b: bytes) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return b.decode(enc)
        except Exception:
            continue
    raise UnicodeDecodeError("decode", b, 0, 1, "unsupported encodings")


@router.post(
    "/api/dpi/csv/import-file", summary="Importa catalogo DPI da file CSV (multipart)"
)
async def import_file(file: UploadFile = File(...), gruppo: Optional[str] = None):
    name = (file.filename or "").lower()
    if not name.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Carica un file .csv")

    raw = await file.read()
    if len(raw) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413, detail=f"File troppo grande (> {MAX_SIZE_MB}MB)"
        )

    text = _decode_bytes(raw)
    sio = io.StringIO(text)
    reader = csv.DictReader(sio)

    headers = set([h.strip() for h in (reader.fieldnames or [])])
    if not headers:
        raise HTTPException(status_code=400, detail="CSV senza header")

    missing = sorted(list(REQUIRED - headers))
    unknown = sorted([h for h in headers if h not in ALLOWED])

    rows: List[Dict] = []
    for r in reader:
        row = {(k or "").strip(): (v or "").strip() for k, v in r.items()}
        if gruppo and not row.get("gruppo"):
            row["gruppo"] = gruppo
        rows.append(row)

    # Persistenza semplice: append su data/catalogo.csv
    CATALOGO_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_header = not CATALOGO_PATH.exists()
    with CATALOGO_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(list(ALLOWED)))
        if write_header:
            writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in sorted(list(ALLOWED))})

    return {
        "filename": file.filename,
        "imported": len(rows),
        "warnings": {
            "missing_required_headers": missing,
            "unknown_headers": unknown,
        },
        "target": str(CATALOGO_PATH),
    }
