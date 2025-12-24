from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Iterable

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


def _route_exists(app: FastAPI, path: str, method: str) -> bool:
    m = method.upper()
    for r in app.routes:
        if getattr(r, "path", None) == path and m in getattr(r, "methods", set()):
            return True
    return False


def create_app() -> FastAPI:
    app = FastAPI(title="TPI_evoluto", version="0.1.0")

    # === CORS (GH Pages -> Render) ===
    origins_env = os.getenv("CORS_ALLOW_ORIGINS", "https://aicreator76.github.io")
    cors_origins = [o.strip() for o in origins_env.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # === SYSTEM ROUTES (compat + sanity) ===
    if not _route_exists(app, "/", "GET"):

        @app.get("/", tags=["system"])
        def root() -> dict[str, str]:
            return {"service": "tpi_evoluto", "status": "ok"}

    if not _route_exists(app, "/version", "GET"):

        @app.get("/version", tags=["system"])
        def version() -> dict[str, str]:
            return {"version": app.version}

    if not _route_exists(app, "/healthz", "GET"):

        @app.get("/healthz", tags=["system"])
        def healthz() -> dict[str, str]:
            return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

    # WOW dashboard chiama /health (non /healthz) -> alias
    if not _route_exists(app, "/health", "GET"):

        @app.get("/health", tags=["system"])
        def health() -> dict[str, str]:
            return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

    # === WOW COMPAT: endpoints attesi dal frontend (evita 404) ===
    # Nota: ora tornano [] così NON rompe niente. Poi li colleghiamo a CSV/DB.
    if not _route_exists(app, "/api/dpi/listino", "GET"):

        @app.get("/api/dpi/listino", tags=["wow_compat"])
        def wow_dpi_listino() -> list[dict[str, Any]]:
            return []

    if not _route_exists(app, "/api/accessori/listino", "GET"):

        @app.get("/api/accessori/listino", tags=["wow_compat"])
        def wow_accessori_listino() -> list[dict[str, Any]]:
            return []

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
            (dpi_csv_router, "/api/dpi_csv"),
        ],
    )

    return app


app = create_app()
