from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException


def _data_path() -> Path:
    app_dir = Path(__file__).resolve().parents[1]
    return app_dir / "data" / "catalog_formazione.json"


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


router = APIRouter(tags=["formazione"])


@router.get("/courses")
def list_courses() -> dict[str, Any]:
    items = _load_items()
    return {"items": items, "count": len(items)}


@router.get("/courses/{code}")
def get_course(code: str) -> dict[str, Any]:
    items = _load_items()
    for it in items:
        if str(it.get("code")) == code:
            return it
    raise HTTPException(status_code=404, detail="Not found")
