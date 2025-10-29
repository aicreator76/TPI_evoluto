from fastapi import APIRouter, UploadFile, File, Response

router = APIRouter(prefix="/api/dpi/csv", tags=["dpi-csv"])

HEADER = "codice,descrizione,marca,modello,matricola,assegnato_a,data_inizio,data_fine,certificazione,scadenza,note"

@router.get("/template")
def csv_template():
    return Response(
        content="\ufeff" + HEADER + "\n",
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=\"dpi_template.csv\"",
            "Cache-Control": "no-store",
        },
    )

@router.post("/import")
async def csv_import(file: UploadFile = File(...)):
    data = (await file.read()).decode("utf-8-sig", errors="ignore").splitlines()
    rows = [r for r in data[1:] if r.strip()]
    return {"status": "ok", "rows": len(rows)}
