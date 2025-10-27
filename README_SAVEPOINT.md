# Savepoint & Workflows helper (locale)

Repo: `aicreator76/TPI_evoluto`  
Script: `savepoint_workflows.ps1`

## Comandi rapidi
- Savepoint del giorno (commit se serve, push, tag): `pwsh .\savepoint_workflows.ps1 -Savepoint`
- Allineamento sicuro da remoto (rebase su origin/<branch>): `pwsh .\savepoint_workflows.ps1 -Align`
- Nuova feature: `pwsh .\savepoint_workflows.ps1 -Feature titolo-breve`
- Hotfix rapido: `pwsh .\savepoint_workflows.ps1 -Hotfix bug-critico`

### Note operative
- Dopo un rebase: `git push --force-with-lease`.
- Il tag giornaliero è idempotente: `Snapshot-OK-YYYY-MM-DD`.
- Il comando `-Savepoint` crea/aggiorna il tag del giorno e fa push.
