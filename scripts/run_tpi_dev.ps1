param(
    [switch]$NoAlembic  # usa: -NoAlembic per saltare alembic upgrade head
)

$ErrorActionPreference = "Stop"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "   TPI_evoluto – DEV RUNNER (AELIS)   " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Radice progetto
$projectRoot = "E:\CLONAZIONE\tpi_evoluto"
$venvActivate = Join-Path $projectRoot ".venv\Scripts\Activate.ps1"

if (-not (Test-Path $projectRoot)) {
    Write-Host "[ERRORE] Cartella progetto non trovata: $projectRoot" -ForegroundColor Red
    exit 1
}

Set-Location $projectRoot

if (-not (Test-Path $venvActivate)) {
    Write-Host "[ERRORE] Virtual env non trovato: $venvActivate" -ForegroundColor Red
    Write-Host "Crea il venv prima, esempio:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor Yellow
    Write-Host "  . .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  python -m pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Attivo virtualenv .venv…" -ForegroundColor Green
. $venvActivate

# DATABASE_URL per SQLite locale
$env:DATABASE_URL = "sqlite:///E:/CLONAZIONE/tpi_evoluto/tpidb.sqlite3"
Write-Host "[OK] DATABASE_URL impostata su SQLite locale" -ForegroundColor Green

# Alembic upgrade (se non disattivato)
if (-not $NoAlembic) {
    Write-Host "[OK] Eseguo alembic upgrade head…" -ForegroundColor Green
    alembic upgrade head
}
else {
    Write-Host "[SKIP] alembic upgrade head (flag -NoAlembic)" -ForegroundColor Yellow
}

# Avvio Uvicorn
Write-Host "[OK] Avvio uvicorn app.main:app --reload…" -ForegroundColor Green
python -m uvicorn app.main:app --reload
