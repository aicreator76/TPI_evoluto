from fastapi import FastAPI
from app.csv_routes import router as csv_router
import logging

app = FastAPI()
app.include_router(csv_router)

logging.getLogger("tpi.app").info("Router CSV registrato: /api/dpi/csv/*")
