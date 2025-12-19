from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException

FALLBACK_ITEMS: list[dict[str, Any]] = [
    {
        "code": "DEMO-0001",
        "name": "Demo 0001",
        "price_eur": 0.0,
        "stock": 0,
        "descr": "Fallback demo (mai 500).",
        "tags": ["demo"],
    },
    {
        "code": "DEMO-0002",
        "name": "Demo 0002",
        "price_eur": 0.0,
        "stock": 0,
        "descr": "Fallback demo (mai 500).",
        "tags": ["demo"],
    },
]


def _data_path() -> Path:
    app_dir = Path(__file__).resolve().parents[1]
    return app_dir / "data" / "demo_products.json"


def _load_items() -> list[dict[str, Any]]:
    p = _data_path()
    if not p.exists():
        return FALLBACK_ITEMS
    try:
        obj = json.loads(p.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return FALLBACK_ITEMS

    if isinstance(obj, dict) and isinstance(obj.get("items"), list):
        return obj["items"]
    if isinstance(obj, list):
        return obj
    return FALLBACK_ITEMS


router = APIRouter(tags=["demo"])


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
    app.include_router(router, prefix="/api/demo")
    app.include_router(router, prefix="/demo")
