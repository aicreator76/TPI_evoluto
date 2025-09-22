# BACKUP_TPI.ps1
# Copia il progetto TPI_evoluto da C: a D: mantenendo aggiornato il backup

$Source = "C:\TPI_evoluto"
$Destination = "D:\TPI_evoluto_backup"

Write-Host "=== Avvio backup da $Source a $Destination ===" -ForegroundColor Cyan

# Crea la cartella di destinazione se non esiste
if (!(Test-Path $Destination)) {
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
}

# Copia con mirroring, escludendo .venv e .git
robocopy $Source $Destination /MIR /XF *.lock /XD .venv .git\objects\pack

Write-Host "=== Backup completato ===" -ForegroundColor Green
