from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

router = APIRouter(prefix="/about", tags=["site"])
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "..", "templates"))

@router.get("/", response_class=HTMLResponse, operation_id="site_about")
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@router.get("", include_in_schema=False)
def about_page_noslash(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})
