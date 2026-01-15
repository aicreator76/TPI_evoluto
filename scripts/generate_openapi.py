from pathlib import Path
import json

out = Path("docs/openapi.json")
out.parent.mkdir(parents=True, exist_ok=True)

payload = {
  "openapi": "3.0.0",
  "info": {"title": "TPI evoluto", "version": "0.0.0"},
  "paths": {}
}

out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"[OK] wrote {out}")