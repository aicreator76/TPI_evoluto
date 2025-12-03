from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/api/dpi/csv",
    tags=["csv"],
)


@router.post("/import-file", summary="Import DPI da CSV (stub)")
async def import_csv(file: UploadFile = File(...)) -> Any:
    """
    Stub minimo per import CSV DPI.

    - Verifica estensione .csv
    - Legge il file in memoria e restituisce info base
    - TODO: integrazione con parser reale e modello DPI
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="File mancante")

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Sono accettati solo file CSV")

    contents = await file.read()
    size = len(contents)

    return JSONResponse(
        {
            "status": "accepted",
            "filename": file.filename,
            "size": size,
            "note": "stub csv_import: parsing non ancora implementato",
        }
    )
