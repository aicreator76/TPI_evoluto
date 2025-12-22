from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.routing import APIRouter

from app.api.inox import router as inox_router
from app.api.linee_vita import router as linee_vita_router

# nuovi
from app.api.accessori import router as accessori_router
from app.api.funi_acciaio import router as funi_acciaio_router
from app.api.formazione import router as formazione_router

from app.routers import demo_real


def _include_api(app: FastAPI, router: APIRouter, prefix_if_missing: str) -> None:
    """
    Se il router ha già un prefix (es. '/api/accessori'), lo includo senza prefix.
    Se non ce l’ha, applico prefix_if_missing.
    Così evitiamo doppioni tipo /api/accessori/api/accessori.
    """
    rp = (getattr(router, "prefix", "") or "").strip()
    if rp:
        app.include_router(router)
    else:
        app.include_router(router, prefix=prefix_if_missing)


def create_app() -> FastAPI:
    app = FastAPI(title="TPI_evoluto", version="0.1.0")

    @app.get("/healthz", tags=["system"])
    def healthz() -> dict:
        return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

    # DEMO (deve restare in OpenAPI)
    demo_real.mount(app)

    # CATALOGHI (in OpenAPI)
    _include_api(app, linee_vita_router, "/api/linee-vita")
    _include_api(app, inox_router, "/api/inox")

    # EXTRA (in OpenAPI)
    _include_api(app, funi_acciaio_router, "/api/funi-acciaio")
    _include_api(app, accessori_router, "/api/accessori")
    _include_api(app, formazione_router, "/api/formazione")

    return app


app = create_app()
