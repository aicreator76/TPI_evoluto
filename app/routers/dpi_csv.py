from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Any, cast

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse, Response

router = APIRouter(prefix="/api/dpi/csv", tags=["dpi-csv"])

TEMPLATE_VERSION = "v1"
TEMPLATE_HEADER = ["codice", "nome", "scadenza"]

MAX_BYTES = 5 * 1024 * 1024
MAX_ROWS = 50_000
SNIFF_DELIMITERS = ",;\t|"
PREVIEW_ROWS = 3

RowValue = str | list[str]


def _parse_date_to_iso(value: str) -> str | None:
    v = value.strip()
    if not v:
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(v, fmt).date().isoformat()
        except ValueError:
            continue
    return None


@router.get("/template", response_class=PlainTextResponse)
def csv_template() -> Response:
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
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded")

    if "\x00" in text:
        raise HTTPException(status_code=400, detail="CSV contains NUL bytes")

    sample = text[:4096]

    delimiter: str = ","
    quotechar: str = '"'
    escapechar: str | None = None
    doublequote: bool = True
    skipinitialspace: bool = False
    quoting: int = csv.QUOTE_MINIMAL

    try:
        sniffed = csv.Sniffer().sniff(sample, delimiters=SNIFF_DELIMITERS)
        delimiter = sniffed.delimiter
        quotechar = sniffed.quotechar or quotechar
        escapechar = sniffed.escapechar
        doublequote = sniffed.doublequote
        skipinitialspace = sniffed.skipinitialspace
        quoting = int(sniffed.quoting)
    except csv.Error:
        pass

    f = io.StringIO(text, newline="")

    reader = csv.DictReader(
        f,
        delimiter=delimiter,
        quotechar=quotechar,
        escapechar=escapechar,
        doublequote=doublequote,
        skipinitialspace=skipinitialspace,
        quoting=quoting,
        restkey="__extra__",
        restval="",
    )

    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="Missing CSV header row")

    raw_fieldnames = [h for h in reader.fieldnames if isinstance(h, str)]
    fieldnames = [h.strip() for h in raw_fieldnames if h.strip()]
    if not fieldnames:
        raise HTTPException(status_code=400, detail="Empty CSV header")

    normalized_header = [h.lower() for h in fieldnames]
    if len(set(normalized_header)) != len(normalized_header):
        raise HTTPException(
            status_code=400, detail="CSV header has duplicate columns (case-insensitive)"
        )

    missing = sorted(set(TEMPLATE_HEADER) - set(normalized_header))
    if missing:
        raise HTTPException(
            status_code=400, detail=f"Missing required columns: {', '.join(missing)}"
        )

    key_map: dict[str, str] = {orig: orig.strip().lower() for orig in raw_fieldnames}

    rows_received = 0
    rows_skipped_empty = 0
    rows_with_extra_columns = 0
    preview: list[dict[str, Any]] = []

    for lineno, row in enumerate(reader, start=2):
        if (lineno - 1) > MAX_ROWS:
            raise HTTPException(status_code=413, detail=f"Too many rows (max {MAX_ROWS})")

        row_t = cast(dict[str, RowValue], row)

        extras = row_t.get("__extra__")
        if isinstance(extras, list):
            if any((x or "").strip() for x in extras):
                rows_with_extra_columns += 1
                raise HTTPException(
                    status_code=400,
                    detail=f"CSV has extra columns on row {lineno} (too many fields)",
                )
        elif isinstance(extras, str):
            if extras.strip():
                rows_with_extra_columns += 1
                raise HTTPException(
                    status_code=400,
                    detail=f"CSV has extra columns on row {lineno} (too many fields)",
                )

        clean: dict[str, Any] = {}
        for k, v in row_t.items():
            if k == "__extra__":
                continue
            nk = key_map.get(k, k.strip().lower())
            if isinstance(v, list):
                clean[nk] = ";".join(v).strip()
            else:
                clean[nk] = v.strip()

        if not any(v not in (None, "", " ") for v in clean.values()):
            rows_skipped_empty += 1
            continue

        if not str(clean.get("codice", "")).strip():
            raise HTTPException(status_code=400, detail=f"Missing 'codice' on row {lineno}")
        if not str(clean.get("nome", "")).strip():
            raise HTTPException(status_code=400, detail=f"Missing 'nome' on row {lineno}")

        scad = clean.get("scadenza")
        if isinstance(scad, str) and scad.strip():
            parsed = _parse_date_to_iso(scad)
            if parsed is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid 'scadenza' format on row {lineno} (use YYYY-MM-DD or DD/MM/YYYY)",
                )
            clean["scadenza"] = parsed

        rows_received += 1
        if len(preview) < PREVIEW_ROWS:
            preview.append(clean)

    if rows_received == 0:
        raise HTTPException(status_code=400, detail="No data rows found")

    return {
        "ok": True,
        "template_version": TEMPLATE_VERSION,
        "detected_delimiter": delimiter,
        "header": normalized_header,
        "rows_received": rows_received,
        "rows_skipped_empty": rows_skipped_empty,
        "rows_with_extra_columns": rows_with_extra_columns,
        "preview": preview,
    }
