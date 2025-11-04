# app/main.py
# ============================================================
# AELIS — Main FastAPI (stile ENTERPRISE, commenti abbondanti)
# - Logging coerente (livello da ENV: LOG_LEVEL)
# - Security middleware: X-Request-ID + header sicurezza
# - CORS: dev = "*" ; prod = lista esplicita (CORS_ALLOW_ORIGINS)
# - TrustedHost e HTTPS redirect in produzione (ALLOWED_HOSTS / ENV=prod)
# - Rate limit per-IP configurabile (RATE_BURST / RATE_WINDOW)
# - Exception handler uniformi con request-id nel log
# - Registrazione router tollerante (non blocca l’avvio)
# - Probes: /health, /healthz (UTC), /version (APP_VERSION/GIT_SHA/BUILD_TIME)
# ============================================================

from __future__ import annotations

# ----------------------------
# Import (devono stare in cima)
# ----------------------------
import logging
import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.middleware_security import (
    CorrelationIdMiddleware,
    SecurityHeadersMiddleware,
)
from app.middleware_rate_limit import RateLimitMiddleware

# ----------------------------
# Logging base (livello da ENV)
# ----------------------------
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
log = logging.getLogger("tpi.app")

# ----------------------------
# Metadati e versioning (ENV)
# ----------------------------
APP_VERSION = os.getenv("APP_VERSION", "dev")
GIT_SHA = os.getenv("GIT_SHA", "")
BUILD_TIME = os.getenv("BUILD_TIME", "")

# Ambiente e parametri security/rate limit
ENV = os.getenv("ENV", "dev").lower()
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "*").split(",") if h.strip()]
RATE_BURST = int(os.getenv("RATE_BURST", "5"))        # richieste massime per finestra
RATE_WINDOW = int(os.getenv("RATE_WINDOW", "60"))      # finestra in secondi

# ----------------------------
# Istanza FastAPI
# ----------------------------
app = FastAPI(
    title="TPI_evoluto",
    description="API TPI — CSV DPI, Health, Version",
    version=APP_VERSION,
    contact={"name": "TPI", "email": "sistemianticaduta@gmail.com"},
)

# --------------------------------------------------
# Middleware di sicurezza / governance
# (ordine importante: correlation → headers → https/hosts → CORS → rate-limit)
# --------------------------------------------------
# 1) Correlation-ID per audit (restituisce X-Request-ID in ogni risposta)
app.add_middleware(CorrelationIdMiddleware)

# 2) Security headers (HSTS solo in prod dietro HTTPS)
app.add_middleware(SecurityHeadersMiddleware, enable_hsts=(ENV == "prod"))

# 3) Redirect HTTPS e Trusted hosts (solo se produci)
if ENV == "prod":
    app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS or ["*"])

# 4) CORS: in prod usa lista esplicita; in dev consenti tutto
if ENV == "prod":
    _origins = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "").split(",") if o.strip()]
else:
    _origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5) Rate limit per-IP (protezione base da flood su upload/POST)
#    Aumenta RATE_BURST o riduci RATE_WINDOW in ambienti interni se serve.
app.add_middleware(RateLimitMiddleware, burst=RATE_BURST, window_sec=RATE_WINDOW)

# --------------------------------------------------
# Exception handlers (risposte coerenti e log utili)
# --------------------------------------------------
def _reqid(request: Request) -> str:
    # header scritto dal CorrelationIdMiddleware
    return request.headers.get("x-request-id", "-")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    log.warning(
        "HTTP %s %s → %s (req:%s)",
        request.method, request.url.path, exc.detail, _reqid(request)
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log.exception("Unhandled error on %s %s (req:%s)", request.method, request.url.path, _reqid(request))
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

# --------------------------------------------------
# Registrazione router (tollerante ai moduli mancanti)
# --------------------------------------------------
# Router "storico" (già presente nel progetto) → /api/dpi/csv/*
try:
    from app.dpi_csv import router as csv_router  # type: ignore
    app.include_router(csv_router)
    log.info("Router storico registrato: /api/dpi/csv/*")
except Exception as e:
    log.warning("Router storico app.dpi_csv non disponibile: %s", e)

# Nuovi router CSV (import-file + export filtrato)
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

# Router ops (healthz, version)
try:
    from routers import ops  # /healthz, /version
    app.include_router(ops.router)
    log.info("Router ops registrato")
except Exception as e:
    log.warning("Impossibile registrare routers.ops: %s", e)

# --------------------------------------------------
# Probes "semplici" (retro-compatibilità + info)
# --------------------------------------------------
@app.get("/health")
def health() -> dict:
    """Probe semplice mantenuta per retro-compatibilità (ambiente legacy)."""
    return {"status": "ok"}

@app.get("/healthz")
def healthz() -> dict:
    """Probe preferita in ambienti moderni, con timestamp UTC ISO 8601."""
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

@app.get("/version")
def version() -> dict:
    """Info versione leggibili anche da automazioni/monitoring."""
    return {
        "app": "TPI_evoluto",
        "version": APP_VERSION,
        "git_sha": GIT_SHA,
        "build_time": BUILD_TIME,
    }

# --------------------------------------------------
# Lifecycle hooks (startup/shutdown) per log puliti
# --------------------------------------------------
@app.on_event("startup")
async def on_startup():
    log.info(
        "TPI_evoluto avviata — env=%s version=%s sha=%s build_time=%s",
        ENV, APP_VERSION, GIT_SHA, BUILD_TIME
    )

@app.on_event("shutdown")
async def on_shutdown():
    log.info("TPI_evoluto arresto in corso…")
