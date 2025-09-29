from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
import io, csv, codecs

router = APIRouter()

def _template_bytes() -> bytes:
    # StringIO con newline='' + lineterminator='\r\n' per CRLF
    buf = io.StringIO(newline='')
    w = csv.writer(buf, lineterminator='\r\n')
    headers = [
        "codice","descrizione","marca","modello","matricola",
        "assegnato_a","data_inizio","data_fine","certificazione","scadenza","note"
    ]
    w.writerow(headers)
    data = buf.getvalue().encode("utf-8")           # senza BOM
    return codecs.BOM_UTF8 + data                    # aggiungo BOM

@router.get(
    "/api/dpi/csv/template",
    summary="CSV template for DPI import",
    responses={
        200: {
            "description": "CSV file",
            "content": {"text/csv": {"schema": {"type": "string", "format": "binary"}}},
        }
    },
)
def csv_template_get():
    headers = {
        "Content-Disposition": 'attachment; filename="dpi_template.csv"',
        "Cache-Control": "no-store",
    }
    # streaming per evitare bufferoni in memoria
    return StreamingResponse(iter([_template_bytes()]), media_type="text/csv; charset=utf-8", headers=headers)

@router.head("/api/dpi/csv/template", summary="HEAD for CSV template")
def csv_template_head():
    # stesse intestazioni del GET, senza body
    headers = {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": 'attachment; filename="dpi_template.csv"',
        "Cache-Control": "no-store",
    }
    return Response(status_code=200, headers=headers)
