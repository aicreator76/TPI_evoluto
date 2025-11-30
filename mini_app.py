import os
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


# ==========================
# CONFIGURAZIONE DI BASE
# ==========================

ENV: str = os.getenv("ENV", "local")
TPI_STAGING_TOKEN: str | None = os.getenv("TPI_STAGING_TOKEN")

# ALLOWED_ORIGINS può essere una lista separata da virgole in ENV,
# es: "http://localhost:3000,https://tpi-frontend-staging.vercel.app"
_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
if _raw_origins.strip() == "*":
    ALLOWED_ORIGINS: List[str] = ["*"]
else:
    ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]


# ==========================
# MIDDLEWARE DI SICUREZZA
# ==========================


async def token_guard_middleware(request: Request, call_next):
    """
    Protezione semplice per STAGING/PROD:
    - /health SEMPRE accessibile (monitoring)
    - se TPI_STAGING_TOKEN non è impostato -> nessun blocco (sviluppo locale)
    - altrimenti richiede header: X-TPI-Token: <token>
    """
    path = request.url.path

    # Endpoint sempre libero per health check
    if path.startswith("/health"):
        return await call_next(request)

    # Nessun token configurato -> non blocchiamo (utile in dev)
    if not TPI_STAGING_TOKEN:
        return await call_next(request)

    # Controllo header
    token = request.headers.get("X-TPI-Token")
    if token != TPI_STAGING_TOKEN:
        return JSONResponse(
            status_code=401,
            content={"detail": "Unauthorized – missing or invalid X-TPI-Token"},
        )

    return await call_next(request)


# ==========================
# APP FASTAPI
# ==========================

app = FastAPI(
    title="TPI Evoluto – Backend",
    version="0.1.0",
    description="Backend FastAPI per progetto TPI_evoluto (Camelot staging).",
)


# CORS pronto per frontend (Netlify/Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Token guard su tutte le richieste HTTP
app.middleware("http")(token_guard_middleware)


# ==========================
# ENDPOINTS BASE
# ==========================


@app.get("/health", tags=["system"])
def health():
    """
    Healthcheck semplice per Render / monitor.
    SEMPRE accessibile (anche senza token).
    """
    return {"status": "ok", "env": ENV}


@app.get("/", tags=["system"])
def root():
    """
    Endpoint root protetto da token (in staging/prod).
    Utile per verificare configurazione e versione.
    """
    return {
        "app": "TPI_evoluto backend",
        "env": ENV,
        "message": "Backend TPI_evoluto operativo",
        "docs": "/docs",
    }
