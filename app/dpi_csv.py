from fastapi import APIRouter, Request, Response
import csv
import io

# Router "contenitore" richiesto da app.main (include_router)
router = APIRouter()


def _csv_router(prefix: str) -> APIRouter:
    r = APIRouter(prefix=prefix, tags=["cataloghi"])

    @r.head("/template")
    async def template_head():
        return Response(status_code=204)

    @r.post("/import")
    async def import_csv(request: Request):
        raw = await request.body()
        text = raw.decode("utf-8", errors="ignore")
        rows = list(csv.DictReader(io.StringIO(text))) if text.strip() else []
        return {"status": "ok", "rows": len(rows), "preview": rows[:3]}

    return r


# Compat: vecchio e nuovo path
router.include_router(_csv_router("/v1/cataloghi/csv"))
router.include_router(_csv_router("/api/dpi/csv"))
