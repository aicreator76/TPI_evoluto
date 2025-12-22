from __future__ import annotations

import csv
import io
from typing import Any, Dict, List

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse

router = APIRouter(tags=["CSV - Percorsi"])

# In-memory store (mock). In futuro: DB.
PERCORSI: List[Dict[str, Any]] = []


def _csv_response(rows: List[Dict[str, Any]], filename: str) -> PlainTextResponse:
    """
    Ritorna un CSV (delimiter ;) come PlainTextResponse con header download.
    - Se rows è vuoto: CSV con messaggio.
    """
    csv_buf = io.StringIO()

    if not rows:
        w = csv.writer(csv_buf, delimiter=";")
        w.writerow(["message"])
        w.writerow(["Nessun dato nei percorsi"])
    else:
        fieldnames = list(rows[0].keys())
        dw = csv.DictWriter(
            csv_buf,
            fieldnames=fieldnames,
            delimiter=";",
            extrasaction="ignore",
        )
        dw.writeheader()
        for row in rows:
            dw.writerow(row)

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return PlainTextResponse(
        content=csv_buf.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers=headers,
    )


@router.get("/percorsi", name="percorsi_list")
def list_percorsi() -> Dict[str, Any]:
    return {
        "total": len(PERCORSI),
        "items": PERCORSI,
    }


@router.get("/percorsi/export", name="percorsi_export")
def export_percorsi() -> PlainTextResponse:
    return _csv_response(PERCORSI, "percorsi.csv")


@router.post("/percorsi/import", name="percorsi_import")
async def import_percorsi(file: UploadFile = File(...)) -> Dict[str, Any]:
    filename = (file.filename or "").strip()
    if not filename:
        raise HTTPException(400, "Nome file mancante")
    if not filename.lower().endswith(".csv"):
        raise HTTPException(400, "Carica un CSV")

    raw = await file.read()
    text = raw.decode("utf-8-sig")  # gestisce BOM
    rdr = csv.DictReader(io.StringIO(text), delimiter=";")
    rows: List[Dict[str, Any]] = list(rdr)

    global PERCORSI
    PERCORSI = rows

    return {"imported": len(rows)}
