from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Iterable

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.accessori import router as accessori_router
from app.api.formazione import router as formazione_router
from app.api.funi_acciaio import router as funi_acciaio_router
from app.api.inox import router as inox_router
from app.api.linee_vita import router as linee_vita_router
from app.orchestrator.router import router as orchestrator_router
from app.admin.router import router as admin_router
from app.routers import demo_real
from app.routers.dpi_csv import router as dpi_csv_router

logger = logging.getLogger("tpi_evoluto")


def _norm_prefix(p: str) -> str:
    p = (p or "").strip()
    return "" if not p else "/" + p.strip("/")


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


def _parse_cors_origins(raw: str) -> tuple[list[str], bool]:
    """
    Returns: (origins, is_wildcard)
    raw example: "https://aicreator76.github.io,http://localhost:3000,null"
    """
    raw = (raw or "").strip()
    if not raw:
        return ([], False)

    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if "*" in parts:
        return (["*"], True)

    return (parts, False)


WOW_DPI_DEMO: list[dict[str, Any]] = [
    {
        "codice": "DPI-ELM-001",
        "descrizione": "Elmetto dielettrico EN 397 con jugulare",
        "famiglia": "TESTA",
        "giorni": 120,
        "revisione_ok": True,
        "ultima_rev": "2025-12-12",
    },
    {
        "codice": "DPI-IMB-002",
        "descrizione": "Imbracatura anticaduta 2 punti con anello dorsale",
        "famiglia": "ANTICADUTA",
        "giorni": 45,
        "revisione_ok": True,
        "ultima_rev": "2025-11-20",
    },
    {
        "codice": "DPI-CON-003",
        "descrizione": "Cordino doppio con assorbitore",
        "famiglia": "ANTICADUTA",
        "giorni": -5,
        "revisione_ok": False,
        "ultima_rev": "2025-09-10",
    },
]

WOW_ACCESSORI_DEMO: list[dict[str, Any]] = [
    {
        "codice": "ACC-MOS-010",
        "descrizione": "Moschettone tripla sicurezza",
        "famiglia": "CONNETTORI",
        "disponibilita": "Disponibile",
    },
    {
        "codice": "ACC-ANC-020",
        "descrizione": "Ancoraggio provvisorio fettuccia",
        "famiglia": "ANCORAGGI",
        "disponibilita": "Stock limitato",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œsafeÃƒÂ¢Ã¢â€šÂ¬Ã‚Â: crea tabelle minime se richiesto (utile in dev/SQLite).
    Disattivabile: AUTO_INIT_DB=0
    """
    auto_init = os.getenv("AUTO_INIT_DB", "1").strip() not in {"0", "false", "False", "no", "NO"}
    if auto_init:
        try:
            import app.db.models as _db_models  # noqa: F401
            from app.db.base import Base
            from app.db.session import engine

            Base.metadata.create_all(bind=engine)
            logger.info("DB init OK: create_all eseguito")
        except Exception:
            logger.exception("DB init FAILED (create_all). Proseguo comunque.")
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="TPI_evoluto", version="0.1.0", lifespan=lifespan)

    # CORS
    origins_env = os.getenv("CORS_ALLOW_ORIGINS", "https://aicreator76.github.io,null")
    cors_origins, is_wildcard = _parse_cors_origins(origins_env)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins if cors_origins else [],
        allow_credentials=False,  # con "*" deve restare False
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Handler generico 500 (logga)
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        # In dev puoi cambiare in {"detail": str(exc)} ma qui restiamo safe
        return JSONResponse(status_code=500, content={"detail": "internal_server_error"})

    # System endpoints
    if not _route_exists(app, "/", "GET"):

        @app.get("/", tags=["system"])
        def root() -> dict[str, str]:
            return {"service": "tpi_evoluto", "status": "ok"}

    if not _route_exists(app, "/version", "GET"):

        @app.get("/version", tags=["system"])
        def version() -> dict[str, str]:
            commit = (
                os.getenv("RENDER_GIT_COMMIT")
                or os.getenv("GIT_COMMIT")
                or os.getenv("COMMIT_SHA")
                or "unknown"
            )
            return {"version": app.version, "commit": commit}

    if not _route_exists(app, "/healthz", "GET"):

        @app.get("/healthz", tags=["system"])
        def healthz() -> dict[str, str]:
            return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

    if not _route_exists(app, "/health", "GET"):

        @app.get("/health", tags=["system"])
        def health() -> dict[str, str]:
            return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

    # WOW compat demo endpoints
    if not _route_exists(app, "/api/dpi/listino", "GET"):

        @app.get("/api/dpi/listino", tags=["wow_compat"])
        def wow_dpi_listino() -> list[dict[str, Any]]:
            return WOW_DPI_DEMO

    if not _route_exists(app, "/api/accessori/listino", "GET"):

        @app.get("/api/accessori/listino", tags=["wow_compat"])
        def wow_accessori_listino(limit: int = 50, offset: int = 0) -> dict[str, Any]:
            items = WOW_ACCESSORI_DEMO[offset : offset + limit]
            return {
                "limit": limit,
                "offset": offset,
                "total": len(WOW_ACCESSORI_DEMO),
                "items": items,
            }

        @app.get("/api/accessori/listino/by-code/{codice}", tags=["wow_compat"])
        def wow_accessori_listino_by_code(codice: str) -> Any:
            for it in WOW_ACCESSORI_DEMO:
                c = it.get("codice") or it.get("code") or it.get("sku")
                if c == codice:
                    return {"found": True, "item": it}
            return JSONResponse(status_code=404, content={"found": False, "item": None})

    # Demo routes (sempre montate)
    demo_real.mount(app)

    # API routers
    _include_many(
        app,
        [
            (linee_vita_router, "/api/linee-vita"),
            (inox_router, "/api/inox"),
            (funi_acciaio_router, "/api/funi-acciaio"),
            (accessori_router, "/api/accessori"),
            (formazione_router, "/api/formazione"),
            (dpi_csv_router, "/api/dpi_csv"),
            (orchestrator_router, "/api/orchestrator"),
        ],
    )
    app.include_router(admin_router, prefix="/admin")
    return app


app = create_app()
