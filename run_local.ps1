$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path .\.venv\Scripts\Activate.ps1)) { py -3.11 -m venv .venv }
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip >$null
pip install --no-cache-dir -r requirements.txt
# chiudi eventuali processi appesi (best-effort)
taskkill /F /IM uvicorn.exe 2>$null; taskkill /F /IM python.exe 2>$null
python -m uvicorn app.main:app --port 8011 --ws none
