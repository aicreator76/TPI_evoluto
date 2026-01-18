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

def _write(data: Dict[str, Any]) -> None:
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

def _is_suspended(html: str) -> bool:
    h = html.lower()
    return ("service suspended" in h) or ("has been suspended" in h) or ("x-render-routing" in h and "suspend" in h)

def fetch_openapi(retries: int = 5, timeout: int = 25) -> Dict[str, Any]:
    last: Optional[BaseException] = None

    for i in range(retries):
        try:
            req = Request(RENDER_OPENAPI, headers={"User-Agent": "TPI-Docs-Generator/1.0"})
            with urlopen(req, timeout=timeout) as r:
                raw = r.read().decode("utf-8-sig")
            return json.loads(raw)

        except HTTPError as e:
            last = e
            try:
                body = e.read().decode("utf-8", errors="ignore")
            except Exception:
                body = ""

            if e.code == 503 and _is_suspended(body):
                _write(_placeholder("service_suspended", f"HTTP 503 suspended: {RENDER_OPENAPI}"))
                print("[WARN] Render suspended (503). Wrote placeholder openapi.json.")
                return _placeholder("service_suspended", "placeholder_returned")

            sleep_s = min(2 ** i, 10)
            print(f"[WARN] fetch failed {i+1}/{retries}: HTTP {e.code} (sleep {sleep_s}s)", file=sys.stderr)
            time.sleep(sleep_s)

        except (URLError, TimeoutError, json.JSONDecodeError) as e:
            last = e
            sleep_s = min(2 ** i, 10)
            print(f"[WARN] fetch failed {i+1}/{retries}: {type(e).__name__}: {e} (sleep {sleep_s}s)", file=sys.stderr)
            time.sleep(sleep_s)

    _write(_placeholder("backend_unreachable", f"{type(last).__name__}: {last}"))
    print("[WARN] Backend unreachable. Wrote placeholder openapi.json.")
    return _placeholder("backend_unreachable", "placeholder_returned")

def main() -> int:
    data = fetch_openapi()

    # Se è placeholder già scritto sopra, usciamo OK.
    if data.get("x_sync_status") in ("service_suspended", "backend_unreachable"):
        return 0

    # Se è OpenAPI reale: salvala e marca ok
    data["x_sync_status"] = "ok"
    data["x_sync_reason"] = "synced_from_render"
    _write(data)

    paths = data.get("paths") or {}
    npaths = len(paths) if isinstance(paths, dict) else -1
    print(f"[OK] wrote {OUT} (paths={npaths})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())