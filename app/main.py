from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from fastapi import APIRouter, FastAPI

from app.api.accessori import router as accessori_router
from app.api.formazione import router as formazione_router
from app.api.funi_acciaio import router as funi_acciaio_router
from app.api.inox import router as inox_router
from app.api.linee_vita import router as linee_vita_router
from app.routers import demo_real
from app.routers.dpi_csv import router as dpi_csv_router


def _norm_prefix(p: str) -> str:
    p = (p or "").strip()
    if not p:
        return ""
    return "/" + p.strip("/")


def _include_api(app: FastAPI, router: APIRouter, prefix_if_missing: str) -> None:
    router_prefix = _norm_prefix(getattr(router, "prefix", "") or "")
    fallback_prefix = _norm_prefix(prefix_if_missing)

    if router_prefix:
        app.include_router(router)
    else:
        app.include_router(router, prefix=fallback_prefix)


def _include_many(app: FastAPI, specs: Iterable[tuple[APIRouter, str]]) -> None:
    for r, p in specs:
        _include_api(app, r, p)


def create_app() -> FastAPI:
    app = FastAPI(title="TPI_evoluto", version="0.1.0")

    @app.get("/healthz", tags=["system"])
    def healthz() -> dict:
        return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

    # Mount demo (se presente)
    demo_real.mount(app)

    # API principali
    _include_many(
        app,
        [
            (linee_vita_router, "/api/linee-vita"),
            (inox_router, "/api/inox"),
            (funi_acciaio_router, "/api/funi-acciaio"),
            (accessori_router, "/api/accessori"),
            (formazione_router, "/api/formazione"),
        ],
    )

    # ✅ CSV DPI (smoke-api aspetta /api/dpi/csv/template)
    app.include_router(dpi_csv_router)

    @app.on_event("startup")
    def _startup_log() -> None:
        wanted = (
            "/api/accessori/overview",
            "/api/formazione/overview",
            "/api/dpi/csv/template",
        )
        present = {getattr(r, "path", "") for r in app.routes}
        missing = [p for p in wanted if p not in present]
        if missing:
            print(f"[STARTUP][WARN] Missing routes: {missing}")
        else:
            print("[STARTUP][OK] routes base presenti (accessori/formazione/dpi_csv)")

    return app


app = create_app()


@app.get("/health", include_in_schema=False)
def health() -> dict:
    return {"status": "ok"}


@app.get("/version", include_in_schema=False)
def version() -> dict:
    return {"app": "tpi_evoluto", "version": app.version}
