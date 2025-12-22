Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Ensure-Dir([string]$p) {
  if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null }
}

function Ensure-LineInFile([string]$Path, [string]$Line) {
  if (-not (Test-Path $Path)) { New-Item -ItemType File -Path $Path -Force | Out-Null }
  $content = Get-Content $Path -Raw
  if ($content -notmatch [regex]::Escape($Line)) {
    Add-Content -Path $Path -Value $Line
    Write-Host "ADD -> $Path :: $Line"
  } else {
    Write-Host "OK  -> $Path :: already has $Line"
  }
}

function Replace-InFile([string]$Path, [string]$Pattern, [string]$Replacement, [string]$Tag) {
  if (-not (Test-Path $Path)) { throw "MISSING FILE: $Path" }
  $txt = Get-Content $Path -Raw
  $new = [regex]::Replace($txt, $Pattern, $Replacement, [System.Text.RegularExpressions.RegexOptions]::Multiline)
  if ($new -ne $txt) {
    Set-Content -Path $Path -Value $new -NoNewline
    Write-Host "PATCH -> $Path :: $Tag"
    return $true
  } else {
    Write-Host "SKIP  -> $Path :: $Tag (no match)"
    return $false
  }
}

function Insert-AfterFirstImportBlock([string]$Path, [string]$Line) {
  $txt = Get-Content $Path -Raw
  if ($txt -match [regex]::Escape($Line)) { Write-Host "OK  -> $Path :: already has inserted line"; return }

  # after __future__ import if present, else after first import block, else at top
  $lines = Get-Content $Path
  $idx = -1
  for ($i=0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^\s*from\s+__future__\s+import\s+') { $idx = $i; break }
  }
  if ($idx -ge 0) {
    $out = @()
    for ($i=0; $i -lt $lines.Count; $i++) {
      $out += $lines[$i]
      if ($i -eq $idx) { $out += $Line }
    }
    Set-Content -Path $Path -Value ($out -join "`r`n")
    Write-Host "INS -> $Path :: after __future__"
    return
  }

  # find last consecutive import line at top
  $lastImport = -1
  for ($i=0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^\s*(from|import)\s+') { $lastImport = $i }
    elseif ($lines[$i].Trim() -eq '') { continue }
    else { break }
  }
  if ($lastImport -ge 0) {
    $out = @()
    for ($i=0; $i -lt $lines.Count; $i++) {
      $out += $lines[$i]
      if ($i -eq $lastImport) { $out += $Line }
    }
    Set-Content -Path $Path -Value ($out -join "`r`n")
    Write-Host "INS -> $Path :: after import block"
  } else {
    Set-Content -Path $Path -Value ($Line + "`r`n" + ($lines -join "`r`n"))
    Write-Host "INS -> $Path :: top"
  }
}

# ----------------- START
$Repo = "E:\CLONAZIONE\tpi_evoluto"
$ScriptsDir = Join-Path $Repo "scripts\CESARE"
Ensure-Dir $ScriptsDir

cd $Repo

# ensure branch
git checkout fix/accessori-by-code-404 | Out-Host

# 0) purge tracked pyc/cache + .gitignore
$pyc = git ls-files "*.pyc"
if ($pyc) { $pyc | ForEach-Object { git rm -f --cached $_ | Out-Null } }

$cache = git ls-files "__pycache__/**"
if ($cache) { $cache | ForEach-Object { git rm -f --cached $_ | Out-Null } }

if (-not (Test-Path ".gitignore")) { New-Item -ItemType File -Path ".gitignore" -Force | Out-Null }
Ensure-LineInFile ".gitignore" "__pycache__/"
Ensure-LineInFile ".gitignore" "*.pyc"
Ensure-LineInFile ".gitignore" ".mypy_cache/"
Ensure-LineInFile ".gitignore" ".pytest_cache/"
Ensure-LineInFile ".gitignore" ".venv/"

# 1) requirements-dev: stubs + httpx
$reqDev = Join-Path $Repo "requirements-dev.txt"
Ensure-LineInFile $reqDev "types-requests"
Ensure-LineInFile $reqDev "types-PyYAML"
Ensure-LineInFile $reqDev "httpx"

# 2) alembic ignores (REPLACE OR INSERT)
$alembicEnv = Join-Path $Repo "alembic\env.py"
$ok = Replace-InFile $alembicEnv '^\s*from\s+alembic\s+import\s+context.*$' 'from alembic import context  # type: ignore[attr-defined]' "alembic context ignore"
if (-not $ok) { Insert-AfterFirstImportBlock $alembicEnv 'from alembic import context  # type: ignore[attr-defined]' }

$alembicVer = Join-Path $Repo "alembic\versions\14252af2016e_init_schema_tpi_v1.py"
$ok2 = Replace-InFile $alembicVer '^\s*from\s+alembic\s+import\s+op.*$' 'from alembic import op  # type: ignore[attr-defined]' "alembic op ignore"
if (-not $ok2) { Insert-AfterFirstImportBlock $alembicVer 'from alembic import op  # type: ignore[attr-defined]' }

# 3) csv_routes: sort None-safe
$csvRoutes = Join-Path $Repo "app\csv_routes.py"
$ok3 = Replace-InFile $csvRoutes '^\s*(sort\s*=\s*)sort\.lower\(\)\s*$' 'sort = (sort or "").lower()' "sort None-safe lower()"
if (-not $ok3) {
  # fallback: replace inline "sort = sort.lower()"
  Replace-InFile $csvRoutes 'sort\s*=\s*sort\.lower\(\)' 'sort = (sort or "").lower()' "sort fallback"
}

# 4) accessori_listino: DictWriter vs _writer
$accListino = Join-Path $Repo "app\api\accessori_listino.py"
Replace-InFile $accListino 'writer\s*:\s*_writer\s*=\s*csv\.DictWriter' 'dw = csv.DictWriter' "DictWriter remove _writer annotation"
Replace-InFile $accListino 'writer\.writeheader\(\)' 'dw.writeheader()' "DictWriter writeheader"
Replace-InFile $accListino 'writer\.writerows' 'dw.writerows' "DictWriter writerows"
Replace-InFile $accListino 'writer\.writerow' 'dw.writerow' "DictWriter writerow"

# 5) README + STATO (FREEZE) on branch (will land on main via PR)
$readmePath = Join-Path $Rep
