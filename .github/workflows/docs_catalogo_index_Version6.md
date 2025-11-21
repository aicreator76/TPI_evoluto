# Catalogo DPI — Overview

Questa sezione documenta le feature del router CSV di FastAPI:
- `GET /api/dpi/csv/template` — Scarica il template CSV
- `POST /api/dpi/csv/save` — Salva record dal CSV
- `GET /api/dpi/csv/catalogo` — Elenco catalogo DPI
- `GET /api/dpi/csv/export` — Esporta CSV
- `POST /api/dpi/csv/import-file` — Importa CSV
- `GET /api/dpi/csv/metrics` — Metriche
- `GET /api/dpi/csv/report.html` — Report HTML con riepilogo

## Smoke (PowerShell)

```powershell
# smoke_catalogo.ps1 (estratto)
$base = ${env:TPI_BASE_URL} # es. http://localhost:8000
Invoke-RestMethod "$base/api/dpi/csv/template" -OutFile "template.csv"
$metrics = Invoke-RestMethod "$base/api/dpi/csv/metrics" -Method GET
$report = Invoke-WebRequest "$base/api/dpi/csv/report.html" -Method GET
$metrics | ConvertTo-Json -Depth 5
```

## Esempi curl

```bash
# Template
curl -sS -o template.csv "$BASE_URL/api/dpi/csv/template"

# Catalogo
curl -sS "$BASE_URL/api/dpi/csv/catalogo"

# Export
curl -sS -o export.csv "$BASE_URL/api/dpi/csv/export"

# Import
curl -sS -F "file=@seed/dpi_seed.csv" "$BASE_URL/api/dpi/csv/import-file"

# Metrics
curl -sS "$BASE_URL/api/dpi/csv/metrics"
```

## Screenshot report.html
Se disponibile in CI/preview, includere uno screenshot del report per validazione visiva.
