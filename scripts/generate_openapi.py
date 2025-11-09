from typing import Optional, List
from pathlib import Path
import csv
import io

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

router = APIRouter(tags=["CSV"])


@router.get(
    "/api/dpi/csv/export",
    summary="Esporta catalogo DPI (CSV) - filtro gruppo opzionale",
)
def export_csv(gruppo: Optional[str] = None):
    """Esporta il catalogo DPI come CSV, con filtro opzionale per gruppo."""
    p = Path("data/catalogo.csv")
    if not p.exists():
        raise HTTPException(status_code=404, detail="Catalogo non trovato")

    # Legge tutte le righe e si tiene le intestazioni
    with p.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames: List[str] = list(reader.fieldnames or [])

    if not fieldnames:
        raise HTTPException(
            status_code=500,
            detail="Intestazioni CSV mancanti nel catalogo",
        )

    # Filtro opzionale per gruppo
    if gruppo:
        rows = [r for r in rows if (r.get("gruppo") or "").strip() == gruppo]

    if not rows:
        raise HTTPException(
            status_code=404,
            detail="Nessuna riga per i criteri richiesti",
        )

    # Scrive il CSV in memoria
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    out.seek(0)

    return StreamingResponse(
        io.BytesIO(out.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="catalogo_export.csv"',
        },
    )
