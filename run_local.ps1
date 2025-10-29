# run_local.ps1 — avvio rapido FastAPI su 8011
$ErrorActionPreference="Stop"
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) { py -3.11 -m venv .venv }
. .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip *> $null
pip install --no-cache-dir -r requirements.txt

# Porta libera?
$port=8011
if (Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue) {
  Write-Host "Porta $port occupata. Uccido server precedenti..."
  taskkill /F /IM uvicorn.exe 2>$null
  taskkill /F /IM python.exe  2>$null
  Start-Sleep -Seconds 1
}

# Avvio
python -m uvicorn app.main:app --port $port --ws none
