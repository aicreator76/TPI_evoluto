from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(
    prefix="/api/ops",
    tags=["ops"],
)


@router.get("/healthz", summary="Health operativo (ops)")
async def ops_healthz():
    """
    Health check operativo per monitor / probe interni.
    """
    return {
        "status": "ok",
        "service": "tpi_ops",
        "time": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/version", summary="Versione servizio (ops)")
async def ops_version():
    """
    Version info separata dall'endpoint /version principale.
    """
    return {
        "service": "tpi_ops",
        "version": "0.1.0-stub",
    }
