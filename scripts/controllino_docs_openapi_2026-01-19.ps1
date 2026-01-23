# CONTROLLINO ENTERPRISE - Docs + OpenAPI Pages
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

cd E:\CLONAZIONE\tpi_evoluto

Write-Host "== LOCAL: compile + generate ==" -ForegroundColor Cyan
python -m py_compile .\scripts\generate_openapi.py
python .\scripts\generate_openapi.py

Write-Host "== LOCAL: pre-commit ==" -ForegroundColor Cyan
pre-commit run --all-files

Write-Host "== REMOTE: last Docs run ==" -ForegroundColor Cyan
$id = (gh run list --workflow docs.yml --limit 1 --json databaseId --jq '.[0].databaseId')
gh run watch $id --exit-status

Write-Host "== PAGES: openapi.json no-cache ==" -ForegroundColor Cyan
$P = "https://aicreator76.github.io/TPI_evoluto/openapi.json?ts=$([DateTime]::UtcNow.Ticks)"
$code = curl.exe -s -L -o "$env:TEMP\openapi_pages.json" -w "%{http_code}" $P
if ($code -ne "200") { throw "FAIL Pages openapi.json HTTP=$code" }

python -c "import json,os;from pathlib import Path;p=Path(os.environ['TEMP'])/'openapi_pages.json';d=json.loads(p.read_text(encoding='utf-8-sig'));st=d.get('x_sync_status');paths=len(d.get('paths') or {});print('OK Pages JSON','status=',st,'paths=',paths);assert st in ('ok','stale','service_suspended','backend_unreachable')"

Write-Host "== DONE: enterprise gate passed ==" -ForegroundColor Green
