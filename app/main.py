# app/main.py
# ============================================================
# AELIS — FastAPI main (robusto per prod/dev)
# - Log a livello da ENV: LOG_LEVEL
# - Correlation-ID + security headers (HSTS solo in prod)
# - HTTPS redirect & TrustedHost SOLO in prod
# - CORS: in dev "*" senza credenziali; in prod lista esplicita
# - Rate limit per-IP (burst/finestra da ENV)
# - Handler eccezioni uniformi con request-id
# - /health, /healthz (UTC), /version e "/" (ping veloce)
# - Registrazione router tollerante a moduli mancanti
# - Startup/shutdown via lifespan (moderno)
# ============================================================

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.middleware_security import CorrelationIdMiddleware, SecurityHeadersMiddleware
from app.middleware_rate_limit import RateLimitMiddleware

# ----------------------------
# Config da ENV
# ----------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
APP_VERSION = os.getenv("APP_VERSION", "dev")
GIT_SHA = os.getenv("GIT_SHA", "")
BUILD_TIME = os.getenv("BUILD_TIME", "")
ENV = os.getenv("ENV", "dev").lower()

# ALLOWED_HOSTS: stringa tipo "example.com,api.example.com" oppure "*"
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("ALLOWED_HOSTS", "*").split(",") if h.strip()
]

# Rate-limit
RATE_BURST = int(os.getenv("RATE_BURST", "5"))
RATE_WINDOW = int(os.getenv("RATE_WINDOW", "60"))

# ----------------------------
# Logging
# ----------------------------
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
log = logging.getLogger("tpi.app")


# ----------------------------
# Lifespan (startup/shutdown)
# ----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
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


# ----------------------------
# App
# ----------------------------
app = FastAPI(
    title="TPI_evoluto",
    description="API TPI — CSV DPI, Health, Version",
    version=APP_VERSION,
    contact={"name": "TPI", "email": "sistemianticaduta@gmail.com"},
    lifespan=lifespan,
)

# --------------------------------------------------
# Middleware
#   ordine: correlation → headers → https/hosts → CORS → rate-limit
# --------------------------------------------------
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(SecurityHeadersMiddleware, enable_hsts=(ENV == "prod"))

# HTTPS redirect + Trusted hosts SOLO in prod (in dev spesso crea 400 indesiderati)
if ENV == "prod":
    app.add_middleware(HTTPSRedirectMiddleware)
    # se ALLOWED_HOSTS = ["*"] consenti tutto, altrimenti rispetta lista
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS or ["*"])

# CORS
if ENV == "prod":
    origins = [
        o.strip()
        for o in os.getenv("CORS_ALLOW_ORIGINS", "").split(",")
        if o.strip()
    ]
else:
    # In dev: wildcard senza credenziali (altrimenti Starlette rifiuta "*"+credentials)
    origins = ["*"]

allow_credentials = False if "*" in origins else True
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limit per-IP
app.add_middleware(RateLimitMiddleware, burst=RATE_BURST, window_sec=RATE_WINDOW)

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def _reqid(request: Request) -> str:
    return request.headers.get("x-request-id", "-")


# --------------------------------------------------
# Exception handlers
# --------------------------------------------------
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
# Router (tollerante)
# --------------------------------------------------
try:
    from app.dpi_csv import router as csv_router  # type: ignore

    app.include_router(csv_router)
    log.info("Router storico registrato: /api/dpi/csv/*")
except Exception as e:
    log.warning("Router storico app.dpi_csv non disponibile: %s", e)

try:
    from routers import csv_import  # POST /api/dpi/csv/import-file

    app.include_router(csv_import.router)
    log.info("Router csv_import registrato")
except Exception as e:
    log.warning("Impossibile registrare routers.csv_import: %s", e)

try:
    from routers import csv_export_filtered  # GET /api/dpi/csv/export?gruppo=...

    app.include_router(csv_export_filtered.router)
    log.info("Router csv_export_filtered registrato")
except Exception as e:
    log.warning("Impossibile registrare routers.csv_export_filtered: %s", e)

try:
    from routers import ops  # /healthz, /version

    app.include_router(ops.router)
    log.info("Router ops registrato")
except Exception as e:
    log.warning("Impossibile registrare routers.ops: %s", e)


# --------------------------------------------------
# Probes & info
# --------------------------------------------------
@app.get("/")
def root() -> dict:
    return {"status": "ok", "app": "TPI_evoluto", "version": APP_VERSION}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/version")
def version() -> dict:
    return {
        "app": "TPI_evoluto",
        "version": APP_VERSION,
        "git_sha": GIT_SHA,
        "build_time": BUILD_TIME,
    }
