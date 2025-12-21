from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI

from app.api.inox import router as inox_router
from app.api.funi_acciaio import router as funi_acciaio_router
from app.api.linee_vita import router as linee_vita_router
from app.routers import demo_real


def create_app() -> FastAPI:
    app = FastAPI(title="TPI_evoluto", version="0.1.0")

    @app.get("/healthz", tags=["system"])
    def healthz() -> dict:
        return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

    # DEMO (deve restare in OpenAPI)
    demo_real.mount(app)

    # CATALOGHI (in OpenAPI)
    app.include_router(linee_vita_router, prefix="/api/linee-vita")
    app.include_router(inox_router, prefix="/api/inox")
    app.include_router(funi_acciaio_router, prefix="/api/funi-acciaio")
    return app


app = create_app()
