$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) { py -3.11 -m venv .venv }
. .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip *> $null
pip install --no-cache-dir -r requirements.txt

$port = 8011
$py   = Join-Path (Get-Location) ".\.venv\Scripts\python.exe"
$arg  = @("-m","uvicorn","app.main:app","--host","127.0.0.1","--port",$port,"--ws","none","--lifespan","off","--log-level","debug")

# Chiudi solo eventuali processi che occupano la porta
Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | %{
  try { taskkill /F /PID $_.OwningProcess 2>$null } catch {}
}
Start-Sleep -Seconds 1

# Avvio DETACHED con log su file
Start-Process -FilePath $py -ArgumentList $arg `
  -RedirectStandardOutput ".\uvicorn-app.out" `
  -RedirectStandardError  ".\uvicorn-app.err" `
  -WindowStyle Hidden -PassThru | Out-Null

Start-Sleep -Seconds 1
Write-Host "→ http://127.0.0.1:$port/health"
