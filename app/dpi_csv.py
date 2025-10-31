import os, time
from fastapi import HTTPException

MAX_BYTES = 5 * 1024 * 1024
EXPECTED = HEADER.split(",")

@router.post("/import")
async def csv_import(file: UploadFile = File(...)):
    raw = await file.read()
    if len(raw) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="file_too_large")

    # salva il file grezzo (con BOM ripulito) per auditing
    os.makedirs("data/imports", exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    raw_path = f"data/imports/dpi_import_{ts}.csv"
    with open(raw_path, "wb") as f:
        f.write(raw)

    text = raw.decode("utf-8-sig", errors="ignore").splitlines()
    if not text:
        return {"status": "ok", "rows": 0}

    header = [h.strip() for h in text[0].split(",")]
    if header != EXPECTED:
        raise HTTPException(status_code=400, detail="bad_header")

    rows = [r for r in text[1:] if r.strip()]
    # TODO: parsing -> dict e persistenza DB
    return {"status": "ok", "rows": len(rows), "file": raw_path}
    )

@router.post("/import")
async def csv_import(file: UploadFile = File(...)):
    data = (await file.read()).decode("utf-8-sig", errors="ignore").splitlines()
    rows = [r for r in data[1:] if r.strip()]
    return {"status": "ok", "rows": len(rows)}
