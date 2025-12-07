from typing import Optional
import os

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# =========================================================
#  TPI_evoluto – MINI API STAGING
#  - /health  → pubblico, no token (monitoring)
#  - /       → root protetta da X-TPI-Token
# =========================================================

# --- Config base da env (con default sicuri per STAGING) ---

TPI_ENV = os.getenv("TPI_ENV", "staging")
TPI_VERSION = os.getenv("TPI_VERSION", "v1")

# 🔐 Token STAGING:
# - se TPI_STAGING_TOKEN non è definito nella env,
#   usiamo il default storico TPI-STAGING-LOCAL-SECRET
TPI_STAGING_TOKEN = os.getenv("TPI_STAGING_TOKEN", "TPI-STAGING-LOCAL-SECRET")

# CORS: in STAGING va bene "*" (più avanti si restringe)
TPI_ALLOWED_ORIGINS = os.getenv("TPI_ALLOWED_ORIGINS", "*")


# --- FastAPI app ---

app = FastAPI(
    title="TPI_evoluto – staging mini API",
    version=TPI_VERSION,
)

if TPI_ALLOWED_ORIGINS == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [o.strip() for o in TPI_ALLOWED_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Schemi di risposta ---


class HealthResponse(BaseModel):
    status: str
    env: str
    version: str


class RootResponse(BaseModel):
    status: str
    env: str
    version: str
    message: Optional[str] = None


# --- Endpoint /health (pubblico) ---


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """
    Endpoint di salute pubblico.
    Usato da Render e dai CESARI per verificare che la staging sia viva.
    """
    return HealthResponse(
        status="ok",
        env=TPI_ENV,
        version=TPI_VERSION,
    )


# --- Endpoint root "/" (protetto da X-TPI-Token) ---


@app.get("/", response_model=RootResponse)
def root(x_tpi_token: str = Header(default="", alias="X-TPI-Token")) -> RootResponse:
    """
    Root protetta da header X-TPI-Token.
    In STAGING accettiamo SOLO il token configurato TPI_STAGING_TOKEN.
    """
    if not x_tpi_token or x_tpi_token != TPI_STAGING_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized – missing or invalid X-TPI-Token",
        )

    return RootResponse(
        status="ok",
        env=TPI_ENV,
        version=TPI_VERSION,
        message="TPI_evoluto staging root reachable",
    )
