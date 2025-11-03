# app/main.py
import logging
from fastapi import FastAPI

app = FastAPI()
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("tpi.app")

try:
    from app.dpi_csv import router as csv_router
    app.include_router(csv_router)
    log.info("Router CSV registrato: /api/dpi/csv/*")
except Exception as e:
    log.exception("Impossibile registrare router CSV: %s", e)


@app.get("/health")
def health():
    return {"status": "ok"}
