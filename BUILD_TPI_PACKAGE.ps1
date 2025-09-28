Write-Host "=== Costruzione pacchetto portabile TPI_evoluto ===" -ForegroundColor Cyan

# 1. Percorso base (modifica se serve)
$BaseDir   = "C:\TPI_evoluto_portabile"
$ZipTarget = "C:\TPI_evoluto_portabile.zip"

# 2. Pulizia se esiste
if (Test-Path $BaseDir) { Remove-Item -Recurse -Force $BaseDir }
if (Test-Path $ZipTarget) { Remove-Item -Force $ZipTarget }

# 3. Crea cartella
New-Item -ItemType Directory -Path $BaseDir | Out-Null

# 4. Copia i file esistenti (adatta se stanno in altra cartella)
Copy-Item "C:\TPI_evoluto\index.html" $BaseDir -Force
Copy-Item "C:\TPI_evoluto\start.cmd" $BaseDir -Force
Copy-Item "C:\TPI_evoluto\START TPI.cmd" $BaseDir -Force
Copy-Item "C:\TPI_evoluto\Avvia-RSPP.ps1" $BaseDir -Force

# 5. README_PRE (istruzioni per l’utente finale)
@'
# TPI_evoluto - Guida rapida (PRE-INSTALLAZIONE)

1. Copia l’intera cartella `TPI_evoluto_portabile` in un percorso sicuro
   (es. C:\ o su chiavetta USB).

2. Per avviare la dashboard offline:
   - Fai doppio clic su `START TPI.cmd`
   - Si aprirà il browser con la dashboard TPI (non serve Python).

3. Compatibile con Windows 10/11. Modalità **read-only**, nessuna scrittura su disco.
'@ | Set-Content -Path "$BaseDir\README_PRE.txt" -Encoding UTF8

# 6. README_PROGETTO (info e GitHub)
@'
# TPI_evoluto - Progetto ufficiale

Questa versione portabile contiene la dashboard base (HTML + script) in sola lettura.

Per la versione **completa con FastAPI, logging, i18n (IT, EN, FR, DE), ruoli (datore, revisore, RSPP, lavoratore, supervisore) e dashboard interattiva**, visita il repository ufficiale:

👉 GitHub: https://github.com/aicreator76/TPI_evoluto

## Come contribuire
- Clona il repo
- Usa i branch `feature/logging-middleware` e `feature/i18n`
- Apri una Pull Request verso `main`

## Contenuto pacchetto
- `index.html` → Dashboard offline
- `START TPI.cmd` / `start.cmd` → Avvio rapido
- `Avvia-RSPP.ps1` → Script demo aggiuntivo
- `README_PRE.txt` → Guida rapida
- `README_PROGETTO.txt` → Info progetto + GitHub
'@ | Set-Content -Path "$BaseDir\README_PROGETTO.txt" -Encoding UTF8

# 7. Comprimi in ZIP
Compress-Archive -Path $BaseDir\* -DestinationPath $ZipTarget -Force

Write-Host "=== Pacchetto creato con successo ===" -ForegroundColor Green
Write-Host "Cartella: $BaseDir"
Write-Host "Archivio: $ZipTarget"
