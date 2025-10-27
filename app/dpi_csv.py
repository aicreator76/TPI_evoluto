from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io, csv

router = APIRouter(prefix="/api/dpi/csv", tags=["dpi_csv"])

@router.get("/template")
def get_template():
    headers = ["codice","descrizione","marca","modello","matricola",
               "assegnato_a","data_inizio","data_fine","certificazione","scadenza","note"]
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=headers)
    w.writeheader()
    data = buf.getvalue().encode("utf-8-sig")  # BOM per Excel (compatibile Excel)
    return StreamingResponse(
        io.BytesIO(data),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="dpi_template.csv"'},
    )
