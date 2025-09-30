from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path

from .dpi_csv import router as csv_router

app = FastAPI(title="TPI evoluto — API + Site")

# API
app.include_router(csv_router)

# Statico su /site
site_dir = Path(__file__).resolve().parents[1] / "site"
if site_dir.exists():
    app.mount("/site", StaticFiles(directory=site_dir, html=True), name="site")

# Redirect root → /site/
@app.get("/", include_in_schema=False)
def _root():
    return RedirectResponse("/site/")
