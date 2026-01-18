from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

RENDER_OPENAPI = "https://tpi-evoluto-staging.onrender.com/openapi.json"
OUT = Path("docs/openapi.json")


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        return None
    return None


def _write_json(data: Dict[str, Any]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _placeholder(status: str, reason: str) -> Dict[str, Any]:
    return {
        "openapi": "3.0.0",
        "info": {"title": "TPI evoluto (staging)", "version": "placeholder"},
        "paths": {},
        "x_sync_status": status,
        "x_sync_reason": reason,
    }


def _looks_like_suspended(html: str) -> bool:
    h = html.lower()
    return ("service suspended" in h) or ("has been suspended" in h)


def _valid_paths(data: Dict[str, Any]) -> bool:
    paths = data.get("paths") or {}
    return isinstance(paths, dict) and len(paths) > 0


def fetch_openapi(retries: int = 5, timeout: int = 25) -> Dict[str, Any]:
    last: Optional[BaseException] = None

    for i in range(retries):
        try:
            req = Request(RENDER_OPENAPI, headers={"User-Agent": "TPI-Docs-Generator/1.0"})
            with urlopen(req, timeout=timeout) as r:
                raw = r.read().decode("utf-8-sig")
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise json.JSONDecodeError("not a dict", raw, 0)
            return data

        except HTTPError as e:
            last = e
            body = ""
            try:
                body = e.read().decode("utf-8", errors="ignore")
            except Exception:
                pass

            if e.code == 503 and _looks_like_suspended(body):
                raise RuntimeError("render_suspended")

            sleep_s = min(2 ** i, 10)
            print(f"[WARN] fetch failed {i+1}/{retries}: HTTP {e.code} (sleep {sleep_s}s)", file=sys.stderr)
            time.sleep(sleep_s)

        except (URLError, TimeoutError, json.JSONDecodeError) as e:
            last = e
            sleep_s = min(2 ** i, 10)
            print(f"[WARN] fetch failed {i+1}/{retries}: {type(e).__name__}: {e} (sleep {sleep_s}s)", file=sys.stderr)
            time.sleep(sleep_s)

    raise RuntimeError(f"backend_unreachable: {type(last).__name__}: {last}")


def main() -> int:
    cached = _read_json(OUT)
    cached_is_good = isinstance(cached, dict) and _valid_paths(cached) and cached.get("x_sync_status") not in (
        "service_suspended",
        "backend_unreachable",
        "placeholder",
    )

    try:
        data = fetch_openapi()
        data["x_sync_status"] = "ok"
        data["x_sync_reason"] = "synced_from_render"
        _write_json(data)
        print(f"[OK] wrote {OUT} (paths={len(data.get('paths') or {})})")
        return 0

    except Exception as e:
        # Render sospeso / backend KO: usa cache buona, altrimenti placeholder
        if cached_is_good:
            cached["x_sync_status"] = "stale"
            cached["x_sync_reason"] = f"render_unavailable_using_cached ({e})"
            _write_json(cached)
            print("[WARN] Render unavailable. Kept cached OpenAPI (stale).")
            return 0

        _write_json(_placeholder("backend_unreachable", str(e)))
        print("[WARN] Render unavailable. Wrote placeholder OpenAPI.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
