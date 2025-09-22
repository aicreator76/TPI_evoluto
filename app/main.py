from fastapi import FastAPI, Request, Request
from fastapi.staticfiles import StaticFiles
import time

# Router
from app.routers import (
    home as home_router,
    api as api_router,
    dpi as dpi_router,
    sottogancio as sottogancio_router,
    funi_metalliche as funi_metalliche_router,
    funi_fibra as funi_fibra_router,
    formazione as formazione_router,
    site as site_router,
)

from tpi_logging import get_logger

# App FastAPI
app = FastAPI(title="TPI_evoluto", redirect_slashes=True)

# Statici: cartella "static" nella root del progetto
app.mount("/static", StaticFiles(directory="static"), name="static")

# Logger
logger = get_logger()

# Middleware di logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000
    logger.info(
        f"{request.method} {request.url.path} completed_in={duration:.2f}ms status={response.status_code}"
    )
    return response

# Includi router
app.include_router(home_router.router)
app.include_router(api_router.router)
app.include_router(dpi_router.router)
app.include_router(sottogancio_router.router)
app.include_router(funi_metalliche_router.router)
app.include_router(funi_fibra_router.router)
app.include_router(formazione_router.router)
app.include_router(site_router.router)

from app.config.i18n import get_locale
@app.middleware("http")
async def add_locale_to_request(request: Request, call_next):
    request.state.locale = get_locale(request)
    response = await call_next(request)
    return response
