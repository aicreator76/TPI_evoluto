import json
import urllib.request
from pathlib import Path

# URL dell'OpenAPI del backend Render
url = "https://tpi-evoluto-staging.onrender.com/openapi.json"

# Scarica e decodifica (ignora eventuali BOM)
data = urllib.request.urlopen(url).read().decode("utf-8-sig")
obj = json.loads(data)

# Scrivi il file nella cartella docs
out = Path("docs/openapi.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print("[OK] wrote", out)
