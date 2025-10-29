from fastapi import APIRouter, UploadFile, File, Response, HTTPException
import os
import datetime

router = APIRouter(prefix="/api/dpi/csv", tags=["dpi-csv"])

HEADER = "codice,descrizione,marca,modello,matricola,assegnato_a,data_inizio,data_fine,certificazione,scadenza,note"
BOM = "\ufeff"
MAX_BYTES = 5 * 1024 * 1024  # 5MB

@router.get("/template")
def csv_template():
    # CSV "sicuro" per Excel/Windows: BOM UTF-8 + CRLF
    content = BOM + HEADER + "\r\n"
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="dpi_template.csv"',
            "Cache-Control": "no-store",
        },
    )

def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

@router.post("/import")
async def csv_import(file: UploadFile = File(...)):
    # Limite dimensione
    raw = await file.read()
    if len(raw) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large (limit 5MB).")

    # Audit su disco
    save_dir = os.path.join("data", "imports")
    _ensure_dir(save_dir)
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_name = os.path.basename(file.filename or "upload.csv")
    audit_path = os.path.join(save_dir, f"{ts}-{safe_name}")
    with open(audit_path, "wb") as f:
        f.write(raw)

    # Decodifica + normalizza righe
    text = raw.decode("utf-8-sig", errors="ignore")
    lines = [ln for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n") if ln.strip() != ""]
    if not lines:
        return {"status": "ok", "rows": 0}

    # Verifica header
    got_header = lines[0].strip()
    if got_header != HEADER:
        raise HTTPException(status_code=400, detail=f"Invalid header. Expected '{HEADER}' got '{got_header}'")

    rows = len(lines) - 1
    return {"status": "ok", "rows": rows}
