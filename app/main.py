# app/main.py
# ============================================================
# AELIS — FastAPI main (robusto per dev/prod)
# - Log a livello da ENV: LOG_LEVEL
# - Correlation-ID + security headers (HSTS solo in prod)
# - HTTPS redirect & TrustedHost SOLO in prod
# - CORS: in dev "*" senza credenziali; in prod lista esplicita
# - Rate limit per-IP (burst/finestra da ENV)
# - Handler eccezioni uniformi (con X-Request-ID)
# - Registrazione router tollerante a moduli mancanti
# - Probes: /health, /healthz (UTC), /version
# - Startup/shutdown via lifespan (moderno)
# ============================================================

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncIterator

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
# Config da ENV (con fallback)
# ----------------------------
def _getenv(key: str, default: str) -> str:
    v = os.getenv(key)
    return v if v is not None and str(v).strip() != "" else default

def _getenv_int(key: str, default: int) -> int:
    try:
        return int(_getenv(key, str(default)))
    except ValueError:
        return default

LOG_LEVEL   = _getenv("LOG_LEVEL", "INFO").upper()
APP_VERSION = _getenv("APP_VERSION", "dev")
GIT_SHA     = _getenv("GIT_SHA", "")
BUILD_TIME  = _getenv("BUILD_TIME", "")
ENV         = _getenv("ENV", "dev").lower()

# hosts consentiti (in prod usa lista esplicita, in dev = "*")
_raw_hosts     = _getenv("ALLOWED_HOSTS", "*" if ENV != "prod" else "")
ALLOWED_HOSTS  = [h.strip() for h in _raw_hosts.split(",") if h.strip()] or (["*"] if ENV != "prod" else [])

# rate limit
RATE_BURST  = _getenv_int("RATE_BURST", 5)
RATE_WINDOW = _getenv_int("RATE_WINDOW", 60)

# CORS: in prod lista esplicita, in dev "*"
if ENV == "prod":
    _origins_env = _getenv("CORS_ALLOW_ORIGINS", "")
    CORS_ORIGINS = [o.strip() for o in _origins_env.split(",") if o.strip()]
else:
    CORS_ORIGINS = ["*"]

# ----------------------------
# Logging base
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
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    log.info(
        "TPI_evoluto avvio — env=%s version=%s sha=%s build_time=%s",
        ENV, APP_VERSION, GIT_SHA, BUILD_TIME
    )
    try:
        yield
    finally:
        log.info("TPI_evoluto arresto in corso…")

# ----------------------------
# Istanza FastAPI
# ----------------------------
app = FastAPI(
    title="TPI_evoluto",
    description="API TPI — CSV DPI, Health, Version",
    version=APP_VERSION,
    contact={"name": "TPI", "email": "sistemianticaduta@gmail.com"},
    lifespan=lifespan,
)
diff --git a/app/main.py b/app/main.py
index 1234567..89abcde 100644
--- a/app/main.py
+++ b/app/main.py
@@ -160,6 +160,16 @@ except Exception as e:
     log.warning("Impossibile registrare routers.csv_export_filtered: %s", e)
 
 # Router ops (healthz, version)
 try:
     from routers import ops  # /healthz, /version
     app.include_router(ops.router)
     log.info("Router ops registrato")
 except Exception as e:
     log.warning("Impossibile registrare routers.ops: %s", e)
 
+# Router NFC (landing + log accessi)
+try:
+    from routers import nfc_routes  # type: ignore
+    app.include_router(nfc_routes.router)
+    log.info("Router nfc_routes registrato: /a/{uid}, /api/nfc/log, /app/open")
+except Exception as e:
+    log.warning("Impossibile registrare routers.nfc_routes: %s", e)

# --------------------------------------------------
# Middleware (ordine importante)
# --------------------------------------------------
# 1) Correlation-ID per audit
app.add_middleware(CorrelationIdMiddleware)

# 2) Security headers (HSTS solo in prod)
app.add_middleware(SecurityHeadersMiddleware, enable_hsts=(ENV == "prod"))

# 3) HTTPS redirect & Trusted hosts SOLO in prod
if ENV == "prod":
    app.add_middleware(HTTPSRedirectMiddleware)
    # In prod devi elencare esplicitamente gli host (no "*")
    if not ALLOWED_HOSTS:
        # fallback sicuro per evitare blocchi se variabile non è impostata
        ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS or ["*"])

# 4) CORS
#    In dev: allow_origins=["*"] ma SENZA credenziali (sicurezza).
#    In prod: specifica i domini in CORS_ALLOW_ORIGINS, credenziali ammesse.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=(ENV == "prod"),
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5) Rate limit per-IP
app.add_middleware(RateLimitMiddleware, burst=RATE_BURST, window_sec=RATE_WINDOW)

# --------------------------------------------------
# Helpers / exception handlers
# --------------------------------------------------
def _reqid(request: Request) -> str:
    # header scritto dal CorrelationIdMiddleware
    return request.headers.get("x-request-id", "-")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    log.warning(
        "HTTP %s %s → %s (req:%s)",
        request.method, request.url.path, exc.detail, _reqid(request)
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    log.exception("Unhandled error on %s %s (req:%s)", request.method, request.url.path, _reqid(request))
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

# --------------------------------------------------
# Registrazione router (tollerante)
# --------------------------------------------------
# Router storico → /api/dpi/csv/*
try:
    from app.dpi_csv import router as csv_router  # type: ignore
    app.include_router(csv_router)
    log.info("Router storico registrato: /api/dpi/csv/*")
except Exception as e:
    log.warning("Router storico app.dpi_csv non disponibile: %s", e)

# Nuovi router CSV
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
# Probes
# --------------------------------------------------
@app.get("/health")
def health() -> dict:
    """Probe semplice per retro-compatibilità."""
    return {"status": "ok"}

@app.get("/healthz")
def healthz() -> dict:
    """Probe preferita con timestamp UTC ISO 8601."""
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

@app.get("/version")
def version() -> dict:
    """Info versione leggibili da automazioni/monitoring."""
    return {
        "app": "TPI_evoluto",
        "version": APP_VERSION,
        "git_sha": GIT_SHA,
        "build_time": BUILD_TIME,
    }
try:
    from routers import nfc_routes  # type: ignore
    app.include_router(nfc_routes.router)
    log.info("Router nfc_routes registrato")
except Exception as e:
    log.warning("Impossibile registrare routers.nfc_routes: %s", e)
