param(
    [string]$Message = "chore: update agente0 orchestratore"
)

Write-Host "=== TPI_evoluto – Save AGENTE0 Orchestratore ===" -ForegroundColor Cyan
Write-Host "Repo: E:\CLONAZIONE\TPI_evoluto" -ForegroundColor DarkCyan

cd E:\CLONAZIONE\TPI_evoluto

Write-Host "`n[1] git status (solo info)..." -ForegroundColor Yellow
git status

Write-Host "`n[2] check diff (vs HEAD) su agents/agente0_orchestratore/agente0_main.py..." -ForegroundColor Yellow
git diff --quiet HEAD -- agents/agente0_orchestratore/agente0_main.py
$hasChanges = $LASTEXITCODE -ne 0

if (-not $hasChanges) {
    Write-Host "`n✅ agente0_main.py già allineato a HEAD: nessuna modifica da salvare." -ForegroundColor Green
    Write-Host "   (Nessun commit, nessun push eseguito)" -ForegroundColor DarkYellow
    return
}

Write-Host "`n[3] git add agents/agente0_orchestratore/agente0_main.py..." -ForegroundColor Yellow
git add agents/agente0_orchestratore/agente0_main.py

Write-Host "`n[4] git commit (primo tentativo, con pre-commit)..." -ForegroundColor Yellow
git commit -m $Message
$commitExit = $LASTEXITCODE

if ($commitExit -ne 0) {
    Write-Host "`n⚠️ Commit NON eseguito al primo tentativo." -ForegroundColor DarkYellow
    Write-Host "   Probabile: i pre-commit hook (Ruff/Black) hanno RIFORMATTATO il file." -ForegroundColor DarkYellow

    Write-Host "`n[4-bis] git status -sb (dopo pre-commit)..." -ForegroundColor Yellow
    git status -sb

    Write-Host "`n[4-ter] git add agents/agente0_orchestratore/agente0_main.py (dopo formattazione hook)..." -ForegroundColor Yellow
    git add agents/agente0_orchestratore/agente0_main.py

    Write-Host "`n[4-quater] git commit (secondo tentativo)..." -ForegroundColor Yellow
    git commit -m $Message
    $secondExit = $LASTEXITCODE

    if ($secondExit -ne 0) {
        Write-Host "`n⚠️ Commit ancora NON eseguito dopo il secondo tentativo." -ForegroundColor Red
        Write-Host "   → Controlla i messaggi dei pre-commit sopra, serve intervento manuale." -ForegroundColor DarkYellow
        return
    }
}

Write-Host "`n[5] git push origin main..." -ForegroundColor Yellow
git push origin main

Write-Host "`n=== DONE: AGENTE0 salvato & spinto su main ===" -ForegroundColor Green
