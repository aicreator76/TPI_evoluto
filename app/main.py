# app/main.py
# ============================================================
# AELIS — Main FastAPI (stile ENTERPRISE, commenti abbondanti)
# - Logging coerente
# - CORS (dev-friendly, configurabile via env)
# - Handler errori uniformi (HTTPException / generico)
# - Registrazione router in try/except (non blocca l'avvio)
# - Probes: /health (retro), /healthz (con timestamp), /version
# - Startup/Shutdown log
# ============================================================

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

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
# CORS: in dev abilitiamo tutto; in prod restringere
# --------------------------------------------------
try:
    from fastapi.middleware.cors import CORSMiddleware

    # Configurabile via ENV (es: "http://localhost:5173,http://127.0.0.1:5173")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
except Exception:
    # Middleware opzionale: se manca non blocchiamo l'avvio
    pass

# --------------------------------------------------
# Exception handlers (risposte coerenti e log utili)
# --------------------------------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    log.warning("HTTP %s %s → %s", request.method, request.url.path, exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    log.exception("Unhandled error on %s %s", request.method, request.url.path)
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
        "TPI_evoluto avviata — version=%s sha=%s build_time=%s",
        APP_VERSION, GIT_SHA, BUILD_TIME
    )

@app.on_event("shutdown")
async def on_shutdown():
    log.info("TPI_evoluto arresto in corso…")

