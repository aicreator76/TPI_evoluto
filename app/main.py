from fastapi import FastAPI
# importa router esistenti se già presenti
try:
    from app.dpi_csv import router as dpi_router
except Exception:
    dpi_router = None

app = FastAPI()
if dpi_router:
    app.include_router(dpi_router)

@app.get("/health")
def health():
    return {"status": "ok"}
