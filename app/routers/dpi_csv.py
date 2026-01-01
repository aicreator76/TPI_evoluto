from __future__ import annotations

import csv
import io
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse, Response

router = APIRouter(prefix="/api/dpi/csv", tags=["dpi-csv"])

TEMPLATE_VERSION = "v1"
TEMPLATE_HEADER = ["codice", "nome", "scadenza"]
MAX_BYTES = 5 * 1024 * 1024  # 5MB


@router.get("/template", response_class=PlainTextResponse)
def csv_template() -> Response:
    # BOM + CRLF (Excel-friendly)
    content = "\ufeff" + ",".join(TEMPLATE_HEADER) + "\r\n"
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"X-Template-Version": TEMPLATE_VERSION},
    )


@router.post("/import")
async def import_csv(request: Request) -> dict[str, Any]:
    raw = await request.body()

    if not raw:
        raise HTTPException(status_code=400, detail="Empty CSV body")

    if len(raw) > MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"CSV too large (max {MAX_BYTES} bytes)")

    try:
        text = raw.decode("utf-8-sig")  # removes BOM if present
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded")

    sample = text[:4096]
    delimiter = ","
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|"])
        delimiter = dialect.delimiter
    except Exception:
        pass

    f = io.StringIO(text)
    reader = csv.DictReader(f, delimiter=delimiter)

    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="Missing CSV header row")

    fieldnames = [h.strip() for h in reader.fieldnames if h is not None]
    if not fieldnames:
        raise HTTPException(status_code=400, detail="Empty CSV header")

    rows = []
    for row in reader:
        clean = {
            str(k).strip(): (v.strip() if isinstance(v, str) else v)
            for k, v in row.items()
            if k is not None
        }
        if any(v not in (None, "", " ") for v in clean.values()):
            rows.append(clean)

    if len(rows) == 0:
        raise HTTPException(status_code=400, detail="No data rows found")

    return {
        "ok": True,
        "template_version": TEMPLATE_VERSION,
        "detected_delimiter": delimiter,
        "header": fieldnames,
        "rows_received": len(rows),
        "preview": rows[:3],
    }
