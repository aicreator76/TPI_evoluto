# TPI_DASHBOARD.ps1
# Menu interattivo per gestione TPI_evoluto

function Show-Menu {
    Clear-Host
    Write-Host "=== Dashboard TPI_evoluto ===" -ForegroundColor Cyan
    Write-Host "1) Avvia server FastAPI (localhost:8000)" -ForegroundColor Green
    Write-Host "2) Backup su D:\TPI_evoluto_backup" -ForegroundColor Yellow
    Write-Host "3) Git Status" -ForegroundColor White
    Write-Host "4) Git Pull (aggiorna da remoto)" -ForegroundColor White
    Write-Host "5) Git Push (carica modifiche su remoto)" -ForegroundColor White
    Write-Host "6) Apri repository GitHub nel browser" -ForegroundColor Magenta
    Write-Host "0) Esci" -ForegroundColor Red
    Write-Host "==============================" -ForegroundColor Cyan
}

function Run-Choice {
    param([string]$choice)
    switch ($choice) {
        "1" {
            Write-Host ">>> Avvio server..." -ForegroundColor Green
            Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\.venv\Scripts\python.exe -m uvicorn app.main:app --reload"
        }
        "2" {
            Write-Host ">>> Backup in corso..." -ForegroundColor Yellow
            robocopy "C:\TPI_evoluto" "D:\TPI_evoluto_backup" /MIR /XD ".git" ".venv" /XF *.lock
        }
        "3" { git status | Out-Host }
        "4" { git pull origin feature/logging-middleware | Out-Host }
        "5" {
            git add .
            git commit -m "update: modifiche automatiche da dashboard" 2>$null
            git push origin feature/logging-middleware | Out-Host
        }
        "6" { Start-Process "https://github.com/aicreator76/TPI_evoluto" }
        "0" { exit }
        default { Write-Host "Scelta non valida!" -ForegroundColor Red }
    }
}

do {
    Show-Menu
    $choice = Read-Host "Seleziona un'opzione"
    Run-Choice $choice
    if ($choice -ne "0") { Pause }
} while ($choice -ne "0")
