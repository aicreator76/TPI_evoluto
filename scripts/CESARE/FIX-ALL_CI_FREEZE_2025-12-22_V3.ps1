Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ===== CONFIG
$Repo   = "E:\CLONAZIONE\tpi_evoluto"
$PrNum  = 74
$GhRepo = "aicreator76/TPI_evoluto"
$Tag    = "Snapshot-OK-2025-12-22"

function Ensure-Line([string]$path, [string]$line) {
  if (-not (Test-Path $path)) { New-Item -ItemType File -Path $path -Force | Out-Null }
  $raw = Get-Content $path -Raw
  if ($raw -notmatch [regex]::Escape($line)) { Add-Content -Path $path -Value $line }
}

function Replace-Regex([string]$path, [string]$pattern, [string]$replacement) {
  if (-not (Test-Path $path)) { throw "MISSING FILE: $path" }
  $txt = Get-Content $path -Raw
  $new = [regex]::Replace($txt, $pattern, $replacement, [Text.RegularExpressions.RegexOptions]::Multiline)
  if ($new -ne $txt) { Set-Content -Path $path -Value $new -Encoding UTF8; return $true }
  return $false
}

function Insert-After-Any-Import([string]$path, [string]$line) {
  $txt = Get-Content $path -Raw
  if ($txt -match [regex]::Escape($line)) { return }
  $lines = Get-Content $path
  $idx = -1
  for ($i=0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^\s*(from|import)\s+') { $idx = $i }
  }
  if ($idx -ge 0) {
    $out = @()
    for ($i=0; $i -lt $lines.Count; $i++) {
      $out += $lines[$i]
      if ($i -eq $idx) { $out += $line }
    }
    Set-Content -Path $path -Value ($out -join "`r`n") -Encoding UTF8
  } else {
    Set-Content -Path $path -Value ($line + "`r`n" + ($lines -join "`r`n")) -Encoding UTF8
  }
}

# ===== START
cd $Repo
git checkout fix/accessori-by-code-404 | Out-Host

# 0) .gitignore harden
$gi = Join-Path $Repo ".gitignore"
Ensure-Line $gi "__pycache__/"
Ensure-Line $gi "*.pyc"
Ensure-Line $gi ".mypy_cache/"
Ensure-Line $gi ".pytest_cache/"
Ensure-Line $gi ".venv/"

# 1) dev deps: stubs + httpx
$reqDev = Join-Path $Repo "requirements-dev.txt"
Ensure-Line $reqDev "types-requests"
Ensure-Line $reqDev "types-PyYAML"
Ensure-Line $reqDev "httpx"

# 2) Alembic: garantisci ignore *sulla riga import*
$alEnv = Join-Path $Repo "alembic\env.py"
$ok = Replace-Regex $alEnv '^\s*from\s+alembic\s+import\s+context\s*(#.*)?$' 'from alembic import context  # type: ignore[attr-defined]'
if (-not $ok) { Insert-After-Any-Import $alEnv 'from alembic import context  # type: ignore[attr-defined]' }

$alVer = Join-Path $Repo "alembic\versions\14252af2016e_init_schema_tpi_v1.py"
$ok2 = Replace-Regex $alVer '^\s*from\s+alembic\s+import\s+op\s*(#.*)?$' 'from alembic import op  # type: ignore[attr-defined]'
if (-not $ok2) { Insert-After-Any-Import $alVer 'from alembic import op  # type: ignore[attr-defined]' }

# 3) csv_routes: rendi "sort" None-safe (3 pattern)
$csvRoutes = Join-Path $Repo "app\csv_routes.py"
Replace-Regex $csvRoutes '(^\s*sort\s*=\s*)(sort)\.lower\(\)\s*$' '${1}(${2} or "").lower()' | Out-Null
Replace-Regex $csvRoutes 'sort\s*=\s*sort\.lower\(\)' 'sort = (sort or "").lower()' | Out-Null
Replace-Regex $csvRoutes 'sort\s*=\s*sort\.strip\(\)\.lower\(\)' 'sort = (sort or "").strip().lower()' | Out-Null

# 4) accessori_listino: elimina tipizzazione _writer e usa DictWriter “dw”
$acc = Join-Path $Repo "app\api\accessori_listino.py"

# 4a) se esiste "writer: _writer = csv.DictWriter(...)" -> "dw = csv.DictWriter(...)"
Replace-Regex $acc '^\s*writer\s*:\s*_writer\s*=\s*csv\.DictWriter' 'dw = csv.DictWriter' | Out-Null

# 4b) se esiste "writer = csv.DictWriter(...)" e poi "writer.writeheader()" -> "dw = ..." e "dw.writeheader()"
# (solo se troviamo writer=DictWriter; altrimenti non tocca)
$hitWriter = Replace-Regex $acc '^\s*writer\s*=\s*csv\.DictWriter' 'dw = csv.DictWriter'
if ($hitWriter) {
  Replace-Regex $acc '(^\s*)writer\.writeheader\(\)' '${1}dw.writeheader()' | Out-Null
  Replace-Regex $acc '(^\s*)writer\.writerows\(' '${1}dw.writerows(' | Out-Null
  Replace-Regex $acc '(^\s*)writer\.writerow\(' '${1}dw.writerow(' | Out-Null
}

# 4c) se rimane "writer: _writer" in giro (altre varianti) lo neutralizziamo
Replace-Regex $acc ':\s*_writer' '' | Out-Null

# 5) install + test
& "$Repo\.venv\Scripts\python.exe" -m pip install -r "$Repo\requirements-dev.txt" | Out-Host
& "$Repo\.venv\Scripts\python.exe" -m mypy . | Out-Host
& "$Repo\.venv\Scripts\python.exe" -m pytest -q | Out-Host

# 6) commit + push (solo se c’è qualcosa)
$por = (git status --porcelain)
if (-not $por) { throw "NESSUN CAMBIAMENTO: controlla che i path esistano e che i pattern matchino." }

$paths = @(
  ".gitignore",
  "requirements-dev.txt",
  "alembic\env.py",
  "alembic\versions\14252af2016e_init_schema_tpi_v1.py",
  "app\csv_routes.py",
  "app\api\accessori_listino.py"
)

git add -- $paths | Out-Host
git commit -m "fix(ci+tests): mypy + pytest green (alembic ignore, sort None-safe, DictWriter, httpx)" | Out-Host
git push | Out-Host

# 7) auto-merge PR (policy)
gh pr merge $PrNum --squash --auto --delete-branch --repo $GhRepo | Out-Host

Write-Host "OK: PATCH PUSHATA. PR in AUTO-MERGE (attende CI)."
Write-Host "Quando PR è MERGED, tagga su main:"
Write-Host "  cd $Repo"
Write-Host "  git checkout main; git pull"
Write-Host "  git tag -a $Tag -m `"Freeze TPI_evoluto: PR$PrNum merged + CI green`""
Write-Host "  git push origin $Tag"
