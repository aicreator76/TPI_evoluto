# app/main.py
# ============================================================
# AELIS — Main FastAPI (stile ENTERPRISE, commenti abbondanti)
# - Logging coerente (livello da ENV: LOG_LEVEL)
# - Security middleware: X-Request-ID + header sicurezza
# - CORS: dev = "*" ; prod = lista esplicita (CORS_ALLOW_ORIGINS)
# - TrustedHost e HTTPS redirect in produzione (ALLOWED_HOSTS / ENV=prod)
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
ENV = os.getenv("ENV", "dev").lower()  # dev | prod

# ----------------------------
# OpenAPI metadata / tags
# ----------------------------
OPENAPI_TAGS = [
    {"name": "CSV", "description": "Catalogo DPI (template/import/export)"},
    {"name": "Ops", "description": "Operazioni di servizio (health/version)"},
]

# ----------------------------
# Istanza FastAPI
# ----------------------------
app = FastAPI(
    title="TPI_evoluto",
    description="API TPI — CSV DPI, Health, Version",
    version=APP_VERSION,
    contact={"name": "TPI", "email": "sistemianticaduta@gmail.com"},
    openapi_tags=OPENAPI_TAGS,
)

# --------------------------------------------------
# Security middleware (sempre attivi)
# --------------------------------------------------
# Correlation-ID (propaga X-Request-ID in risposta)
app.add_middleware(CorrelationIdMiddleware)
# Header sicurezza comuni; HSTS solo in produzione (dietro HTTPS)
app.add_middleware(SecurityHeadersMiddleware, enable_hsts=(ENV == "prod"))

# --------------------------------------------------
# HTTPS redirect & TrustedHost
# --------------------------------------------------
# In produzione: forziamo HTTPS e limitiamo gli host consentiti.
if ENV == "prod":
    app.add_middleware(HTTPSRedirectMiddleware)

allowed_hosts = os.getenv("ALLOWED_HOSTS", "*").split(",")
# Esempi validi: "tpi.example.com,*.azienda.it"
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# --------------------------------------------------
# CORS: dev = tutto; prod = lista esplicita
# --------------------------------------------------
if ENV == "prod":
    allow_origins = [o for o in os.getenv("CORS_ALLOW_ORIGINS", "").split(",") if o]
    if not allow_origins:
        # Se non metti origin in prod, di fatto blocchi tutte le origini → meglio warn esplicito.
        log.warning(
            "CORS in PROD senza CORS_ALLOW_ORIGINS impostato: nessun origin consentito"
        )
else:
    allow_origins = ["*"]  # sviluppo: massima flessibilità

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Exception handlers (risposte coerenti e log utili)
# --------------------------------------------------
def _reqid(request: Request) -> str:
    """Estrae l'X-Request-ID impostato dal middleware (se assente ritorna "-")."""
    return request.headers.get("x-request-id", "-")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    log.warning(
        "HTTP %s %s → %s (rid=%s)",
        request.method,
        request.url.path,
        exc.detail,
        _reqid(request),
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log.exception(
        "Unhandled error on %s %s (rid=%s)",
        request.method,
        request.url.path,
        _reqid(request),


@app.on_event("shutdown")
async def on_shutdown():
    log.info("TPI_evoluto arresto in corso")
