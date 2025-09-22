# FINAL_PUSH.ps1
Write-Host "=== Avvio push finale di TPI_evoluto su GitHub ===" -ForegroundColor Cyan

# Vai nella cartella del progetto
Set-Location "C:\TPI_evoluto"

# 1. Aggiorna il remote (giusto URL GitHub)
git remote set-url origin https://github.com/aicreator76/TPI_evoluto.git

# 2. Assicurati di essere sul branch corretto
git checkout feature/logging-middleware

# 3. Aggiungi tutti i file nuovi o modificati
git add .

# 4. Commit solo se ci sono modifiche
if (git status --porcelain) {
    git commit -m "final: push completo con file base, UI aggiornata e script esecuzione"
} else {
    Write-Host "Nessuna modifica da committare" -ForegroundColor Yellow
}

# 5. Push finale sul branch remoto
git push origin feature/logging-middleware

# 6. Backup automatico su D:
$backupPath = "D:\TPI_evoluto_backup"
Write-Host "=== Backup su $backupPath ===" -ForegroundColor Cyan
robocopy "C:\TPI_evoluto" $backupPath /MIR /XD ".git" ".venv" /XF *.lock

Write-Host "=== Push finale completato e backup salvato su D: ===" -ForegroundColor Green
