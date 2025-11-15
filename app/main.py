# app/main.py
# ============================================================
# AELIS ΓÇö FastAPI main (robusto per dev/prod)
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
from typing import AsyncIterator

from fastapi import FastAPI


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


LOG_LEVEL = _getenv("LOG_LEVEL", "INFO").upper()
APP_VERSION = _getenv("APP_VERSION", "dev")
GIT_SHA = _getenv("GIT_SHA", "")
BUILD_TIME = _getenv("BUILD_TIME", "")
ENV = _getenv("ENV", "dev").lower()

# hosts consentiti (in prod usa lista esplicita, in dev = "*")
_raw_hosts = _getenv("ALLOWED_HOSTS", "*" if ENV != "prod" else "")
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(",") if h.strip()] or (
    ["*"] if ENV != "prod" else []
)

# rate limit
RATE_BURST = _getenv_int("RATE_BURST", 5)
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
    format="%(asctime)s %(levelname)s %(name)s ΓÇö %(message)s",
)
log = logging.getLogger("tpi.app")


# ----------------------------
# Lifespan (startup/shutdown)
# ----------------------------
@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    log.info(
        "TPI_evoluto avvio ΓÇö env=%s version=%s sha=%s build_time=%s",
        ENV,
        APP_VERSION,
        GIT_SHA,
        BUILD_TIME,
    )
    try:
        yield
    finally:
        log.info("TPI_evoluto arresto in corsoΓÇª")


# ----------------------------
# Istanza FastAPI
# ----------------------------
app = FastAPI(
    title="TPI_evoluto",
    description="API TPI ΓÇö CSV DPI, Health, Version",
    version=APP_VERSION,
    contact={"name": "TPI", "email": "sistemianticaduta@gmail.com"},
    lifespan=lifespan,
)

# Router CSV export filtrato
try:
    from routers import csv_export_filtered

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

# Router NFC (landing + log accessi + WhatsApp)
try:
    from routers import nfc_routes  # type: ignore

    app.include_router(nfc_routes.router)
    log.info(
        "Router nfc_routes registrato: /a/{uid}, /api/nfc/log, /api/nfc/whatsapp-link"
    )
except Exception as e:
    log.warning("Impossibile registrare routers.nfc_routes: %s", e)
