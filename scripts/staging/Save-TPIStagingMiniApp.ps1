param(
    [string]$Message = "chore: update mini_app TPI_evoluto staging"
)

Write-Host "=== TPI_evoluto – Save mini_app STAGING ===" -ForegroundColor Cyan
Write-Host "Repo: E:\CLONAZIONE\TPI_evoluto" -ForegroundColor DarkCyan

cd E:\CLONAZIONE\TPI_evoluto

Write-Host "`n[1] git status (solo info)..." -ForegroundColor Yellow
git status

Write-Host "`n[2] check diff su src/mini_app.py..." -ForegroundColor Yellow
git diff --quiet src/mini_app.py
$hasChanges = $LASTEXITCODE -ne 0

if (-not $hasChanges) {
    Write-Host "`n✅ mini_app già allineata: nessuna modifica da salvare." -ForegroundColor Green
    Write-Host "   (Nessun commit, nessun push eseguito)" -ForegroundColor DarkYellow
    return
}

Write-Host "`n[3] git add src/mini_app.py..." -ForegroundColor Yellow
git add src/mini_app.py

Write-Host "`n[4] git commit..." -ForegroundColor Yellow
git commit -m $Message

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n⚠️ Commit non eseguito (hook o altro problema)." -ForegroundColor DarkYellow
    return
}

Write-Host "`n[5] git push origin main..." -ForegroundColor Yellow
git push origin main

Write-Host "`n=== DONE: mini_app salvata & spinta su main ===" -ForegroundColor Green
