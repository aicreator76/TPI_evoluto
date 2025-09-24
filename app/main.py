from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config.roles import ROLES
from app.config.i18n import get_locale

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.middleware("http")
async def validate_role(request: Request, call_next):
    role = request.query_params.get("role")
    if role and role not in ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Ruolo '{role}' non valido. Ruoli disponibili: {', '.join(ROLES)}"
        )
    return await call_next(request)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    translations, lang = get_locale(request)
    role = request.query_params.get("role", ROLES[0])
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "translations": translations, "lang": lang, "role": role}
    )
