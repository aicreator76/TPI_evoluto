from typing import Optional
import io

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

router = APIRouter(
    prefix="/api/dpi/csv",
    tags=["csv"],
)


@router.get("/export", summary="Export DPI filtrato in CSV (stub)")
async def export_csv(gruppo: Optional[str] = Query(None)) -> StreamingResponse:
    """
    Stub minimo per export CSV DPI.

    Parametri:
    - gruppo: filtro logico (non ancora applicato, solo riportato nel CSV)

    Restituisce:
    - CSV con intestazioni corrette e una riga di esempio vuota.
    """
    stream = io.StringIO()
    # Intestazioni: allineate alla logica TPI (puoi adattarle in seguito)
    stream.write(
        "codice,descrizione,marca,modello,matricola,assegnato_a,"
        "data_inizio,data_fine,certificazione,scadenza,note,gruppo\n"
    )

    # Riga di esempio (vuota, solo per smoke test)
    stream.write("," * 11 + (gruppo or "") + "\n")
    stream.seek(0)

    return StreamingResponse(
        stream,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="dpi_export_stub.csv"'},
    )
