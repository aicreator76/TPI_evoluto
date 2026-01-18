$py = @'
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

RENDER_OPENAPI = "https://tpi-evoluto-staging.onrender.com/openapi.json"
OUT = Path("docs/openapi.json")

def write_placeholder(reason: str) -> None:
    payload = {
        "openapi": "3.0.0",
        "info": {"title": "TPI evoluto (staging)", "version": "suspended"},
        "paths": {},
        "x_sync_status": "service_suspended",
        "x_sync_reason": reason,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[WARN] wrote placeholder {OUT} ({reason})")

def fetch(retries: int = 4, timeout: int = 25) -> dict:
    last: Exception | None = None
    for i in range(retries):
        try:
            req = Request(RENDER_OPENAPI, headers={"User-Agent": "TPI-Docs-Generator/1.0"})
            with urlopen(req, timeout=timeout) as r:
                raw = r.read().decode("utf-8-sig")
            # se Render manda HTML, json.loads fallisce -> gestito sotto
            return json.loads(raw)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as e:
            last = e
            sleep_s = min(2 ** i, 8)
            print(f"[WARN] fetch failed {i+1}/{retries}: {e} (sleep {sleep_s}s)", file=sys.stderr)
            time.sleep(sleep_s)
    raise RuntimeError(str(last))

def main() -> int:
    try:
        data = fetch()
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        paths = data.get("paths") or {}
        n = len(paths) if isinstance(paths, dict) else -1
        print(f"[OK] wrote {OUT} (paths={n})")
        return 0
    except Exception as e:
        # ENTERPRISE: non bloccare Pages quando backend è sospeso
        write_placeholder(f"{type(e).__name__}: {e}")
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
'@

[System.IO.File]::WriteAllText("E:\CLONAZIONE\tpi_evoluto\scripts\generate_openapi.py", $py, (New-Object System.Text.UTF8Encoding($false)))
python -m py_compile .\scripts\generate_openapi.py
python .\scripts\generate_openapi.py
