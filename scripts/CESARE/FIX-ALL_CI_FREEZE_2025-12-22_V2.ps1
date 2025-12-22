Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ----------------- CONFIG
$Repo     = "E:\CLONAZIONE\tpi_evoluto"
$Scripts  = "E:\CLONAZIONE\tpi_evoluto\scripts\CESARE"
$LogDir   = "E:\CLONAZIONE\LOG"
$TagName  = "Snapshot-OK-2025-12-22"
$PrNumber = 74
$GhRepo   = "aicreator76/TPI_evoluto"

function Ensure-Dir([string]$p) { if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null } }

function Ensure-Line([string]$path, [string]$line) {
  if (-not (Test-Path $path)) { New-Item -ItemType File -Path $path -Force | Out-Null }
  $raw = Get-Content $path -Raw
  if ($raw -notmatch [regex]::Escape($line)) { Add-Content -Path $path -Value $line }
}

function Replace-Regex([string]$path, [string]$pattern, [string]$replacement) {
  if (-not (Test-Path $path)) { throw "MISSING FILE: $path" }
  $txt = Get-Content $path -Raw
  $new = [regex]::Replace($txt, $pattern, $replacement, [System.Text.RegularExpressions.RegexOptions]::Multiline)
  if ($new -ne $txt) { Set-Content -Path $path -Value $new -NoNewline; return $true }
  return $false
}

function Insert-Line-After-Imports([string]$path, [string]$line) {
  $txt = Get-Content $path -Raw
  if ($txt -match [regex]::Escape($line)) { return }

  $lines = Get-Content $path
  $lastImport = -1
  for ($i=0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^\s*(from|import)\s+') { $lastImport = $i; continue }
    if ($lines[$i].Trim() -eq '') { continue }
    break
  }

  if ($lastImport -ge 0) {
    $out = @()
    for ($i=0; $i -lt $lines.Count; $i++) {
      $out += $lines[$i]
      if ($i -eq $lastImport) { $out += $line }
    }
    Set-Content -Path $path -Value ($out -join "`r`n")
  } else {
    Set-Content -Path $path -Value ($line + "`r`n" + ($lines -join "`r`n"))
  }
}

# ----------------- START
Ensure-Dir $Scripts
Ensure-Dir $LogDir

$stamp = (Get-Date).ToString("yyyy-MM-dd_HH-mm-ss")
$log = Join-Path $LogDir "FIX-ALL_CI_FREEZE_2025-12-22_V2_$stamp.log"
Start-Transcript -Path $log | Out-Null

try {
  cd $Repo

  # branch
  git checkout fix/accessori-by-code-404 | Out-Host

  # 0) purge tracked artifacts + .gitignore harden
  $pyc = git ls-files "*.pyc"
  if ($pyc) { $pyc | ForEach-Object { git rm -f --cached $_ | Out-Null } }

  $cache = git ls-files "__pycache__/**"
  if ($cache) { $cache | ForEach-Object { git rm -f --cached $_ | Out-Null } }

  if (-not (Test-Path "$Repo\.gitignore")) { New-Item -ItemType File -Path "$Repo\.gitignore" -Force | Out-Null }
  Ensure-Line "$Repo\.gitignore" "__pycache__/"
  Ensure-Line "$Repo\.gitignore" "*.pyc"
  Ensure-Line "$Repo\.gitignore" ".mypy_cache/"
  Ensure-Line "$Repo\.gitignore" ".pytest_cache/"
  Ensure-Line "$Repo\.gitignore" ".venv/"

  # 1) requirements-dev: ensure stubs + httpx
  $reqDev = "$Repo\requirements-dev.txt"
  Ensure-Line $reqDev "types-requests"
  Ensure-Line $reqDev "types-PyYAML"
  Ensure-Line $reqDev "httpx"

  # 2) Alembic typing ignores (replace or insert)
  $alEnv = "$Repo\alembic\env.py"
  $did = Replace-Regex $alEnv '^\s*from\s+alembic\s+import\s+context\s*$' 'from alembic import context  # type: ignore[attr-defined]'
  if (-not $did) { Insert-Line-After-Imports $alEnv 'from alembic import context  # type: ignore[attr-defined]' }

  $alVer = "$Repo\alembic\versions\14252af2016e_init_schema_tpi_v1.py"
  $did2 = Replace-Regex $alVer '^\s*from\s+alembic\s+import\s+op\s*$' 'from alembic import op  # type: ignore[attr-defined]'
  if (-not $did2) { Insert-Line-After-Imports $alVer 'from alembic import op  # type: ignore[attr-defined]' }

  # 3) csv_routes: fix sort None.lower (robusto)
  $csvRoutes = "$Repo\app\csv_routes.py"
  $r1 = Replace-Regex $csvRoutes '^\s*sort\s*=\s*sort\.lower\(\)\s*$' 'sort = (sort or "").lower()'
  $r2 = Replace-Regex $csvRoutes '^\s*sort\s*=\s*sort\.strip\(\)\.lower\(\)\s*$' 'sort = (sort or "").strip().lower()'
  $r3 = Replace-Regex $csvRoutes 'sort\s*=\s*sort\.lower\(\)' 'sort = (sort or "").lower()'
  $r4 = Replace-Regex $csvRoutes 'sort\s*=\s*sort\.strip\(\)\.lower\(\)' 'sort = (sort or "").strip().lower()'

  # 4) accessori_listino: ripristina writer (no dw) + elimina annotazione _writer
  $acc = "$Repo\app\api\accessori_listino.py"
  # se il tuo file è stato "mezzo patchato" con dw., torna a writer.
  Replace-Regex $acc '(^\s*)dw\.' '${1}writer.' | Out-Null
  # elimina type annotation che rompe mypy
  # writer: _writer = csv.DictWriter(...)  -> writer = csv.DictWriter(...)
  $r5 = Replace-Regex $acc '^\s*writer\s*:\s*_writer\s*=\s*csv\.DictWriter' 'writer = csv.DictWriter'

  # 5) README + STATO (freeze) sul branch PR (andrà in main via merge)
  $readme = "$Repo\README.md"
  @"
# TPI_evoluto — Orchestratore DPI (FastAPI)

Backend FastAPI per gestione DPI via CSV: template, import/export, catalogo, metriche e report HTML.

## API principali (CSV/DPI)
Base URL (dev): http://127.0.0.1:8012

- GET  /api/dpi/csv/template
- POST /api/dpi/csv/save
- GET  /api/dpi/csv/catalogo
- GET  /api/dpi/csv/export
- POST /api/dpi/csv/import-file
- POST /api/dpi/csv/import
- GET  /api/dpi/csv/metrics
- GET  /api/dpi/csv/report.html
- GET  /openapi.json

## Cataloghi
- E:\CLONAZIONE\tpi_evoluto\app\data\catalog_linee_vita.json
- E:\CLONAZIONE\tpi_evoluto\app\data\catalog_inox.json

## Avvio (Windows PowerShell)
cd E:\CLONAZIONE\tpi_evoluto
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8012 --log-level warning

## Dev / Qualità
cd E:\CLONAZIONE\tpi_evoluto
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m mypy .
.\.venv\Scripts\python.exe -m pytest -q

## Agenti (repo)
- E:\CLONAZIONE\tpi_evoluto\agents\agente0_orchestratore\agente0_main.py
- classifier.py, reader_excel.py, writer_log.py, notifier_n8n.py

## Artefatti (storico)
- E:\CLONAZIONE\RELEASE_TPI\LISTINI\ACCESSORI\TPI_ACCESSORI_API_3_0_DELTA_2025-12-08.zip
"@ | Set-Content -Encoding UTF8 $readme

  $stato = "$Repo\STATO_TPI_FINAL.txt"
  @"
TPI_evoluto — STATO FINALE
Data: 2025-12-22
Stato Regno: GIALLO (in attesa CI)

Repo:
- Path: E:\CLONAZIONE\tpi_evoluto
- Branch PR74: fix/accessori-by-code-404

Cataloghi:
- E:\CLONAZIONE\tpi_evoluto\app\data\catalog_linee_vita.json
- E:\CLONAZIONE\tpi_evoluto\app\data\catalog_inox.json

Artefatto ZIP:
- E:\CLONAZIONE\RELEASE_TPI\LISTINI\ACCESSORI\TPI_ACCESSORI_API_3_0_DELTA_2025-12-08.zip

CI disciplina:
- Alembic typing ignore (op/context)
- Stubs: types-requests, types-PyYAML
- Fix: sort None.lower -> (sort or "").lower()
- Fix: DictWriter tipizzazione (_writer) rimossa
- Tests: httpx aggiunto per TestClient
"@ | Set-Content -Encoding UTF8 $stato

  # 6) install + mypy + pytest
  & "$Repo\.venv\Scripts\python.exe" -m pip install -r "$Repo\requirements-dev.txt" | Out-Host
  & "$Repo\.venv\Scripts\python.exe" -m mypy . | Out-Host
  & "$Repo\.venv\Scripts\python.exe" -m pytest -q | Out-Host

  # 7) commit + push branch
  git status --porcelain | Out-Host
  git add "$Repo\.gitignore" "$Repo\requirements-dev.txt" "$Repo\alembic\env.py" "$Repo\alembic\versions\14252af2016e_init_schema_tpi_v1.py" "$Repo\ap
