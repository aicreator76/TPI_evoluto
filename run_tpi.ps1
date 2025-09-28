Write-Host "=== Avvio TPI_evoluto ===" -ForegroundColor Green
Set-Location "C:\TPI_evoluto"

# Attiva virtualenv se presente
if (Test-Path .\.venv\Scripts\Activate.ps1) {
    . .\.venv\Scripts\Activate.ps1
    Write-Host "Virtualenv attivato." -ForegroundColor Cyan
} else {
    Write-Host "⚠️ Nessun virtualenv trovato, proseguo senza." -ForegroundColor Yellow
}

# Directory log
$logDir = Join-Path (Get-Location) "logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$logFile = Join-Path $logDir "tpi_server.log"

Write-Host "Logging su $logFile"

# Chiude eventuali server uvicorn già avviati
$running = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*\.venv\Scripts\python.exe" }
if ($running) {
    Write-Host "⚠️ Uvicorn già attivo, lo chiudo..." -ForegroundColor Yellow
    $running | Stop-Process -Force
    Start-Sleep -Seconds 2
}

# Avvio uvicorn in nuova finestra con log live
Start-Process powershell -ArgumentList "-NoExit","-ExecutionPolicy Bypass","-Command",
    "& { .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload | Tee-Object -FilePath `"$logFile`" }"

Start-Sleep -Seconds 2
Write-Host "✅ Server avviato in nuova finestra."
Start-Process "http://127.0.0.1:8000"
