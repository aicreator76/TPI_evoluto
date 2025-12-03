from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/nfc",
    tags=["nfc"],
)


class NFCLandingRequest(BaseModel):
    """
    Payload minimo per NFC landing/log.
    """

    tag_id: str
    source: str | None = None  # es: "qrcode", "app", "reader"
    note: str | None = None


@router.post("/landing", summary="NFC landing / log accesso (stub)")
async def nfc_landing(payload: NFCLandingRequest):
    """
    Stub NFC:

    - Valida che ci sia un tag_id
    - Registra un evento "virtuale" (solo in risposta JSON)
    - TODO: in futuro log su DB + apertura deep-link app
    """
    if not payload.tag_id:
        raise HTTPException(status_code=400, detail="tag_id obbligatorio")

    return {
        "status": "logged",
        "tag_id": payload.tag_id,
        "source": payload.source or "unknown",
        "note": payload.note,
        "logged_at": datetime.now(timezone.utc).isoformat(),
    }
