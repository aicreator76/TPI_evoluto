# Build-Portable.ps1
# Uso: powershell -ExecutionPolicy Bypass -File .\Build-Portable.ps1
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ===============================
# Logging
# ===============================
$Script:LogFile = Join-Path (Get-Location) 'Build-Portable.log'
function Write-Log {
    param(
        [Parameter(Mandatory)][string]$Message,
        [ValidateSet('INFO','WARN','ERROR')][string]$Level = 'INFO'
    )
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "$ts [$Level] $Message"
    Write-Host $line
    try { Add-Content -LiteralPath $Script:LogFile -Value $line } catch {}
}

# ===============================
# Scelta destinazione
# Priorità: env:PORTABLE_TARGET -> D:\ -> primo rimovibile -> corrente
# ===============================
function Get-PortableTarget {
    try {
        if ($env:PORTABLE_TARGET -and (Test-Path -LiteralPath $env:PORTABLE_TARGET)) {
            return (Resolve-Path -LiteralPath $env:PORTABLE_TARGET).Path.TrimEnd('\') + '\'
        }
        if (Test-Path 'D:\') { return 'D:\' }
        try {
            $wmi = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DriveType=2" -ErrorAction Stop |
                   Sort-Object DeviceID | Select-Object -First 1
            if ($wmi -and (Test-Path ($wmi.DeviceID + '\'))) { return ($wmi.DeviceID + '\') }
        } catch {}
        return (Get-Location).Path.TrimEnd('\') + '\'
    } catch {
        return (Get-Location).Path.TrimEnd('\') + '\'
    }
}

# ===============================
# Crea file solo se mancanti
# ===============================
function Ensure-File {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Content,
        [ValidateSet('UTF8','ASCII')][string]$Encoding = 'UTF8'
    )
    try {
        if (-not (Test-Path -LiteralPath $Path)) {
            $dir = Split-Path -Parent $Path
            if ($dir -and -not (Test-Path -LiteralPath $dir)) {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
            }
            $Content | Set-Content -LiteralPath $Path -Encoding $Encoding -Force
            Write-Log "Creato file: $Path"
        } else {
            Write-Log "File già presente: $Path"
        }
    } catch {
        Write-Log "Impossibile creare $Path. Dettagli: $($_.Exception.Message)" 'ERROR'
        throw
    }
}

# ===============================
# ZIP con fallback .NET
# ===============================
function New-ZipRobust {
    param(
        [Parameter(Mandatory)][string]$SourceDir,
        [Parameter(Mandatory)][string]$ZipPath
    )
    if (Test-Path -LiteralPath $ZipPath) {
        try { Remove-Item -LiteralPath $ZipPath -Force -ErrorAction Stop } catch {
            Write-Log "Impossibile rimuovere ZIP esistente: $ZipPath. $($_.Exception.Message)" 'ERROR'
            throw
        }
    }
    # 1) Compress-Archive (PowerShell)
    try {
        Compress-Archive -Path (Join-Path $SourceDir '*') -DestinationPath $ZipPath -Force -ErrorAction Stop
        Write-Log "ZIP creato con Compress-Archive: $ZipPath"
        return
    } catch {
        Write-Log "Compress-Archive fallito, uso fallback .NET: $($_.Exception.Message)" 'WARN'
    }
    # 2) .NET ZipFile
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        [System.IO.Compression.ZipFile]::CreateFromDirectory(
            $SourceDir,
            $ZipPath,
            [System.IO.Compression.CompressionLevel]::Optimal,
            $false
        )
        Write-Log "ZIP creato con .NET ZipFile: $ZipPath"
    } catch {
        Write-Log "Creazione ZIP fallita anche con .NET: $($_.Exception.Message)" 'ERROR'
        throw
    }
}

# ===============================
# Validazione contenuti ZIP
# ===============================
function Test-ZipContents {
    param(
        [Parameter(Mandatory)][string]  $ZipPath,
        [Parameter(Mandatory)][string[]]$ExpectedRelativeFiles
    )
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        # Normalizza attesi
        $expected = @($ExpectedRelativeFiles) |
            Where-Object { $_ -ne $null -and $_.ToString().Trim() -ne '' } |
            ForEach-Object { ($_ -replace '\\','/').TrimStart('/') }

        # Apri ZIP in sola lettura
        $fs = [System.IO.File]::Open($ZipPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        try {
            $za = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Read, $false)
            # Solo file (no directory)
            $actual = @(
                $za.Entries |
                Where-Object { $_.FullName -and ($_.FullName -notmatch '/$') } |
                ForEach-Object { ($_.FullName -replace '\\','/').TrimStart('/') }
            )
        } finally {
            if ($fs) { $fs.Dispose() }
        }

        # Confronto insensibile all'ordine
        $missing = @($expected | Where-Object { $_ -notin $actual })
        $extra   = @($actual   | Where-Object { $_ -notin $expected })

        if ($missing.Count -eq 0 -and $extra.Count -eq 0) {
            Write-Log "Validazione ZIP OK: contenuti attesi presenti"
            return $true
        } else {
            if ($missing.Count -gt 0) { Write-Log "File mancanti nello ZIP: $($missing -join ', ')" 'ERROR' }
            if ($extra.Count   -gt 0) { Write-Log "File extra nello ZIP: $($extra   -join ', ')" 'WARN'  }
            return $false
        }
    } catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
}

# ===============================
# MAIN
# ===============================
try {
    Write-Log "Avvio build portabile TPI_evoluto"

    $TARGET_ROOT = Get-PortableTarget
    Write-Log "Target root: $TARGET_ROOT"

    $PKG_DIR = Join-Path $TARGET_ROOT 'TPI_evoluto_portabile'
    New-Item -ItemType Directory -Path $PKG_DIR -Force | Out-Null

    # --- FILE BASE ---
    $IndexFile = Join-Path $PKG_DIR 'index.html'
    $IndexContent = @'
<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8" />
  <title>TPI_evoluto - Dashboard (Portabile)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body{font-family:system-ui,Segoe UI,Arial;margin:32px}
    .card{border:1px solid #ddd;padding:16px;border-radius:12px;max-width:900px}
    .grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
    .badge{display:inline-block;background:#eee;padding:4px 10px;border-radius:999px;margin-right:6px}
    a.button{display:inline-block;margin-top:12px;border:1px solid #888;padding:8px 12px;border-radius:8px;text-decoration:none}
  </style>
</head>
<body>
  <h1>TPI_evoluto · Dashboard</h1>
  <div class="card">
    <p>Versione portabile/offline (solo HTML/CSS/JS). Nessun server richiesto.</p>
    <div class="grid">
      <div><span class="badge">DPI</span></div>
      <div><span class="badge">Sottogancio</span></div>
      <div><span class="badge">Funi metalliche</span></div>
      <div><span class="badge">Formazione</span></div>
    </div>
    <a class="button" href="README_PROGETTO.txt">Info progetto</a>
  </div>
</body>
</html>
'@
    Ensure-File -Path $IndexFile -Content $IndexContent

    $StartContent = @'
@echo off
REM Avvia la dashboard portabile aprendo index.html
start "" "%~dp0index.html"
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'start.cmd') -Content $StartContent -Encoding ASCII
    Copy-Item -LiteralPath (Join-Path $PKG_DIR 'start.cmd') -Destination (Join-Path $PKG_DIR 'START TPI.cmd') -Force

    $ReadmePre = @'
# TPI_evoluto - Guida rapida (PRE-INSTALLAZIONE)

1. Copia l'intera cartella "TPI_evoluto_portabile" in un percorso sicuro (es. C:\ o su USB).
2. Per avviare la dashboard offline:
   - Doppio clic su "START TPI.cmd"
   - Si aprirà il browser con la dashboard TPI (non serve Python né Internet).
3. Requisiti:
   - Windows 10 o 11
   - Nessuna installazione richiesta
   - Modalità read-only
4. In caso di problemi, apri "index.html" direttamente con Edge/Chrome/Firefox.
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PRE.txt') -Content $ReadmePre

    $ReadmeProgetto = @'
# TPI_evoluto - Progetto ufficiale

Questa versione portabile contiene la dashboard base (HTML) in sola lettura.
Per la versione completa (FastAPI, logging, i18n IT/EN/FR/DE, ruoli: datore di lavoro, revisore, RSPP, lavoratore, supervisore) visita il repository:

- GitHub: https://github.com/aicreator76/TPI_evoluto

## Come contribuire
- git clone https://github.com/aicreator76/TPI_evoluto.git
- branch suggeriti: feature/logging-middleware, feature/i18n
- apri PR verso main

## Contenuto pacchetto portabile
- index.html
- START TPI.cmd / start.cmd
- README_PRE.txt
- README_PROGETTO.txt
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PROGETTO.txt') -Content $ReadmeProgetto

    # --- ZIP + REPORT ---
    $ZIP = Join-Path $TARGET_ROOT 'TPI_evoluto_portabile.zip'
    New-ZipRobust -SourceDir $PKG_DIR -ZipPath $ZIP

    # SHA256
    $sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $ZIP).Hash

    # Checklist (compatibile con Windows PowerShell 5.1)
    $chk = @()
    if (Test-Path -LiteralPath $IndexFile) { $chk += '- [x] index.html presente' } else { $chk += '- [ ] index.html presente' }
    if (Test-Path -LiteralPath (Join-Path $PKG_DIR 'start.cmd')) { $chk += '- [x] start.cmd presente' } else { $chk += '- [ ] start.cmd presente' }
    if (Test-Path -LiteralPath (Join-Path $PKG_DIR 'START TPI.cmd')) { $chk += '- [x] START TPI.cmd presente' } else { $chk += '- [ ] START TPI.cmd presente' }
    if (Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PRE.txt')) { $chk += '- [x] README_PRE.txt presente' } else { $chk += '- [ ] README_PRE.txt presente' }
    if (Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PROGETTO.txt')) { $chk += '- [x] README_PROGETTO.txt presente' } else { $chk += '- [ ] README_PROGETTO.txt presente' }
    if (Test-Path -LiteralPath $ZIP) { $chk += '- [x] Zip creato correttamente' } else { $chk += '- [ ] Zip creato correttamente' }

    $reportPath = Join-Path $TARGET_ROOT 'PACKAGE_REPORT.md'
    $report = @"
# PACKAGE REPORT

- Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Destinazione: $TARGET_ROOT
- Cartella: $PKG_DIR
- ZIP: $ZIP
- SHA256: $sha

## Verifiche
$($chk -join "`r`n")

## Istruzioni d'uso
- Copia "TPI_evoluto_portabile" o lo ZIP sulla destinazione finale
- Avvia "START TPI.cmd"
"@
    $report | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-Log "Generato report: $reportPath"

    # Validazione ZIP: esattamente questi file
    $expected = @('index.html','start.cmd','START TPI.cmd','README_PRE.txt','README_PROGETTO.txt')
    if (-not (Test-ZipContents -ZipPath $ZIP -ExpectedRelativeFiles $expected)) {
        Write-Log "Validazione ZIP non riuscita: controllare Build-Portable.log e contenuti." 'ERROR'
        throw "ZIP non conforme."
    }

    # Output richiesto
    Write-Output "Percorso cartella: $PKG_DIR"
    Write-Output "Percorso ZIP: $ZIP"
    Write-Output "SHA256: $sha"
    Write-Output "`nPACKAGE_REPORT.md:`n"
    Get-Content -LiteralPath $reportPath
    Write-Log "Build completata con successo."
    exit 0
}
catch {
    Write-Log "Build fallita: $($_.Exception.Message)" 'ERROR'
    Write-Output "Errore: $($_.Exception.Message)"
    Write-Output "Vedi log: $Script:LogFile"
    exit 1
}
