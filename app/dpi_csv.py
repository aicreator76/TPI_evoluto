from fastapi import APIRouter, Request, Response
from fastapi.responses import PlainTextResponse
import csv
import io

router = APIRouter()


def _decode_best(raw: bytes) -> str:
    # ordina i fallback in modo pragmatico; niente one-liners (ruff E701)
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def _csv_router(prefix: str) -> APIRouter:
    r = APIRouter(prefix=prefix, tags=["cataloghi"])

    @r.head("/template")
    async def template_head() -> Response:
        return Response(status_code=204)

    @r.get("/template", response_class=PlainTextResponse)
    async def template_get() -> str:
        return "codice,descrizione,prezzo,gruppo\n"

    @r.post("/import")
    async def import_csv(request: Request):
        raw = await request.body()
        text = _decode_best(raw)
        rows = list(csv.DictReader(io.StringIO(text))) if text.strip() else []
        return {"status": "ok", "rows": len(rows), "preview": rows[:3]}

    return r


# Compat: vecchio+nuovo path
router.include_router(_csv_router("/v1/cataloghi/csv"))
router.include_router(_csv_router("/api/dpi/csv"))
