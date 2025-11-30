# FILE: E:\CLONAZIONE\scripts\Setup_TPI_Docs.ps1
# Scopo:
# - Creare/aggiornare 3 documenti base per TPI_evoluto:
#   * docs/README_POWER_TPI_evoluto.md
#   * docs/CRONACA_TPI_TEMPLATE.md
#   * docs/REGINA_SINTESI_TPI_DEMO.md

$ErrorActionPreference = "Stop"

$root    = "E:\CLONAZIONE"
$repo    = Join-Path $root "tpi_evoluto"
$docsDir = Join-Path $repo "docs"

if (-not (Test-Path $repo -PathType Container)) {
    Write-Host "Repo TPI_evoluto NON trovato: $repo" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $docsDir -PathType Container)) {
    New-Item -ItemType Directory -Path $docsDir -Force | Out-Null
}

$readmePath  = Join-Path $docsDir "README_POWER_TPI_evoluto.md"
$cronacaPath = Join-Path $docsDir "CRONACA_TPI_TEMPLATE.md"
$reginaPath  = Join-Path $docsDir "REGINA_SINTESI_TPI_DEMO.md"

# -----------------------------
# Contenuto README POWER (DEMO)
# -----------------------------
$readmeLines = @(
  "# TPI_evoluto - Modalita DEMO (Build Stub)",
  "",
  "Questo repository contiene la versione TPI_evoluto del progetto TPI (Tecnologia, Prevenzione, Innovazione).",
  "",
  "Stato attuale:",
  "- Esistono gli script di build stub CESARE_BUILD_TPI_WIN.ps1 e CESARE_BUILD_TPI_APK.ps1 nella cartella ci.",
  "- Le release DEMO scrivono file di test (STUB) in E:\CLONAZIONE\RELEASE_TPI\YYYY-MM-DD\WIN e APK.",
  "",
  "Importante:",
  "Gli artefatti generati oggi sono solo file di test, non veri .exe o .apk pronti per i clienti.",
  "",
  "Log collegati:",
  "- E:\CLONAZIONE\LOG\RELEASE_TPI_*.log",
  "- E:\CLONAZIONE\RELEASE_TPI\YYYY-MM-DD\LOG\...",
  "",
  "Le build reali verranno documentate in una sezione separata quando saranno disponibili."
)

# ------------------------------------
# Template CRONACA_TPI (Cronista Reale)
# ------------------------------------
$cronacaLines = @(
  "# CRONACA DI CAMELOT - TEMPLATE TPI",
  "",
  "Data: YYYY-MM-DD",
  "Release: vTEST-DEMO-XXX (stub)",
  "Semaforo tecnico: VERDE / GIALLO / ROSSO",
  "",
  "1) BACKUP / STRUTTURA",
  "- Backup_EMERGENZA: ...",
  "- Get-CesareStatus: ...",
  "",
  "2) BUILD / PACCHETTO",
  "- Comando usato: CESARE_RELEASE_TPI_DEMO.ps1 -Version vTEST-DEMO-XXX",
  "- Artefatti presenti:",
  "  - E:\CLONAZIONE\RELEASE_TPI\YYYY-MM-DD\WIN\...",
  "  - E:\CLONAZIONE\RELEASE_TPI\YYYY-MM-DD\APK\...",
  "",
  "3) RIEPILOGO / LIONEL",
  "- RIEPILOGO_GIORNO_YYYY-MM-DD.txt",
  "- ML.Status / ML.Check.Health: stato generale, errori principali.",
  "",
  "4) PROMESSE / RISCHI",
  "- Promesse fatte oggi:",
  "- Rischi e note per domani:",
  "",
  "5) FONTE SUMMARY",
  "- Riga SUMMARY tecnica usata come base narrativa."
)

# ----------------------------------------
# Sintesi TPI DEMO - per la Regina (1 pag.)
# ----------------------------------------
$reginaLines = @(
  "# Sintesi TPI - Modalita DEMO (per la Regina)",
  "",
  "Oggi:",
  "- Esiste una procedura tecnica che simula una release del giorno del progetto TPI_evoluto.",
  "- Ogni esecuzione crea cartelle ordinate in E:\CLONAZIONE\RELEASE_TPI\YYYY-MM-DD\ e log in E:\CLONAZIONE\LOG\RELEASE_TPI_*.log.",
  "",
  "Cosa sappiamo fare adesso:",
  "- Simulare una release tecnica giornaliera in modalita DEMO.",
  "- Controllare se la struttura di CESARE e TPI e sana (backup, cartelle, log).",
  "- Preparare la base documentale per quando le build reali saranno pronte.",
  "",
  "Cosa NON promettiamo ancora:",
  "- Nessun file .exe Windows reale pronto per clienti.",
  "- Nessun file .apk Android pronto per il Play Store.",
  "- Nessuna installazione automatica su PC o telefono del cliente.",
  "",
  "Prossimo gradino tecnico:",
  "- Installare e configurare Flutter e SDK Android sul PC che fara le build.",
  "- Collegare gli script di build DEMO alle build reali (EXE e APK).",
  "- Definire un test minimo umano su ogni file prima dell invio a clienti o partner.",
  "",
  "Note:",
  "- Questa pagina descrive solo lo stato attuale in modalita DEMO.",
  "- Gli stati futuri saranno confermati dai log:",
  "  - BUILD_TPI_WIN_*.log",
  "  - BUILD_TPI_APK_*.log",
  "  - RIEPILOGO_GIORNO_*.txt",
  "  - ML.Status e ML.Check.Health."
)

Set-Content -Path $readmePath  -Value $readmeLines  -Encoding UTF8
Set-Content -Path $cronacaPath -Value $cronacaLines -Encoding UTF8
Set-Content -Path $reginaPath  -Value $reginaLines -Encoding UTF8

Write-Host "Documenti TPI DEMO aggiornati:" -ForegroundColor Green
Write-Host " - $readmePath"
Write-Host " - $cronacaPath"
Write-Host " - $reginaPath"
