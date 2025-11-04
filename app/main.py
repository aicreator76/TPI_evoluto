from app.middleware_rate_limit import RateLimitMiddleware
@'
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
GIT_SHA = os.getenv("GIT_
