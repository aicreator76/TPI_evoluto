param(
  [string]$Base = "http://127.0.0.1:8000"
)
$ErrorActionPreference = "Stop"

Write-Host "→ Healthz / Version"
irm "$Base/healthz" | Out-Null
irm "$Base/version" | Out-Null

Write-Host "→ Template"
$tpl = irm "$Base/api/dpi/csv/template"
$tpl | Out-Null

Write-Host "→ Save (seed)"
$csv = Get-Content -Raw ".\data\cataloghi\inputs\catalogo_seed.csv"
irm -Uri "$Base/api/dpi/csv/save" -Method Post -ContentType "text/csv" -Body $csv | Out-Null

Write-Host "→ Catalogo (JSON)"
$cat = irm "$Base/api/dpi/csv/catalogo"

Write-Host "→ Export short (anticaduta)"
iwr "$Base/api/dpi/csv/export?gruppo=anticaduta&columns=short" -OutFile ".\export_short.csv" | Out-Null

Write-Host "→ Report HTML (listino)"
iwr "$Base/api/dpi/csv/report.html?columns=listino&gruppo=anticaduta" -OutFile ".\report.html" | Out-Null

Write-Host "OK ✓  (export_short.csv, report.html pronti)"
