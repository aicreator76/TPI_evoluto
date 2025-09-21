from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

router = APIRouter(prefix="/funi_fibra", tags=["funi_fibra"])
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "..", "templates"))

@router.get("/", response_class=HTMLResponse, operation_id="funi_fibra_home")
def funi_fibra_home(request: Request):
    return templates.TemplateResponse("funi_fibra.html", {"request": request})

@router.get("", include_in_schema=False)
def funi_fibra_home_noslash(request: Request):
    return templates.TemplateResponse("funi_fibra.html", {"request": request})
