# ============================================================
# AELIS — FastAPI main (robusto per dev/prod)
#
# - Config da ENV (LOG_LEVEL, ENV, CORS, rate limit, ecc.)
# - Correlation-ID + security headers (HSTS solo in prod)
# - HTTPS redirect & TrustedHost SOLO in prod
# - CORS:
#     * dev  → allow_origins=["*"], no credenziali
#     * prod → lista esplicita da ENV
# - Rate limit per-IP (burst/finestra da ENV) in-memory
# - Handler eccezioni uniformi (con X-Request-ID / X-Correlation-ID)
# - Registrazione router tollerante a moduli mancanti
# - Probes: /health, /healthz (UTC), /version
# - Endpoint /debug/routes in dev
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
# Middleware custom (inline)
# --------------------------------------------------
class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Genera / propaga un X-Request-ID su ogni richiesta.

    - Legge da header esistenti (x-request-id, x-correlation-id)
    - Se assente, genera un UUID4
    - Espone request.state.request_id
    """

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
    """
    Aggiunge header di sicurezza base.
    HSTS abilitato solo se enable_hsts=True (prod).
    """

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
    """
    Rate limit grezzo per-IP (in-memory, single-process).
    Adatto per dev / piccole installazioni on-prem.
    """

    def __init__(self, app: ASGIApp, burst: int, window_sec: int) -> None:
        super().__init__(app)
        self.burst = max(burst, 1)
        self.window = float(max(window_sec, 1))
        self._hits: dict[str, list[float]] = {}
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
# Lifespan (startup/shutdown moderno)
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
    description="API TPI — Catalogo DPI, Health, Version, NFC",
    version=APP_VERSION,
    contact={"name": "TPI", "email": "sistemianticaduta@gmail.com"},
    lifespan=lifespan,
)


# --------------------------------------------------
# Helpers / exception handlers
# --------------------------------------------------
def _reqid(request: Request) -> str:
    for key in ("x-request-id", "x-correlation-id"):
        v = request.headers.get(key)
        if v:
            return v
    return getattr(request.state, "request_id", "-")


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    log.warning(
        "HTTP %s %s → %s (req:%s)",
        request.method,
        request.url.path,
        exc.detail,
        _reqid(request),
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    log.exception(
        "Unhandled error on %s %s (req:%s)",
        request.method,
        request.url.path,
        _reqid(request),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


# --------------------------------------------------
# Registrazione router (tollerante)
# --------------------------------------------------
def _include_optional_router(import_path: str, description: str) -> None:
    """
    Import dinamico tollerante per router FastAPI.

    import_path es. "app.dpi_csv:router"
    """
    try:
        module_path, attr_name = import_path.split(":", 1)
        module = importlib.import_module(module_path)
        router = getattr(module, attr_name)
        app.include_router(router)
        log.info("Router %s registrato (%s)", import_path, description)
    except Exception as exc:  # pragma: no cover
        log.warning(
            "Impossibile registrare router %s (%s): %s",
            import_path,
            description,
            exc,
        )


# Router storico Catalogo DPI → /api/dpi/csv/*
_include_optional_router(
    "app.dpi_csv:router",
    "Router storico CSV DPI (/api/dpi/csv/*)",
)

# Nuovi router CSV (import/export evoluti) se presenti
_include_optional_router(
    "routers.csv_import:router",
    "Import CSV avanzato (POST /api/dpi/csv/import-file)",
)
_include_optional_router(
    "routers.csv_export_filtered:router",
    "Export filtrato (GET /api/dpi/csv/export?gruppo=...)",
)

# Router ops: /healthz, /version, eventuali metriche
_include_optional_router(
    "routers.ops:router",
    "Ops /healthz /version",
)

# Router NFC (landing / log accessi / deep link app)
_include_optional_router(
    "routers.nfc_routes:router",
    "NFC landing / log / app open",
)


# --------------------------------------------------
# Middleware (ordine importante)
# --------------------------------------------------
# 1) Correlation-ID per audit
app.add_middleware(CorrelationIdMiddleware)

# 2) Security headers (HSTS solo in prod)
app.add_middleware(
    SecurityHeadersMiddleware,
    enable_hsts=(ENV == "prod"),
)

# 3) HTTPS redirect + Trusted hosts SOLO in prod
if ENV == "prod":
    app.add_middleware(HTTPSRedirectMiddleware)
    if not ALLOWED_HOSTS:
        ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS or ["*"],
)

# 4) CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=(ENV == "prod"),
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5) Rate limit per-IP
app.add_middleware(
    RateLimitMiddleware,
    burst=RATE_BURST,
    window_sec=RATE_WINDOW,
)


# --------------------------------------------------
# Probes
# --------------------------------------------------
@app.get("/health")
def health() -> Dict[str, Any]:
    """Probe semplice per retro-compatibilità."""
    return {"status": "ok"}


@app.get("/healthz")
def healthz() -> Dict[str, Any]:
    """Probe preferita con timestamp UTC ISO 8601."""
    return {
        "status": "ok",
        "time": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/version")
def version() -> Dict[str, Any]:
    """Info versione leggibili da automazioni / monitoring."""
    return {
        "app": "TPI_evoluto",
        "version": APP_VERSION,
        "git_sha": GIT_SHA,
        "build_time": BUILD_TIME,
        "env": ENV,
    }


# --------------------------------------------------
# Debug dev-only (non in prod)
# --------------------------------------------------
if ENV != "prod":

    @app.get("/debug/routes")
    def debug_routes() -> List[Dict[str, Any]]:
        """Lista dei path registrati, utile in dev per capire cosa è attivo."""
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
