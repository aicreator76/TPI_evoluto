# Endpoint HTTP — Catalogo DPI

- GET `/api/dpi/csv/template`
- POST `/api/dpi/csv/save`
- GET `/api/dpi/csv/catalogo`
- GET `/api/dpi/csv/export`
- POST `/api/dpi/csv/import-file`
- GET `/api/dpi/csv/metrics`
- GET `/api/dpi/csv/report.html`

## PowerShell (Invoke-RestMethod)

```powershell
$base = ${env:TPI_BASE_URL}
Invoke-RestMethod "$base/api/dpi/csv/catalogo" -Method GET
```

## curl

```bash
curl -sS "$BASE_URL/api/dpi/csv/catalogo"
```