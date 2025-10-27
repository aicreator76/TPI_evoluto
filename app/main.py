from fastapi import FastAPI
from app.dpi_csv import router as dpi_router

app = FastAPI(title="TPI_evoluto API")
app.include_router(dpi_router)

@app.get("/health")
def health():
    return {"status": "ok"}
