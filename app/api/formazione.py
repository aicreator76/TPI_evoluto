from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api/formazione", tags=["formazione"])

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "catalog_formazione.json"


@lru_cache(maxsize=1)
def _load_items() -> list[dict[str, Any]]:
    if not DATA_FILE.exists():
        return []

    raw = DATA_FILE.read_text(encoding="utf-8").strip()
    if not raw:
        return []

    obj = json.loads(raw)

    # accetta sia lista che {"items":[...]}
    if isinstance(obj, dict) and "items" in obj:
        obj = obj["items"]

    if not isinstance(obj, list):
        raise ValueError("catalog_formazione.json must be a list or a dict with key 'items'.")

    # forza dict
    out: list[dict[str, Any]] = []
    for it in obj:
        if isinstance(it, dict):
            out.append(it)
    return out


def _match_q(it: dict[str, Any], q: str) -> bool:
    q = q.lower().strip()
    if not q:
        return True
    hay = " ".join(
        str(it.get(k, "") or "") for k in ("code", "name", "descr", "tags", "famiglia", "sorgente")
    ).lower()
    return q in hay


@router.get("/overview")
def overview() -> dict[str, Any]:
    items = _load_items()
    famiglie = {str(x.get("famiglia", "")).strip() for x in items if x.get("famiglia")}
    sorgenti = {str(x.get("sorgente", "")).strip() for x in items if x.get("sorgente")}
    return {
        "items": int(len(items)),
        "famiglie": int(len(famiglie)),
        "sorgenti": int(len(sorgenti)),
        "file": str(DATA_FILE),
    }


@router.get("/products")
def list_products(
    q: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    items = _load_items()
    qv = (q or "").strip()
    filtered = [it for it in items if _match_q(it, qv)]
    page = filtered[offset : offset + limit]
    return {"items": page, "count": int(len(filtered))}


@router.get("/products/{code}")
def get_product(code: str) -> dict[str, Any]:
    items = _load_items()
    code_norm = code.strip().lower()
    for it in items:
        if str(it.get("code", "")).strip().lower() == code_norm:
            return it
    raise HTTPException(status_code=404, detail="Not found")
