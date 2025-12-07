from typing import Optional
import os

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# =========================================================
#  TPI_evoluto – MINI API STAGING (root + health + token)
# =========================================================

# --- Config base da env (solo info, non blocca) ---

TPI_ENV = os.getenv("TPI_ENV", "staging")
TPI_VERSION = os.getenv("TPI_VERSION", "v1")

# 🔐 Token STAGING FISSO (facile da ricordare e usare)
#  Quando vorrai cambiare, modifichi SOLO questa riga.
TPI_STAGING_TOKEN = "TPI-STAGING-LOCAL-SECRET"

# CORS di base (puoi restringere più avanti)
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


# --- Endpoint ---


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """
    Endpoint di salute pubblico (senza token).
    Usato da Render e dai CESARI per verificare che la staging sia viva.
    """
    return HealthResponse(
        status="ok",
        env=TPI_ENV,
        version=TPI_VERSION,
    )


@app.get("/", response_model=RootResponse)
def root(x_tpi_token: str = Header(default="", alias="X-TPI-Token")) -> RootResponse:
    """
    Root protetta da header X-TPI-Token.
    In STAGING accettiamo SOLO il token TPI_STAGING_TOKEN.
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
