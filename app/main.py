from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Routers
from app.routers.home import router as home_router
from app.routers.api import router as api_router
from app.routers.dpi import router as dpi_router
from app.routers.sottogancio import router as sottogancio_router
from app.routers.funi_metalliche import router as funi_metalliche_router
from app.routers.funi_fibra import router as funi_fibra_router
from app.routers.formazione import router as formazione_router
from app.routers.site import router as site_router

# redirect_slashes=True per accettare /sezione e /sezione/
app = FastAPI(title="TPI_evoluto", redirect_slashes=True)

# Statici: cartella "static" nella root del progetto
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include router
app.include_router(home_router)
app.include_router(api_router)
app.include_router(dpi_router)
app.include_router(sottogancio_router)
app.include_router(funi_metalliche_router)
app.include_router(funi_fibra_router)
app.include_router(formazione_router)
app.include_router(site_router)
