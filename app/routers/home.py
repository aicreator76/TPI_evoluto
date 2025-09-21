from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "..", "templates"))

@router.get("/", response_class=HTMLResponse, operation_id="home_root")
def home_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
