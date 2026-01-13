from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api", tags=["cataloghi"])


def _repo_root() -> Path:
    # ...\app\routers\cataloghi.py -> parents[0]=routers, [1]=app, [2]=repo
    return Path(__file__).resolve().parents[2]


def _catalog_dir() -> Path:
    return _repo_root() / "data" / "cataloghi"


@router.get("/cataloghi")
def list_cataloghi():
    d = _catalog_dir()
    if not d.exists():
        return {"ok": True, "count": 0, "items": []}

    items = []
    for p in sorted(d.glob("*")):
        if p.is_file():
            st = p.stat()
            items.append(
                {
                    "name": p.name,
                    "size": st.st_size,
                    "mtime": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
                    "download_url": f"/api/cataloghi/{p.name}",
                }
            )
    return {"ok": True, "count": len(items), "items": items}


@router.get("/cataloghi/{name}")
def download_catalogo(name: str):
    # anti path traversal
    safe = Path(name).name
    p = _catalog_dir() / safe
    if not p.exists() or not p.is_file():
        raise HTTPException(status_code=404, detail="catalogo_not_found")
    return FileResponse(str(p), filename=safe)
