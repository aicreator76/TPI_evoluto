## ============================================================
# AELIS — FastAPI main (robusto per dev/prod)
#
# - Config da ENV (LOG_LEVEL, ENV, CORS, rate limit, ecc.)
# - Modalità DEV senza token (TPI_DEV_NO_AUTH=1) → gestita nei router
# - Correlation-ID + security headers
# - HSTS / HTTPS redirect SOLO in prod
# - CORS dinamico
# - Rate limit per-IP
# - Handler eccezioni uniformi
# - Auth JWT dev (/auth/token)
# - Router modulari con import tollerante
# - Health probe, version, debug routes
# ============================================================

from __future__ import annotations

import asyncio
import importlib
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Dict, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.types import ASGIApp

# Router auth interno
from app.auth.router import router as auth_router

# Router ACCESSORI 3.0 (import esplicito, niente sorprese)
from app.api import accessori_listino as accessori_listino_router


# --------------------------------------------------
# Helpers ENV
# --------------------------------------------------
def _getenv(key: str, default: str) -> str:
    value = os.getenv(key)
    if value is None:
        return default
    value = str(value).strip()
    return value if value else default


def _getenv_int(key: str, default: int) -> int:
    raw = _getenv(key, str(default))
    try:
        return int(raw)
    except ValueError:
        return default


# --------------------------------------------------
# Config applicativa
# --------------------------------------------------
LOG_LEVEL = _getenv("LOG_LEVEL", "INFO").upper()
APP_VERSION = _getenv("APP_VERSION", "dev")
GIT_SHA = _getenv("GIT_SHA", "")
BUILD_TIME = _getenv("BUILD_TIME", "")
ENV = _getenv("ENV", "dev").lower()

# Host consentiti
_raw_hosts = _getenv("ALLOWED_HOSTS", "*" if ENV != "prod" else "")
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(",") if h.strip()] or (
    ["*"] if ENV != "prod" else []
)

# Rate limit
RATE_BURST = _getenv_int("RATE_BURST", 5)
RATE_WINDOW = _getenv_int("RATE_WINDOW", 60)

# CORS
if ENV == "prod":
    _origins_env = _getenv("CORS_ALLOW_ORIGINS", "")
    CORS_ORIGINS = [o.strip() for o in _origins_env.split(",") if o.strip()]
else:
    CORS_ORIGINS = ["*"]


# --------------------------------------------------
# Logging base
# --------------------------------------------------
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
log = logging.getLogger("tpi.app")


# --------------------------------------------------
# Middleware custom
# --------------------------------------------------
class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Genera / propaga un X-Request-ID su ogni richiesta."""

    def __init__(self, app: ASGIApp, header_name: str = "x-request-id") -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        req_id = (
            request.headers.get(self.header_name)
            or request.headers.get("x-correlation-id")
            or str(uuid.uuid4())
        )
        request.state.request_id = req_id
        response = await call_next(request)
        response.headers.setdefault(self.header_name, req_id)
        response.headers.setdefault("x-correlation-id", req_id)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Aggiunge header di sicurezza standard (HSTS solo in prod)."""

    def __init__(self, app: ASGIApp, enable_hsts: bool = False) -> None:
        super().__init__(app)
        self.enable_hsts = enable_hsts

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        response = await call_next(request)
        headers = response.headers

        headers.setdefault("X-Content-Type-Options", "nosniff")
        headers.setdefault("X-Frame-Options", "DENY")
        headers.setdefault("X-XSS-Protection", "1; mode=block")
        headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=()",
        )

        if self.enable_hsts:
            headers.setdefault(
                "Strict-Transport-Security",
                "max-age=63072000; includeSubDomains; preload",
            )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limit semplice per-IP (dev/on-prem)."""

    def __init__(self, app: ASGIApp, burst: int, window_sec: int) -> None:
        super().__init__(app)
        self.burst = max(burst, 1)
        self.window = float(max(window_sec, 1))
        self._hits: dict[str, List[float]] = {}
        self._lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        async with self._lock:
            hits = self._hits.get(client_ip, [])
            hits = [ts for ts in hits if now - ts <= self.window]
            if len(hits) >= self.burst:
                log.warning("Rate limit superato per %s", client_ip)
                raise HTTPException(status_code=429, detail="Too Many Requests")

            hits.append(now)
            self._hits[client_ip] = hits

        return await call_next(request)


# --------------------------------------------------
# Lifespan
# --------------------------------------------------
@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    log.info(
        "TPI_evoluto avvio — env=%s version=%s sha=%s build_time=%s",
        ENV,
        APP_VERSION,
        GIT_SHA,
        BUILD_TIME,
    )
    try:
        yield
    finally:
        log.info("TPI_evoluto arresto in corso…")


# --------------------------------------------------
# Istanza FastAPI
# --------------------------------------------------
app = FastAPI(
    title="TPI_evoluto",
    description="API TPI — Catalogo DPI, Funi in fibra, Accessori, NFC, Auth",
    version=APP_VERSION,
    contact={"name": "TPI", "email": "sistemianticaduta@gmail.com"},
    lifespan=lifespan,
)


# --------------------------------------------------
# Exception handlers
# --------------------------------------------------
def _reqid(request: Request) -> str:
    return (
        request.headers.get("x-request-id")
        or request.headers.get("x-correlation-id")
        or getattr(request.state, "request_id", "-")
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    log.warning(
        "HTTP %s %s → %s (req:%s)",
        request.method,
        request.url.path,
        exc.detail,
        _reqid(request),
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log.exception(
        "Unhandled error on %s %s (req:%s)",
        request.method,
        request.url.path,
        _reqid(request),
    )
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


# --------------------------------------------------
# Registrazione router (modulare, tollerante)
# --------------------------------------------------
def _include_optional_router(import_path: str, description: str) -> None:
    try:
        module_path, attr_name = import_path.split(":", 1)
        module = importlib.import_module(module_path)
        router = getattr(module, attr_name)
        app.include_router(router)
        log.info("Router %s registrato (%s)", import_path, description)
    except Exception as exc:
        log.warning(
            "Impossibile registrare router %s (%s): %s",
            import_path,
            description,
            exc,
        )


# Router fondamentali
app.include_router(auth_router)
log.info("Router auth registrato (/auth/*)")

_include_optional_router("app.dpi_csv:router", "Router storico CSV DPI")
_include_optional_router("app.routers.csv_import:router", "Import CSV evoluto DPI")
_include_optional_router("app.routers.csv_export_filtered:router", "Export filtrato DPI")
_include_optional_router("app.routers.ops:router", "Healthz / Version")
_include_optional_router("app.routers.nfc_routes:router", "NFC landing")
_include_optional_router("app.api.funi_fibra:router", "Catalogo funi in fibra")

# Router ACCESSORI 3.0 — montato in modo esplicito (prefix già nel file)
app.include_router(accessori_listino_router.router)
log.info("Router accessori_listino registrato (/api/accessori/* — Listino 3.0 Accessori)")


# --------------------------------------------------
# Middleware (ordine corretto)
# --------------------------------------------------
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(SecurityHeadersMiddleware, enable_hsts=(ENV == "prod"))

if ENV == "prod":
    app.add_middleware(HTTPSRedirectMiddleware)
    if not ALLOWED_HOSTS:
        ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS or ["*"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=(ENV == "prod"),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    RateLimitMiddleware,
    burst=RATE_BURST,
    window_sec=RATE_WINDOW,
)


# --------------------------------------------------
# Helpers introspezione rotte
# --------------------------------------------------
def _list_route_paths() -> List[str]:
    """Ritorna l'elenco dei path registrati (unico, ordinato)."""
    paths: set[str] = set()
    for r in app.routes:
        path = getattr(r, "path", None)
        if path:
            paths.add(path)
    return sorted(paths)


# --------------------------------------------------
# Endpoint base
# --------------------------------------------------
@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "app": "TPI_evoluto",
        "env": ENV,
        "version": APP_VERSION,
        "git_sha": GIT_SHA,
        "build_time": BUILD_TIME,
        "routes": _list_route_paths(),
        "docs": {
            "openapi": "/openapi.json",
            "swagger_ui": "/docs",
            "redoc": "/redoc",
        },
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}


@app.get("/healthz")
def healthz() -> Dict[str, Any]:
    return {
        "status": "ok",
        "time": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/version")
def version() -> Dict[str, Any]:
    return {
        "app": "TPI_evoluto",
        "version": APP_VERSION,
        "git_sha": GIT_SHA,
        "build_time": BUILD_TIME,
        "env": ENV,
    }


# --------------------------------------------------
# Debug solo in dev
# --------------------------------------------------
if ENV != "prod":

    @app.get("/debug/routes")
    def debug_routes() -> List[Dict[str, Any]]:
        descr: List[Dict[str, Any]] = []
        for r in app.routes:
            descr.append(
                {
                    "path": getattr(r, "path", None),
                    "name": getattr(r, "name", None),
                    "methods": sorted(getattr(r, "methods", []) or []),
                }
            )
        return descr
