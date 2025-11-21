# Cruscotto TPI – Catena Release DEMO

## 1. CESARE_RELEASE_TPI_DEMO.ps1
- Script: E:\CLONAZIONE\CESARE_COMANDI\scripts\CESARE_RELEASE_TPI_DEMO.ps1
- Effetto: crea BACKUP_EMERGENZA +
  cartella E:\CLONAZIONE\RELEASE_TPI\YYYY-MM-DD +
  file STATUS_TPI_YYYY-MM-DD.json
- Log: E:\CLONAZIONE\LOG\RELEASE_TPI_YYYY-MM-DD.log

## 2. CESARE_TPI_CI_BRIDGE.ps1
- Script: E:\CLONAZIONE\scripts\CESARE\CESARE_TPI_CI_BRIDGE.ps1
- Effetto: crea tag tpi-v* (es. tpi-vTEST-CI-BRIDGE-001)
  e accende il workflow GitHub 'Build TPI (stub)'
- Risultato: artifact stub (WIN/APK) per quella versione in GitHub Actions

## 3. Workflow GitHub 'Build TPI (stub)'
- File: .github/workflows/build-tpi.yml
- Effetto: genera artefatti STUB (non EXE/APK reali)
  per verificare CI e collegamento con CESARE

## 4. CESARE_CRONACA_OK.ps1
- Script: E:\CLONAZIONE\scripts\CESARE\CESARE_CRONACA_OK.ps1
- Effetto: aggiorna STATUS_TPI_YYYY-MM-DD.json con:
  cronaca='saved', cronaca_file, cronaca_updated_at, semaforo_tecnico, note_critiche, regina_note
- Logga: riga CRONACA YYYY-MM-DD : SALVATA nel log RELEASE_TPI_YYYY-MM-DD.log

## 5. Cronache Regina
- File: E:\CLONAZIONE\Cronache_Regina\Cronache_Regina_YYYY-MM.md
- Effetto: riassume la giornata con:
  - semafori 001–BLD / 002–GIT / 003–LMB
  - riferimenti a STATUS_TPI_YYYY-MM-DD.json e ai log RELEASE_TPI
