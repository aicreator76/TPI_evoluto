from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
import time

from app.routers import home, api, dpi, sottogancio, funi_metalliche, funi_fibra, formazione, site
from tpi_logging import get_logger

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

logger = get_logger()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000
    logger.info(f"{request.method} {request.url.path} completed_in={duration:.2f}ms status={response.status_code}")
    return response

# Routers
app.include_router(home.router)
app.include_router(api.router)
app.include_router(dpi.router)
app.include_router(sottogancio.router)
app.include_router(funi_metalliche.router)
app.include_router(funi_fibra.router)
app.include_router(formazione.router)
app.include_router(site.router)
