from fastapi import APIRouter
import os

router = APIRouter(prefix="/api", tags=["API"])

@router.get("/healthz")
def healthz(): return {"status":"ok"}

@router.get("/version")
def version(): return {"version": os.environ.get("TPI_VERSION","dev")}
