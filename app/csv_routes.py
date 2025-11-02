import csv
import io

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api", tags=["csv"])

# --- MOCK DATA (sostituirai con storage reale)
CATALOGHI = [
    {"id": "CAT-001", "nome": "Imbracature"},
    {"id": "CAT-002", "nome": "Cordini"},
]
SCHEDE = [{"id": "SCH-001", "catalogo_id": "CAT-001", "titolo": "Imbracatura X"}]
PERCORSI = [{"id": "PER-001", "nome": "Linea vita tetto A", "stato": "attivo"}]


def _csv_response(rows, filename):
    buf = io.StringIO(newline="")
    w = (
        csv.DictWriter(buf, fieldnames=rows[0].keys())
        if rows
        else csv.DictWriter(buf, fieldnames=["vuoto"])
    )
    w.writeheader()
    for r in rows:
        w.writerow(r)
    data = buf.getvalue().encode("utf-8-sig")  # BOM
    return StreamingResponse(
        io.BytesIO(data),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/cataloghi/export")
def export_cataloghi():
    return _csv_response(CATALOGHI, "cataloghi.csv")


@router.get("/schede/export")
def export_schede():
    return _csv_response(SCHEDE, "schede.csv")


@router.get("/percorsi/export")
def export_percorsi():
    return _csv_response(PERCORSI, "percorsi.csv")


@router.post("/cataloghi/import")
async def import_cataloghi(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Carica un CSV")
    text = (await file.read()).decode("utf-8-sig")
    rdr = csv.DictReader(io.StringIO(text))
    rows = list(rdr)
    if rows:  # replace mock for now
        global CATALOGHI
        CATALOGHI = rows
    return {"imported": len(rows)}


@router.post("/schede/import")
async def import_schede(file: UploadFile = File(...)):
    text = (await file.read()).decode("utf-8-sig")
    rdr = csv.DictReader(io.StringIO(text))
    rows = list(rdr)
    if rows:
        global SCHEDE
        SCHEDE = rows
    return {"imported": len(rows)}


@router.post("/percorsi/import")
async def import_percorsi(file: UploadFile = File(...)):
    text = (await file.read()).decode("utf-8-sig")
    rdr = csv.DictReader(io.StringIO(text))
    rows = list(rdr)
    if rows:
        global PERCORSI
        PERCORSI = rows
    return {"imported": len(rows)}
