from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

router = APIRouter(prefix="/sottogancio", tags=["sottogancio"])
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "..", "templates"))

@router.get("/", response_class=HTMLResponse, operation_id="sottogancio_home")
def sottogancio_home(request: Request):
    return templates.TemplateResponse("sottogancio.html", {"request": request})

@router.get("", include_in_schema=False)
def sottogancio_home_noslash(request: Request):
    return templates.TemplateResponse("sottogancio.html", {"request": request})
