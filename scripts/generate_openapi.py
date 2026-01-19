from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

RENDER_OPENAPI = "https://tpi-evoluto-staging.onrender.com/openapi.json"
OUT = Path("docs/openapi.json")

ALLOWED_STATUSES = {"ok", "stale", "service_suspended", "backend_unreachable"}


class RenderSuspended(RuntimeError):
    pass


class BackendUnreachable(RuntimeError):
    pass


def _utc_ts() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _read_json(path: Path) -> Optional[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _write_json(data: dict[str, Any]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _placeholder(status: str, reason: str) -> dict[str, Any]:
    return {
        "openapi": "3.0.0",
        "info": {"title": "TPI evoluto (staging)", "version": "placeholder"},
        "paths": {},
        "x_sync_status": status,
        "x_sync_reason": reason,
        "x_sync_ts_utc": _utc_ts(),
    }


def _looks_like_html(text: str) -> bool:
    t = (text or "").lstrip().lower()
    return t.startswith("<!doctype html") or t.startswith("<html") or "<html" in t[:5000]


def _looks_like_suspended(text: str) -> bool:
    h = (text or "").lower()
    return (
        ("service suspended" in h)
        or ("has been suspended" in h)
        or ("suspended" in h and "render" in h)
    )


def _valid_paths(d: dict[str, Any]) -> bool:
    paths = d.get("paths") or {}
    return isinstance(paths, dict) and len(paths) > 0


def _cached_is_good(d: Optional[dict[str, Any]]) -> bool:
    if not isinstance(d, dict):
        return False
    st = d.get("x_sync_status")
    if st in {"service_suspended", "backend_unreachable"}:
        return False
    return _valid_paths(d)


def fetch_openapi(retries: int = 5, timeout: int = 25) -> dict[str, Any]:
    last: Optional[BaseException] = None

    for i in range(retries):
        try:
            req = Request(RENDER_OPENAPI, headers={"User-Agent": "TPI-Docs-Generator/2.0"})
            with urlopen(req, timeout=timeout) as r:
                raw = r.read().decode("utf-8-sig", errors="replace")

            if _looks_like_html(raw):
                if _looks_like_suspended(raw):
                    raise RenderSuspended("html_suspended")
                raise BackendUnreachable("html_response")

            data = json.loads(raw)
            if not isinstance(data, dict):
                raise BackendUnreachable("openapi_not_object")

            # ENTERPRISE HARDENING:
            # se arriva JSON “valido” ma senza paths, NON lo consideriamo ok.
            if not _valid_paths(data):
                raise BackendUnreachable("empty_paths_from_render")

            return data

        except HTTPError as e:
            last = e
            body = ""
            try:
                body = e.read().decode("utf-8", errors="ignore")
            except Exception:
                body = ""

            if e.code == 503 and _looks_like_suspended(body):
                raise RenderSuspended("render_suspended_503")

            sleep_s = min(2**i, 10)
            print(
                f"[WARN] fetch failed {i+1}/{retries}: HTTP {e.code} (sleep {sleep_s}s)",
                file=sys.stderr,
            )
            time.sleep(sleep_s)

        except (URLError, TimeoutError, json.JSONDecodeError, BackendUnreachable) as e:
            last = e
            sleep_s = min(2**i, 10)
            print(
                f"[WARN] fetch failed {i+1}/{retries}: {type(e).__name__}: {e} (sleep {sleep_s}s)",
                file=sys.stderr,
            )
            time.sleep(sleep_s)

    raise BackendUnreachable(f"{type(last).__name__}: {last}")


def main() -> int:
    cached = _read_json(OUT)

    try:
        data = fetch_openapi()
        data["x_sync_status"] = "ok"
        data["x_sync_reason"] = "synced_from_render"
        data["x_sync_ts_utc"] = _utc_ts()
        _write_json(data)
        print(f"[OK] wrote {OUT} (paths={len(data.get('paths') or {})})")
        return 0

    except RenderSuspended as e:
        if _cached_is_good(cached) and cached is not None:
            cached["x_sync_status"] = "stale"
            cached["x_sync_reason"] = f"render_suspended_using_cached ({e})"
            cached["x_sync_ts_utc"] = _utc_ts()
            _write_json(cached)
            print("[WARN] Render suspended. Kept cached OpenAPI (stale).")
            return 0

        _write_json(_placeholder("service_suspended", str(e)))
        print("[WARN] Render suspended. Wrote placeholder OpenAPI.")
        return 0

    except BackendUnreachable as e:
        if _cached_is_good(cached) and cached is not None:
            cached["x_sync_status"] = "stale"
            cached["x_sync_reason"] = f"backend_unreachable_using_cached ({e})"
            cached["x_sync_ts_utc"] = _utc_ts()
            _write_json(cached)
            print("[WARN] Backend unreachable. Kept cached OpenAPI (stale).")
            return 0

        _write_json(_placeholder("backend_unreachable", str(e)))
        print("[WARN] Backend unreachable. Wrote placeholder OpenAPI.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
