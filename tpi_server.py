from __future__ import annotations
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from tpi_logging import setup_logging

logger = setup_logging()
app = FastAPI(title="TPI evoluto", version="0.1.0")

BASE_DIR   = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
TPL_DIR    = os.path.join(BASE_DIR, "templates")
FAVICON    = os.path.join(STATIC_DIR, "favicon.ico")

if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def _read(path:str)->str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/", response_class=HTMLResponse)
def home(_: Request):
    index = os.path.join(TPL_DIR, "index.html")
    if os.path.isfile(index):
        return HTMLResponse(_read(index))
    return HTMLResponse("<h1>TPI</h1><p>Home non trovata.</p>")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"version": os.environ.get("TPI_VERSION", "dev")}

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    if os.path.isfile(FAVICON):
        return FileResponse(FAVICON, media_type="image/x-icon")
    return Response(status_code=204)
