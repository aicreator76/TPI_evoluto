import os
from fastapi import Request
from fastapi.responses import JSONResponse

# Legge il token dall'ambiente: TPI_STAGING_TOKEN
TPI_STAGING_TOKEN = os.getenv("TPI_STAGING_TOKEN")


async def token_guard_middleware(request: Request, call_next):
    """
    Middleware semplice:
    - /health SEMPRE accessibile
    - se TPI_STAGING_TOKEN non è impostato → nessun blocco (utile in locale)
    - altrimenti richiede header: X-TPI-Token: <token>
    """
    # Endpoint sempre libero (healthcheck)
    if request.url.path.startswith("/health"):
        return await call_next(request)

    # Se non c'è token configurato, non blocchiamo (sviluppo)
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
