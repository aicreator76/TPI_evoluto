from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

MAX_BYTES = 5 * 1024 * 1024
HEADER = "id,code,desc"  # TODO: aggiorna allo schema reale
EXPECTED = HEADER.split(",")


@router.post("/import")
async def csv_import(file: UploadFile = File(...)):
    raw = await file.read()
    if len(raw) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File troppo grande")

    data = raw.decode("utf-8-sig", errors="ignore").splitlines()
    if not data:
        raise HTTPException(status_code=400, detail="CSV vuoto")

    # Esempio di validazione header (abilita se vuoi)
    # if data[0].strip() != HEADER:
    #     raise HTTPException(status_code=400, detail="Header CSV non valido")

    rows = [r for r in data[1:] if r.strip()]
    return {"status": "ok", "rows": len(rows), "file": getattr(file, "filename", None)}
