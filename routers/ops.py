from fastapi import APIRouter
import os
import datetime

router = APIRouter(tags=["Ops"])


@router.get("/healthz", summary="Health probe")
def healthz():
    return {"status": "ok", "time": datetime.datetime.utcnow().isoformat() + "Z"}


@router.get("/version", summary="Version info")
def version():
    return {
        "app": "TPI_evoluto",
        "version": os.getenv("APP_VERSION", "dev"),
        "git_sha": os.getenv("GIT_SHA", ""),
        "build_time": os.getenv("BUILD_TIME", ""),
    }
