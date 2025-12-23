from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/api/dpi/csv", tags=["dpi-csv"])


@router.get("/template", response_class=PlainTextResponse)
def csv_template() -> str:
    return "codice,nome,scadenza\n"
