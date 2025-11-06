from fastapi import APIRouter, HTTPException
from typing import Optional
from pathlib import Path
from fastapi.responses import StreamingResponse
import csv
import io

router = APIRouter(tags=["CSV"])


@router.get(
    "/api/dpi/csv/export",
    summary="Esporta catalogo DPI (CSV) â€“ filtro gruppo opzionale",
)
def export_csv(gruppo: Optional[str] = None):
    p = Path("data/catalogo.csv")
    if not p.exists():
        raise HTTPException(status_code=404, detail="Catalogo non trovato")

    with p.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if gruppo:
        rows = [r for r in rows if (r.get("gruppo") or "").strip() == gruppo]

    if not rows:
        raise HTTPException(
            status_code=404, detail="Nessuna riga per i criteri richiesti"
        )

    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=reader.fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    out.seek(0)

    return StreamingResponse(
        io.BytesIO(out.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="catalogo_export.csv"'},
    )
