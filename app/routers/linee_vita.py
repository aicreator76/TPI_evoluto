from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException


def _data_path() -> Path:
    app_dir = Path(__file__).resolve().parents[1]
    return app_dir / "data" / "catalogo_linee_vita.json"


def _load_items() -> list[dict[str, Any]]:
    p = _data_path()
    if not p.exists():
        return []
    obj = json.loads(p.read_text(encoding="utf-8-sig"))
    if isinstance(obj, dict) and isinstance(obj.get("items"), list):
        return obj["items"]
    if isinstance(obj, list):
        return obj
    return []


router = APIRouter(tags=["linee-vita"])


@router.get("/products")
def list_products() -> dict[str, Any]:
    items = _load_items()
    return {"items": items, "count": len(items)}


@router.get("/products/{code}")
def get_product(code: str) -> dict[str, Any]:
    items = _load_items()
    for it in items:
        if str(it.get("code")) == code:
            return it
    raise HTTPException(status_code=404, detail="Not found")


def mount(app: FastAPI) -> None:
    # OpenAPI: SOLO /api/*
    app.include_router(router, prefix="/api/linee-vita", include_in_schema=True)
    # Fallback: stesso comportamento, fuori da OpenAPI (mount-safe)
    app.include_router(router, prefix="/linee-vita", include_in_schema=False)
