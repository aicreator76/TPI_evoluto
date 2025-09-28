Write-Host "=== Arresto TPI_evoluto ===" -ForegroundColor Red

# Cerca i processi uvicorn/python legati al tuo progetto
$running = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*\.venv\Scripts\python.exe" }

if ($running) {
    $running | ForEach-Object {
        Write-Host "Uccido processo PID=$($_.Id) - $($_.Path)" -ForegroundColor Yellow
        Stop-Process -Id $_.Id -Force
    }
    Write-Host "✅ Tutti i processi TPI_evoluto sono stati fermati." -ForegroundColor Green
} else {
    Write-Host "ℹ️ Nessun server TPI_evoluto attivo trovato." -ForegroundColor Cyan
}
