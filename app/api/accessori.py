from fastapi import APIRouter

from app.api.accessori_listino import router as listino_router
from app.api.accessori_sollevamento import router as sollevamento_router

# Router "collettore": NON mettere prefix qui (i sotto-router hanno già prefix="/api/accessori")
router = APIRouter(tags=["accessori"])

router.include_router(sollevamento_router)
router.include_router(listino_router)
