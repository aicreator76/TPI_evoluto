Write-Host "=== Avvio SAFE PUSH per TPI_evoluto ===" -ForegroundColor Cyan

# Vai nella cartella del progetto
Set-Location "C:\TPI_evoluto"

# Controlla cartella config
if (-not (Test-Path "app\config")) {
    Write-Host "⚠️ Creo cartella app\config mancante..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "app\config" | Out-Null
}

# Controlla file roles.py
if (-not (Test-Path "app\config\roles.py")) {
    Write-Host "⚠️ Creo file roles.py mancante..." -ForegroundColor Yellow
    @'
ROLES = [
    "datore",
    "revisore",
    "RSPP",
    "lavoratore",
    "supervisore"
]
'@ | Set-Content "app\config\roles.py" -Encoding UTF8
}

# Controlla __init__.py (serve per il modulo Python)
if (-not (Test-Path "app\config\__init__.py")) {
    Write-Host "⚠️ Creo __init__.py mancante..." -ForegroundColor Yellow
    "" | Set-Content "app\config\__init__.py" -Encoding UTF8
}

# Aggiungi e committa
git add .
git commit -m "SAFE PUSH: fix struttura app/config + aggiornamento file"
git push origin feature/logging-middleware

# Backup su D:
$backupPath = "D:\TPI_evoluto_backup"
Write-Host "=== Avvio backup su $backupPath ===" -ForegroundColor Green
robocopy C:\TPI_evoluto $backupPath /MIR /XD ".git" ".venv" /XF *.lock

Write-Host "=== SAFE PUSH completato con successo! ===" -ForegroundColor Green
