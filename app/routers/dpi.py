from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

router = APIRouter(prefix="/dpi", tags=["dpi"])
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "..", "templates"))

# Home sezione DPI
@router.get("/", response_class=HTMLResponse, operation_id="dpi_home")
def dpi_home(request: Request):
    return templates.TemplateResponse("dpi.html", {"request": request})

@router.get("", include_in_schema=False)
def dpi_home_noslash(request: Request):
    return templates.TemplateResponse("dpi.html", {"request": request})

# --- Sottocapitoli ---
@router.get("/catalogo", response_class=HTMLResponse, operation_id="dpi_catalogo")
def dpi_catalogo(request: Request):
    return templates.TemplateResponse("dpi_catalogo.html", {"request": request})

@router.get("/consegna", response_class=HTMLResponse, operation_id="dpi_consegna")
def dpi_consegna(request: Request):
    return templates.TemplateResponse("dpi_consegna.html", {"request": request})

@router.get("/revisioni", response_class=HTMLResponse, operation_id="dpi_revisioni")
def dpi_revisioni(request: Request):
    return templates.TemplateResponse("dpi_revisioni.html", {"request": request})
