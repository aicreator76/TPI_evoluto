<incolla qui la funzione Test-ZipContents completa mostrata sopra>
# Requisiti: Windows PowerShell 5.1+ o PowerShell 7+. Nessun privilegio elevato richiesto.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ---------------------------------
# Logging
# ---------------------------------
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

# ---------------------------------
# Helper percorsi / compatibilità
# ---------------------------------
$IsWin = [System.Environment]::OSVersion.Platform -eq 'Win32NT'

function Add-LongPathPrefix {
    param([Parameter(Mandatory)][string]$Path)
    if ($IsWin) {
        if ($Path -like '\\?\*') { return $Path }
        $full = [System.IO.Path]::GetFullPath($Path)
        if ($full.StartsWith('\\')) { return "\\?\UNC\$($full.TrimStart('\'))" }
        return "\\?\$full"
    } else {
        return $Path
    }
}

function Test-Command { param([string]$Name) $null -ne (Get-Command $Name -ErrorAction SilentlyContinue) }

# ---------------------------------
# Destinazione: D:\ poi primo rimovibile, altrimenti corrente
# ---------------------------------
function Get-PortableTarget {
    try {
        if (Test-Path 'D:\') { return 'D:\' }

        try {
            $wmi = Get-CimInstance -Class Win32_LogicalDisk -Filter "DriveType=2" -ErrorAction Stop |
                   Sort-Object DeviceID | Select-Object -First 1
            if ($wmi -and (Test-Path ($wmi.DeviceID + '\'))) { return ($wmi.DeviceID + '\') }
        } catch {}

        if (Test-Command -Name Get-Volume) {
            $vol = Get-Volume | Where-Object DriveType -eq 'Removable' | Select-Object -First 1
            if ($vol) { return ($vol.DriveLetter + ':\') }
        }

        return (Get-Location).Path + '\'
    } catch {
        return (Get-Location).Path + '\'
    }
}

# ---------------------------------
# Creazione file solo se mancanti
# ---------------------------------
function Ensure-File {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Content,
        [ValidateSet('UTF8','ASCII')][string]$Encoding = 'UTF8'
    )
    try {
        if (-not (Test-Path -LiteralPath $Path)) {
            $dir = Split-Path -Parent $Path
            if (-not (Test-Path -LiteralPath $dir)) {
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

# ---------------------------------
# ZIP robusto con fallback .NET
# ---------------------------------
function New-ZipRobust {
    param(
        [Parameter(Mandatory)][string]$SourceDir,
        [Parameter(Mandatory)][string]$ZipPath
    )
    $src = Add-LongPathPrefix -Path $SourceDir
    $zip = Add-LongPathPrefix -Path $ZipPath

    if (Test-Path -LiteralPath $ZipPath) {
        try { Remove-Item -LiteralPath $ZipPath -Force -ErrorAction Stop }
        catch {
            Write-Log "Impossibile rimuovere ZIP esistente: $ZipPath. $($_.Exception.Message)" 'ERROR'
            throw
        }
    }

    try {
        Compress-Archive -Path (Join-Path $SourceDir '*') -DestinationPath $ZipPath -Force -ErrorAction Stop
        Write-Log "ZIP creato con Compress-Archive: $ZipPath"
        return
    } catch {
        Write-Log "Compress-Archive fallito, uso fallback .NET: $($_.Exception.Message)" 'WARN'
    }

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        [System.IO.Compression.ZipFile]::CreateFromDirectory($src, $zip, [System.IO.Compression.CompressionLevel]::Optimal, $false)
        Write-Log "ZIP creato con .NET ZipFile: $ZipPath"
    } catch {
        Write-Log "Creazione ZIP fallita anche con .NET: $($_.Exception.Message)" 'ERROR'
        throw
    }
}

# ---------------------------------
# Validazione contenuti ZIP
# ---------------------------------
function Test-ZipContents {
    param(
        [Parameter(Mandatory)][string]  $ZipPath,
        [Parameter(Mandatory)][string[]]$ExpectedRelativeFiles
    )
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        $expected = @($ExpectedRelativeFiles) |
            Where-Object { $_ -ne $null -and $_.ToString().Trim() -ne '' } |
            ForEach-Object { ($_ -replace '\\','/').TrimStart('/') }
        $fs = [System.IO.File]::Open($ZipPath,[System.IO.FileMode]::Open,[System.IO.FileAccess]::Read,[System.IO.FileShare]::Read)
        try {
            $za = New-Object System.IO.Compression.ZipArchive($fs,[System.IO.Compression.ZipArchiveMode]::Read,$false)
            $actual = @(
                $za.Entries |
                Where-Object { $_.FullName -and ($_.FullName -notmatch '/$') } |
                ForEach-Object { ($_.FullName -replace '\\','/').TrimStart('/') }
            )
        } finally { if ($fs) { $fs.Dispose() } }
        $missing = @($expected | Where-Object { $_ -notin $actual })
        $extra   = @($actual   | Where-Object { $_ -notin $expected })
        if ($missing.Count -eq 0 -and $extra.Count -eq 0) {
            Write-Log "Validazione ZIP OK: contenuti attesi presenti"
            return $true
        } else {
            if ($missing.Count -gt 0) { Write-Log "File mancanti nello ZIP: $($missing -join ', ')" 'ERROR' }
            if ($extra.Count   -gt 0) { Write-Log "File extra nello ZIP: $($extra   -join ', ')" 'WARN' }
            return $false
        }
    } catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
}
}

# ---------------------------------
# Helper percorsi / compatibilità
# ---------------------------------
$IsWin = [System.Environment]::OSVersion.Platform -eq 'Win32NT'

function Add-LongPathPrefix {
    param([Parameter(Mandatory)][string]$Path)
    if ($IsWin) {
        if ($Path -like '\\?\*') { return $Path }
        $full = [System.IO.Path]::GetFullPath($Path)
        if ($full.StartsWith('\\')) { return "\\?\UNC\$($full.TrimStart('\'))" }
        return "\\?\$full"
    } else {
        return $Path
    }
}

function Test-Command { param([string]$Name) $null -ne (Get-Command $Name -ErrorAction SilentlyContinue) }

# ---------------------------------
# Destinazione: D:\ poi primo rimovibile, altrimenti corrente
# ---------------------------------
function Get-PortableTarget {
    try {
        if (Test-Path 'D:\') { return 'D:\' }

        try {
            $wmi = Get-CimInstance -Class Win32_LogicalDisk -Filter "DriveType=2" -ErrorAction Stop |
                   Sort-Object DeviceID | Select-Object -First 1
            if ($wmi -and (Test-Path ($wmi.DeviceID + '\'))) { return ($wmi.DeviceID + '\') }
        } catch {}

        if (Test-Command -Name Get-Volume) {
            $vol = Get-Volume | Where-Object DriveType -eq 'Removable' | Select-Object -First 1
            if ($vol) { return ($vol.DriveLetter + ':\') }
        }

        return (Get-Location).Path + '\'
    } catch {
        return (Get-Location).Path + '\'
    }
}

# ---------------------------------
# Creazione file solo se mancanti
# ---------------------------------
function Ensure-File {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Content,
        [ValidateSet('UTF8','ASCII')][string]$Encoding = 'UTF8'
    )
    try {
        if (-not (Test-Path -LiteralPath $Path)) {
            $dir = Split-Path -Parent $Path
            if (-not (Test-Path -LiteralPath $dir)) {
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

# ---------------------------------
# ZIP robusto con fallback .NET
# ---------------------------------
function New-ZipRobust {
    param(
        [Parameter(Mandatory)][string]$SourceDir,
        [Parameter(Mandatory)][string]$ZipPath
    )
    $src = Add-LongPathPrefix -Path $SourceDir
    $zip = Add-LongPathPrefix -Path $ZipPath

    if (Test-Path -LiteralPath $ZipPath) {
        try { Remove-Item -LiteralPath $ZipPath -Force -ErrorAction Stop }
        catch {
            Write-Log "Impossibile rimuovere ZIP esistente: $ZipPath. $($_.Exception.Message)" 'ERROR'
            throw
        }
    }

    try {
        Compress-Archive -Path (Join-Path $SourceDir '*') -DestinationPath $ZipPath -Force -ErrorAction Stop
        Write-Log "ZIP creato con Compress-Archive: $ZipPath"
        return
    } catch {
        Write-Log "Compress-Archive fallito, uso fallback .NET: $($_.Exception.Message)" 'WARN'
    }

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        [System.IO.Compression.ZipFile]::CreateFromDirectory($src, $zip, [System.IO.Compression.CompressionLevel]::Optimal, $false)
        Write-Log "ZIP creato con .NET ZipFile: $ZipPath"
    } catch {
        Write-Log "Creazione ZIP fallita anche con .NET: $($_.Exception.Message)" 'ERROR'
        throw
    }
}

# ---------------------------------
# Validazione contenuti ZIP
# ---------------------------------
function Test-ZipContents {
    param(
        [Parameter(Mandatory)][string]  $ZipPath,
        [Parameter(Mandatory)][string[]]$ExpectedRelativeFiles
    )

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        $expected = @($ExpectedRelativeFiles) |
            Where-Object { $_ -ne $null -and $_.ToString().Trim() -ne '' } |
            ForEach-Object { ($_ -replace '\\','/').TrimStart('/') }

        $fs = [System.IO.File]::Open($ZipPath,
                                     [System.IO.FileMode]::Open,
                                     [System.IO.FileAccess]::Read,
                                     [System.IO.FileShare]::Read)
        try {
            $za = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Read, $false)
            $actual = @(
                $za.Entries |
                Where-Object { $_.FullName -and ($_.FullName -notmatch '/$') } |
                ForEach-Object { ($_.FullName -replace '\\','/').TrimStart('/') }
            )
        }
        finally {
            if ($fs) { $fs.Dispose() }
        }

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
    }
    catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
} | ForEach-Object { $_.FullName.TrimStart('.','/','\') }
            $expected = $ExpectedRelativeFiles | ForEach-Object { $_.Replace('\','/').TrimStart('/') }
            $actual   = $entries | ForEach-Object { $_.Replace('\','/').TrimStart('/') }

            $missing = $expected | Where-Object { $_ -notin $actual }
            $extra   = $actual   | Where-Object { $_ -notin $expected }

            if ($missing.Count -eq 0 -and $extra.Count -eq 0) {
                Write-Log "Validazione ZIP OK: contenuti attesi presenti"
                return $true
            } else {
                if ($missing.Count -gt 0) { Write-Log "File mancanti nello ZIP: $($missing -join ', ')" 'ERROR' }
                if ($extra.Count -gt 0)   { Write-Log "File extra nello ZIP: $($extra -join ', ')"   'WARN'  }
                return $false
            }
        } finally {
            $fs.Dispose()
        }
    } catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
}

# ---------------------------------
# MAIN
# ---------------------------------
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
  <style> body{font-family:system-ui,Segoe UI,Arial;margin:32px} .card{border:1px solid #ddd;padding:16px;border-radius:12px;max-width:900px} .grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))} .badge{display:inline-block;background:#eee;padding:4px 10px;border-radius:999px;margin-right:6px} a.button{display:inline-block;margin-top:12px;border:1px solid #888;padding:8px 12px;border-radius:8px;text-decoration:none} </style>
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

1. Copia l’intera cartella `TPI_evoluto_portabile` in un percorso sicuro
   (es. C:\ oppure su una chiavetta USB).

2. Per avviare la dashboard offline:
   - Doppio clic su `START TPI.cmd`
   - Si aprirà il browser con la dashboard TPI (non serve Python, né Internet).

3. Requisiti:
   - Windows 10 o 11
   - Nessuna installazione aggiuntiva richiesta
   - Modalità **read-only**: non scrive nulla su disco

4. In caso di problemi, apri `index.html` direttamente con il browser (Edge/Chrome/Firefox).
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PRE.txt') -Content $ReadmePre

    $ReadmeProgetto = @'
# TPI_evoluto - Progetto ufficiale

Questa versione portabile contiene la dashboard base (HTML + script) in sola lettura.

Per la versione **completa con FastAPI**, logging, internazionalizzazione (IT, EN, FR, DE), ruoli
(datore di lavoro, revisore, RSPP, lavoratore, supervisore) e dashboard interattiva,
visita il repository ufficiale:

👉 GitHub: https://github.com/aicreator76/TPI_evoluto

---

## Come contribuire
- Clona il repo:
  `git clone https://github.com/aicreator76/TPI_evoluto.git`
- Lavora sui branch:
  - `feature/logging-middleware`
  - `feature/i18n`
- Apri una Pull Request verso `main`.

---

## Contenuto pacchetto portabile
- `index.html` → Dashboard offline
- `START TPI.cmd` / `start.cmd` → Avvio rapido
- `README_PRE.txt` → Guida rapida
- `README_PROGETTO.txt` → Info progetto + link GitHub
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PROGETTO.txt') -Content $ReadmeProgetto

    # --- ZIP + REPORT ---
    $ZIP = Join-Path $TARGET_ROOT 'TPI_evoluto_portabile.zip'
    New-ZipRobust -SourceDir $PKG_DIR -ZipPath $ZIP

    try {
        $sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $ZIP).Hash
        Write-Log "SHA256: $sha"
    } catch {
        Write-Log "Impossibile calcolare SHA256: $($_.Exception.Message)" 'ERROR'
        throw
    }

    $reportPath = Join-Path $TARGET_ROOT 'PACKAGE_REPORT.md'
    $report = @"
# PACKAGE REPORT

- Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Destinazione: $TARGET_ROOT
- Cartella: $PKG_DIR
- ZIP: $ZIP
- SHA256: $sha

## Metadati progetto
- Nome: TPI_evoluto
- Versione: 0.1.0-portable
- Autore: Team TPI
- GitHub: https://github.com/aicreator76/TPI_evoluto

## Verifiche
- [$([bool](Test-Path -LiteralPath $IndexFile) -as [int] -replace '^1$','x' -replace '^0$',' ')] index.html presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'start.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] start.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'START TPI.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] START TPI.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PRE.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PRE.txt presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PROGETTO.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PROGETTO.txt presente
- [x] Zip creato correttamente

## Istruzioni d’uso
- Copia `TPI_evoluto_portabile` o lo `ZIP` su destinazione finale
- Avvia `START TPI.cmd`
"@
    $report | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-Log "Generato report: $reportPath"

    # Validazione ZIP
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
 -ne $null -and # Build-Portable.ps1
# Requisiti: Windows PowerShell 5.1+ o PowerShell 7+. Nessun privilegio elevato richiesto.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ---------------------------------
# Logging
# ---------------------------------
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

# ---------------------------------
# Helper percorsi / compatibilità
# ---------------------------------
$IsWin = [System.Environment]::OSVersion.Platform -eq 'Win32NT'

function Add-LongPathPrefix {
    param([Parameter(Mandatory)][string]$Path)
    if ($IsWin) {
        if ($Path -like '\\?\*') { return $Path }
        $full = [System.IO.Path]::GetFullPath($Path)
        if ($full.StartsWith('\\')) { return "\\?\UNC\$($full.TrimStart('\'))" }
        return "\\?\$full"
    } else {
        return $Path
    }
}

function Test-Command { param([string]$Name) $null -ne (Get-Command $Name -ErrorAction SilentlyContinue) }

# ---------------------------------
# Destinazione: D:\ poi primo rimovibile, altrimenti corrente
# ---------------------------------
function Get-PortableTarget {
    try {
        if (Test-Path 'D:\') { return 'D:\' }

        try {
            $wmi = Get-CimInstance -Class Win32_LogicalDisk -Filter "DriveType=2" -ErrorAction Stop |
                   Sort-Object DeviceID | Select-Object -First 1
            if ($wmi -and (Test-Path ($wmi.DeviceID + '\'))) { return ($wmi.DeviceID + '\') }
        } catch {}

        if (Test-Command -Name Get-Volume) {
            $vol = Get-Volume | Where-Object DriveType -eq 'Removable' | Select-Object -First 1
            if ($vol) { return ($vol.DriveLetter + ':\') }
        }

        return (Get-Location).Path + '\'
    } catch {
        return (Get-Location).Path + '\'
    }
}

# ---------------------------------
# Creazione file solo se mancanti
# ---------------------------------
function Ensure-File {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Content,
        [ValidateSet('UTF8','ASCII')][string]$Encoding = 'UTF8'
    )
    try {
        if (-not (Test-Path -LiteralPath $Path)) {
            $dir = Split-Path -Parent $Path
            if (-not (Test-Path -LiteralPath $dir)) {
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

# ---------------------------------
# ZIP robusto con fallback .NET
# ---------------------------------
function New-ZipRobust {
    param(
        [Parameter(Mandatory)][string]$SourceDir,
        [Parameter(Mandatory)][string]$ZipPath
    )
    $src = Add-LongPathPrefix -Path $SourceDir
    $zip = Add-LongPathPrefix -Path $ZipPath

    if (Test-Path -LiteralPath $ZipPath) {
        try { Remove-Item -LiteralPath $ZipPath -Force -ErrorAction Stop }
        catch {
            Write-Log "Impossibile rimuovere ZIP esistente: $ZipPath. $($_.Exception.Message)" 'ERROR'
            throw
        }
    }

    try {
        Compress-Archive -Path (Join-Path $SourceDir '*') -DestinationPath $ZipPath -Force -ErrorAction Stop
        Write-Log "ZIP creato con Compress-Archive: $ZipPath"
        return
    } catch {
        Write-Log "Compress-Archive fallito, uso fallback .NET: $($_.Exception.Message)" 'WARN'
    }

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        [System.IO.Compression.ZipFile]::CreateFromDirectory($src, $zip, [System.IO.Compression.CompressionLevel]::Optimal, $false)
        Write-Log "ZIP creato con .NET ZipFile: $ZipPath"
    } catch {
        Write-Log "Creazione ZIP fallita anche con .NET: $($_.Exception.Message)" 'ERROR'
        throw
    }
}

# ---------------------------------
# Validazione contenuti ZIP
# ---------------------------------
function Test-ZipContents {
    param(
        [Parameter(Mandatory)][string]  $ZipPath,
        [Parameter(Mandatory)][string[]]$ExpectedRelativeFiles
    )

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        $expected = @($ExpectedRelativeFiles) |
            Where-Object { $_ -ne $null -and $_.ToString().Trim() -ne '' } |
            ForEach-Object { ($_ -replace '\\','/').TrimStart('/') }

        $fs = [System.IO.File]::Open($ZipPath,
                                     [System.IO.FileMode]::Open,
                                     [System.IO.FileAccess]::Read,
                                     [System.IO.FileShare]::Read)
        try {
            $za = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Read, $false)
            $actual = @(
                $za.Entries |
                Where-Object { $_.FullName -and ($_.FullName -notmatch '/$') } |
                ForEach-Object { ($_.FullName -replace '\\','/').TrimStart('/') }
            )
        }
        finally {
            if ($fs) { $fs.Dispose() }
        }

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
    }
    catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
} | ForEach-Object { $_.FullName.TrimStart('.','/','\') }
            $expected = $ExpectedRelativeFiles | ForEach-Object { $_.Replace('\','/').TrimStart('/') }
            $actual   = $entries | ForEach-Object { $_.Replace('\','/').TrimStart('/') }

            $missing = $expected | Where-Object { $_ -notin $actual }
            $extra   = $actual   | Where-Object { $_ -notin $expected }

            if ($missing.Count -eq 0 -and $extra.Count -eq 0) {
                Write-Log "Validazione ZIP OK: contenuti attesi presenti"
                return $true
            } else {
                if ($missing.Count -gt 0) { Write-Log "File mancanti nello ZIP: $($missing -join ', ')" 'ERROR' }
                if ($extra.Count -gt 0)   { Write-Log "File extra nello ZIP: $($extra -join ', ')"   'WARN'  }
                return $false
            }
        } finally {
            $fs.Dispose()
        }
    } catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
}

# ---------------------------------
# MAIN
# ---------------------------------
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
  <style> body{font-family:system-ui,Segoe UI,Arial;margin:32px} .card{border:1px solid #ddd;padding:16px;border-radius:12px;max-width:900px} .grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))} .badge{display:inline-block;background:#eee;padding:4px 10px;border-radius:999px;margin-right:6px} a.button{display:inline-block;margin-top:12px;border:1px solid #888;padding:8px 12px;border-radius:8px;text-decoration:none} </style>
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

1. Copia l’intera cartella `TPI_evoluto_portabile` in un percorso sicuro
   (es. C:\ oppure su una chiavetta USB).

2. Per avviare la dashboard offline:
   - Doppio clic su `START TPI.cmd`
   - Si aprirà il browser con la dashboard TPI (non serve Python, né Internet).

3. Requisiti:
   - Windows 10 o 11
   - Nessuna installazione aggiuntiva richiesta
   - Modalità **read-only**: non scrive nulla su disco

4. In caso di problemi, apri `index.html` direttamente con il browser (Edge/Chrome/Firefox).
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PRE.txt') -Content $ReadmePre

    $ReadmeProgetto = @'
# TPI_evoluto - Progetto ufficiale

Questa versione portabile contiene la dashboard base (HTML + script) in sola lettura.

Per la versione **completa con FastAPI**, logging, internazionalizzazione (IT, EN, FR, DE), ruoli
(datore di lavoro, revisore, RSPP, lavoratore, supervisore) e dashboard interattiva,
visita il repository ufficiale:

👉 GitHub: https://github.com/aicreator76/TPI_evoluto

---

## Come contribuire
- Clona il repo:
  `git clone https://github.com/aicreator76/TPI_evoluto.git`
- Lavora sui branch:
  - `feature/logging-middleware`
  - `feature/i18n`
- Apri una Pull Request verso `main`.

---

## Contenuto pacchetto portabile
- `index.html` → Dashboard offline
- `START TPI.cmd` / `start.cmd` → Avvio rapido
- `README_PRE.txt` → Guida rapida
- `README_PROGETTO.txt` → Info progetto + link GitHub
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PROGETTO.txt') -Content $ReadmeProgetto

    # --- ZIP + REPORT ---
    $ZIP = Join-Path $TARGET_ROOT 'TPI_evoluto_portabile.zip'
    New-ZipRobust -SourceDir $PKG_DIR -ZipPath $ZIP

    try {
        $sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $ZIP).Hash
        Write-Log "SHA256: $sha"
    } catch {
        Write-Log "Impossibile calcolare SHA256: $($_.Exception.Message)" 'ERROR'
        throw
    }

    $reportPath = Join-Path $TARGET_ROOT 'PACKAGE_REPORT.md'
    $report = @"
# PACKAGE REPORT

- Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Destinazione: $TARGET_ROOT
- Cartella: $PKG_DIR
- ZIP: $ZIP
- SHA256: $sha

## Metadati progetto
- Nome: TPI_evoluto
- Versione: 0.1.0-portable
- Autore: Team TPI
- GitHub: https://github.com/aicreator76/TPI_evoluto

## Verifiche
- [$([bool](Test-Path -LiteralPath $IndexFile) -as [int] -replace '^1$','x' -replace '^0$',' ')] index.html presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'start.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] start.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'START TPI.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] START TPI.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PRE.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PRE.txt presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PROGETTO.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PROGETTO.txt presente
- [x] Zip creato correttamente

## Istruzioni d’uso
- Copia `TPI_evoluto_portabile` o lo `ZIP` su destinazione finale
- Avvia `START TPI.cmd`
"@
    $report | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-Log "Generato report: $reportPath"

    # Validazione ZIP
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
.ToString().Trim() -ne '' } |
            ForEach-Object { (# Build-Portable.ps1
# Requisiti: Windows PowerShell 5.1+ o PowerShell 7+. Nessun privilegio elevato richiesto.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ---------------------------------
# Logging
# ---------------------------------
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

# ---------------------------------
# Helper percorsi / compatibilità
# ---------------------------------
$IsWin = [System.Environment]::OSVersion.Platform -eq 'Win32NT'

function Add-LongPathPrefix {
    param([Parameter(Mandatory)][string]$Path)
    if ($IsWin) {
        if ($Path -like '\\?\*') { return $Path }
        $full = [System.IO.Path]::GetFullPath($Path)
        if ($full.StartsWith('\\')) { return "\\?\UNC\$($full.TrimStart('\'))" }
        return "\\?\$full"
    } else {
        return $Path
    }
}

function Test-Command { param([string]$Name) $null -ne (Get-Command $Name -ErrorAction SilentlyContinue) }

# ---------------------------------
# Destinazione: D:\ poi primo rimovibile, altrimenti corrente
# ---------------------------------
function Get-PortableTarget {
    try {
        if (Test-Path 'D:\') { return 'D:\' }

        try {
            $wmi = Get-CimInstance -Class Win32_LogicalDisk -Filter "DriveType=2" -ErrorAction Stop |
                   Sort-Object DeviceID | Select-Object -First 1
            if ($wmi -and (Test-Path ($wmi.DeviceID + '\'))) { return ($wmi.DeviceID + '\') }
        } catch {}

        if (Test-Command -Name Get-Volume) {
            $vol = Get-Volume | Where-Object DriveType -eq 'Removable' | Select-Object -First 1
            if ($vol) { return ($vol.DriveLetter + ':\') }
        }

        return (Get-Location).Path + '\'
    } catch {
        return (Get-Location).Path + '\'
    }
}

# ---------------------------------
# Creazione file solo se mancanti
# ---------------------------------
function Ensure-File {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Content,
        [ValidateSet('UTF8','ASCII')][string]$Encoding = 'UTF8'
    )
    try {
        if (-not (Test-Path -LiteralPath $Path)) {
            $dir = Split-Path -Parent $Path
            if (-not (Test-Path -LiteralPath $dir)) {
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

# ---------------------------------
# ZIP robusto con fallback .NET
# ---------------------------------
function New-ZipRobust {
    param(
        [Parameter(Mandatory)][string]$SourceDir,
        [Parameter(Mandatory)][string]$ZipPath
    )
    $src = Add-LongPathPrefix -Path $SourceDir
    $zip = Add-LongPathPrefix -Path $ZipPath

    if (Test-Path -LiteralPath $ZipPath) {
        try { Remove-Item -LiteralPath $ZipPath -Force -ErrorAction Stop }
        catch {
            Write-Log "Impossibile rimuovere ZIP esistente: $ZipPath. $($_.Exception.Message)" 'ERROR'
            throw
        }
    }

    try {
        Compress-Archive -Path (Join-Path $SourceDir '*') -DestinationPath $ZipPath -Force -ErrorAction Stop
        Write-Log "ZIP creato con Compress-Archive: $ZipPath"
        return
    } catch {
        Write-Log "Compress-Archive fallito, uso fallback .NET: $($_.Exception.Message)" 'WARN'
    }

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        [System.IO.Compression.ZipFile]::CreateFromDirectory($src, $zip, [System.IO.Compression.CompressionLevel]::Optimal, $false)
        Write-Log "ZIP creato con .NET ZipFile: $ZipPath"
    } catch {
        Write-Log "Creazione ZIP fallita anche con .NET: $($_.Exception.Message)" 'ERROR'
        throw
    }
}

# ---------------------------------
# Validazione contenuti ZIP
# ---------------------------------
function Test-ZipContents {
    param(
        [Parameter(Mandatory)][string]  $ZipPath,
        [Parameter(Mandatory)][string[]]$ExpectedRelativeFiles
    )

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        $expected = @($ExpectedRelativeFiles) |
            Where-Object { $_ -ne $null -and $_.ToString().Trim() -ne '' } |
            ForEach-Object { ($_ -replace '\\','/').TrimStart('/') }

        $fs = [System.IO.File]::Open($ZipPath,
                                     [System.IO.FileMode]::Open,
                                     [System.IO.FileAccess]::Read,
                                     [System.IO.FileShare]::Read)
        try {
            $za = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Read, $false)
            $actual = @(
                $za.Entries |
                Where-Object { $_.FullName -and ($_.FullName -notmatch '/$') } |
                ForEach-Object { ($_.FullName -replace '\\','/').TrimStart('/') }
            )
        }
        finally {
            if ($fs) { $fs.Dispose() }
        }

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
    }
    catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
} | ForEach-Object { $_.FullName.TrimStart('.','/','\') }
            $expected = $ExpectedRelativeFiles | ForEach-Object { $_.Replace('\','/').TrimStart('/') }
            $actual   = $entries | ForEach-Object { $_.Replace('\','/').TrimStart('/') }

            $missing = $expected | Where-Object { $_ -notin $actual }
            $extra   = $actual   | Where-Object { $_ -notin $expected }

            if ($missing.Count -eq 0 -and $extra.Count -eq 0) {
                Write-Log "Validazione ZIP OK: contenuti attesi presenti"
                return $true
            } else {
                if ($missing.Count -gt 0) { Write-Log "File mancanti nello ZIP: $($missing -join ', ')" 'ERROR' }
                if ($extra.Count -gt 0)   { Write-Log "File extra nello ZIP: $($extra -join ', ')"   'WARN'  }
                return $false
            }
        } finally {
            $fs.Dispose()
        }
    } catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
}

# ---------------------------------
# MAIN
# ---------------------------------
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
  <style> body{font-family:system-ui,Segoe UI,Arial;margin:32px} .card{border:1px solid #ddd;padding:16px;border-radius:12px;max-width:900px} .grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))} .badge{display:inline-block;background:#eee;padding:4px 10px;border-radius:999px;margin-right:6px} a.button{display:inline-block;margin-top:12px;border:1px solid #888;padding:8px 12px;border-radius:8px;text-decoration:none} </style>
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

1. Copia l’intera cartella `TPI_evoluto_portabile` in un percorso sicuro
   (es. C:\ oppure su una chiavetta USB).

2. Per avviare la dashboard offline:
   - Doppio clic su `START TPI.cmd`
   - Si aprirà il browser con la dashboard TPI (non serve Python, né Internet).

3. Requisiti:
   - Windows 10 o 11
   - Nessuna installazione aggiuntiva richiesta
   - Modalità **read-only**: non scrive nulla su disco

4. In caso di problemi, apri `index.html` direttamente con il browser (Edge/Chrome/Firefox).
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PRE.txt') -Content $ReadmePre

    $ReadmeProgetto = @'
# TPI_evoluto - Progetto ufficiale

Questa versione portabile contiene la dashboard base (HTML + script) in sola lettura.

Per la versione **completa con FastAPI**, logging, internazionalizzazione (IT, EN, FR, DE), ruoli
(datore di lavoro, revisore, RSPP, lavoratore, supervisore) e dashboard interattiva,
visita il repository ufficiale:

👉 GitHub: https://github.com/aicreator76/TPI_evoluto

---

## Come contribuire
- Clona il repo:
  `git clone https://github.com/aicreator76/TPI_evoluto.git`
- Lavora sui branch:
  - `feature/logging-middleware`
  - `feature/i18n`
- Apri una Pull Request verso `main`.

---

## Contenuto pacchetto portabile
- `index.html` → Dashboard offline
- `START TPI.cmd` / `start.cmd` → Avvio rapido
- `README_PRE.txt` → Guida rapida
- `README_PROGETTO.txt` → Info progetto + link GitHub
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PROGETTO.txt') -Content $ReadmeProgetto

    # --- ZIP + REPORT ---
    $ZIP = Join-Path $TARGET_ROOT 'TPI_evoluto_portabile.zip'
    New-ZipRobust -SourceDir $PKG_DIR -ZipPath $ZIP

    try {
        $sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $ZIP).Hash
        Write-Log "SHA256: $sha"
    } catch {
        Write-Log "Impossibile calcolare SHA256: $($_.Exception.Message)" 'ERROR'
        throw
    }

    $reportPath = Join-Path $TARGET_ROOT 'PACKAGE_REPORT.md'
    $report = @"
# PACKAGE REPORT

- Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Destinazione: $TARGET_ROOT
- Cartella: $PKG_DIR
- ZIP: $ZIP
- SHA256: $sha

## Metadati progetto
- Nome: TPI_evoluto
- Versione: 0.1.0-portable
- Autore: Team TPI
- GitHub: https://github.com/aicreator76/TPI_evoluto

## Verifiche
- [$([bool](Test-Path -LiteralPath $IndexFile) -as [int] -replace '^1$','x' -replace '^0$',' ')] index.html presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'start.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] start.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'START TPI.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] START TPI.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PRE.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PRE.txt presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PROGETTO.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PROGETTO.txt presente
- [x] Zip creato correttamente

## Istruzioni d’uso
- Copia `TPI_evoluto_portabile` o lo `ZIP` su destinazione finale
- Avvia `START TPI.cmd`
"@
    $report | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-Log "Generato report: $reportPath"

    # Validazione ZIP
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
 -replace '\\','/').TrimStart('/') }
        $fs = [System.IO.File]::Open($ZipPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::Read)
        try {
            $za = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Read, $false)
            $actual = @(
                $za.Entries |
                Where-Object { # Build-Portable.ps1
# Requisiti: Windows PowerShell 5.1+ o PowerShell 7+. Nessun privilegio elevato richiesto.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ---------------------------------
# Logging
# ---------------------------------
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

# ---------------------------------
# Helper percorsi / compatibilità
# ---------------------------------
$IsWin = [System.Environment]::OSVersion.Platform -eq 'Win32NT'

function Add-LongPathPrefix {
    param([Parameter(Mandatory)][string]$Path)
    if ($IsWin) {
        if ($Path -like '\\?\*') { return $Path }
        $full = [System.IO.Path]::GetFullPath($Path)
        if ($full.StartsWith('\\')) { return "\\?\UNC\$($full.TrimStart('\'))" }
        return "\\?\$full"
    } else {
        return $Path
    }
}

function Test-Command { param([string]$Name) $null -ne (Get-Command $Name -ErrorAction SilentlyContinue) }

# ---------------------------------
# Destinazione: D:\ poi primo rimovibile, altrimenti corrente
# ---------------------------------
function Get-PortableTarget {
    try {
        if (Test-Path 'D:\') { return 'D:\' }

        try {
            $wmi = Get-CimInstance -Class Win32_LogicalDisk -Filter "DriveType=2" -ErrorAction Stop |
                   Sort-Object DeviceID | Select-Object -First 1
            if ($wmi -and (Test-Path ($wmi.DeviceID + '\'))) { return ($wmi.DeviceID + '\') }
        } catch {}

        if (Test-Command -Name Get-Volume) {
            $vol = Get-Volume | Where-Object DriveType -eq 'Removable' | Select-Object -First 1
            if ($vol) { return ($vol.DriveLetter + ':\') }
        }

        return (Get-Location).Path + '\'
    } catch {
        return (Get-Location).Path + '\'
    }
}

# ---------------------------------
# Creazione file solo se mancanti
# ---------------------------------
function Ensure-File {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Content,
        [ValidateSet('UTF8','ASCII')][string]$Encoding = 'UTF8'
    )
    try {
        if (-not (Test-Path -LiteralPath $Path)) {
            $dir = Split-Path -Parent $Path
            if (-not (Test-Path -LiteralPath $dir)) {
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

# ---------------------------------
# ZIP robusto con fallback .NET
# ---------------------------------
function New-ZipRobust {
    param(
        [Parameter(Mandatory)][string]$SourceDir,
        [Parameter(Mandatory)][string]$ZipPath
    )
    $src = Add-LongPathPrefix -Path $SourceDir
    $zip = Add-LongPathPrefix -Path $ZipPath

    if (Test-Path -LiteralPath $ZipPath) {
        try { Remove-Item -LiteralPath $ZipPath -Force -ErrorAction Stop }
        catch {
            Write-Log "Impossibile rimuovere ZIP esistente: $ZipPath. $($_.Exception.Message)" 'ERROR'
            throw
        }
    }

    try {
        Compress-Archive -Path (Join-Path $SourceDir '*') -DestinationPath $ZipPath -Force -ErrorAction Stop
        Write-Log "ZIP creato con Compress-Archive: $ZipPath"
        return
    } catch {
        Write-Log "Compress-Archive fallito, uso fallback .NET: $($_.Exception.Message)" 'WARN'
    }

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        [System.IO.Compression.ZipFile]::CreateFromDirectory($src, $zip, [System.IO.Compression.CompressionLevel]::Optimal, $false)
        Write-Log "ZIP creato con .NET ZipFile: $ZipPath"
    } catch {
        Write-Log "Creazione ZIP fallita anche con .NET: $($_.Exception.Message)" 'ERROR'
        throw
    }
}

# ---------------------------------
# Validazione contenuti ZIP
# ---------------------------------
function Test-ZipContents {
    param(
        [Parameter(Mandatory)][string]  $ZipPath,
        [Parameter(Mandatory)][string[]]$ExpectedRelativeFiles
    )

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        $expected = @($ExpectedRelativeFiles) |
            Where-Object { $_ -ne $null -and $_.ToString().Trim() -ne '' } |
            ForEach-Object { ($_ -replace '\\','/').TrimStart('/') }

        $fs = [System.IO.File]::Open($ZipPath,
                                     [System.IO.FileMode]::Open,
                                     [System.IO.FileAccess]::Read,
                                     [System.IO.FileShare]::Read)
        try {
            $za = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Read, $false)
            $actual = @(
                $za.Entries |
                Where-Object { $_.FullName -and ($_.FullName -notmatch '/$') } |
                ForEach-Object { ($_.FullName -replace '\\','/').TrimStart('/') }
            )
        }
        finally {
            if ($fs) { $fs.Dispose() }
        }

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
    }
    catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
} | ForEach-Object { $_.FullName.TrimStart('.','/','\') }
            $expected = $ExpectedRelativeFiles | ForEach-Object { $_.Replace('\','/').TrimStart('/') }
            $actual   = $entries | ForEach-Object { $_.Replace('\','/').TrimStart('/') }

            $missing = $expected | Where-Object { $_ -notin $actual }
            $extra   = $actual   | Where-Object { $_ -notin $expected }

            if ($missing.Count -eq 0 -and $extra.Count -eq 0) {
                Write-Log "Validazione ZIP OK: contenuti attesi presenti"
                return $true
            } else {
                if ($missing.Count -gt 0) { Write-Log "File mancanti nello ZIP: $($missing -join ', ')" 'ERROR' }
                if ($extra.Count -gt 0)   { Write-Log "File extra nello ZIP: $($extra -join ', ')"   'WARN'  }
                return $false
            }
        } finally {
            $fs.Dispose()
        }
    } catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
}

# ---------------------------------
# MAIN
# ---------------------------------
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
  <style> body{font-family:system-ui,Segoe UI,Arial;margin:32px} .card{border:1px solid #ddd;padding:16px;border-radius:12px;max-width:900px} .grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))} .badge{display:inline-block;background:#eee;padding:4px 10px;border-radius:999px;margin-right:6px} a.button{display:inline-block;margin-top:12px;border:1px solid #888;padding:8px 12px;border-radius:8px;text-decoration:none} </style>
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

1. Copia l’intera cartella `TPI_evoluto_portabile` in un percorso sicuro
   (es. C:\ oppure su una chiavetta USB).

2. Per avviare la dashboard offline:
   - Doppio clic su `START TPI.cmd`
   - Si aprirà il browser con la dashboard TPI (non serve Python, né Internet).

3. Requisiti:
   - Windows 10 o 11
   - Nessuna installazione aggiuntiva richiesta
   - Modalità **read-only**: non scrive nulla su disco

4. In caso di problemi, apri `index.html` direttamente con il browser (Edge/Chrome/Firefox).
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PRE.txt') -Content $ReadmePre

    $ReadmeProgetto = @'
# TPI_evoluto - Progetto ufficiale

Questa versione portabile contiene la dashboard base (HTML + script) in sola lettura.

Per la versione **completa con FastAPI**, logging, internazionalizzazione (IT, EN, FR, DE), ruoli
(datore di lavoro, revisore, RSPP, lavoratore, supervisore) e dashboard interattiva,
visita il repository ufficiale:

👉 GitHub: https://github.com/aicreator76/TPI_evoluto

---

## Come contribuire
- Clona il repo:
  `git clone https://github.com/aicreator76/TPI_evoluto.git`
- Lavora sui branch:
  - `feature/logging-middleware`
  - `feature/i18n`
- Apri una Pull Request verso `main`.

---

## Contenuto pacchetto portabile
- `index.html` → Dashboard offline
- `START TPI.cmd` / `start.cmd` → Avvio rapido
- `README_PRE.txt` → Guida rapida
- `README_PROGETTO.txt` → Info progetto + link GitHub
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PROGETTO.txt') -Content $ReadmeProgetto

    # --- ZIP + REPORT ---
    $ZIP = Join-Path $TARGET_ROOT 'TPI_evoluto_portabile.zip'
    New-ZipRobust -SourceDir $PKG_DIR -ZipPath $ZIP

    try {
        $sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $ZIP).Hash
        Write-Log "SHA256: $sha"
    } catch {
        Write-Log "Impossibile calcolare SHA256: $($_.Exception.Message)" 'ERROR'
        throw
    }

    $reportPath = Join-Path $TARGET_ROOT 'PACKAGE_REPORT.md'
    $report = @"
# PACKAGE REPORT

- Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Destinazione: $TARGET_ROOT
- Cartella: $PKG_DIR
- ZIP: $ZIP
- SHA256: $sha

## Metadati progetto
- Nome: TPI_evoluto
- Versione: 0.1.0-portable
- Autore: Team TPI
- GitHub: https://github.com/aicreator76/TPI_evoluto

## Verifiche
- [$([bool](Test-Path -LiteralPath $IndexFile) -as [int] -replace '^1$','x' -replace '^0$',' ')] index.html presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'start.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] start.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'START TPI.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] START TPI.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PRE.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PRE.txt presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PROGETTO.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PROGETTO.txt presente
- [x] Zip creato correttamente

## Istruzioni d’uso
- Copia `TPI_evoluto_portabile` o lo `ZIP` su destinazione finale
- Avvia `START TPI.cmd`
"@
    $report | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-Log "Generato report: $reportPath"

    # Validazione ZIP
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
.FullName -and (# Build-Portable.ps1
# Requisiti: Windows PowerShell 5.1+ o PowerShell 7+. Nessun privilegio elevato richiesto.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ---------------------------------
# Logging
# ---------------------------------
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

# ---------------------------------
# Helper percorsi / compatibilità
# ---------------------------------
$IsWin = [System.Environment]::OSVersion.Platform -eq 'Win32NT'

function Add-LongPathPrefix {
    param([Parameter(Mandatory)][string]$Path)
    if ($IsWin) {
        if ($Path -like '\\?\*') { return $Path }
        $full = [System.IO.Path]::GetFullPath($Path)
        if ($full.StartsWith('\\')) { return "\\?\UNC\$($full.TrimStart('\'))" }
        return "\\?\$full"
    } else {
        return $Path
    }
}

function Test-Command { param([string]$Name) $null -ne (Get-Command $Name -ErrorAction SilentlyContinue) }

# ---------------------------------
# Destinazione: D:\ poi primo rimovibile, altrimenti corrente
# ---------------------------------
function Get-PortableTarget {
    try {
        if (Test-Path 'D:\') { return 'D:\' }

        try {
            $wmi = Get-CimInstance -Class Win32_LogicalDisk -Filter "DriveType=2" -ErrorAction Stop |
                   Sort-Object DeviceID | Select-Object -First 1
            if ($wmi -and (Test-Path ($wmi.DeviceID + '\'))) { return ($wmi.DeviceID + '\') }
        } catch {}

        if (Test-Command -Name Get-Volume) {
            $vol = Get-Volume | Where-Object DriveType -eq 'Removable' | Select-Object -First 1
            if ($vol) { return ($vol.DriveLetter + ':\') }
        }

        return (Get-Location).Path + '\'
    } catch {
        return (Get-Location).Path + '\'
    }
}

# ---------------------------------
# Creazione file solo se mancanti
# ---------------------------------
function Ensure-File {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Content,
        [ValidateSet('UTF8','ASCII')][string]$Encoding = 'UTF8'
    )
    try {
        if (-not (Test-Path -LiteralPath $Path)) {
            $dir = Split-Path -Parent $Path
            if (-not (Test-Path -LiteralPath $dir)) {
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

# ---------------------------------
# ZIP robusto con fallback .NET
# ---------------------------------
function New-ZipRobust {
    param(
        [Parameter(Mandatory)][string]$SourceDir,
        [Parameter(Mandatory)][string]$ZipPath
    )
    $src = Add-LongPathPrefix -Path $SourceDir
    $zip = Add-LongPathPrefix -Path $ZipPath

    if (Test-Path -LiteralPath $ZipPath) {
        try { Remove-Item -LiteralPath $ZipPath -Force -ErrorAction Stop }
        catch {
            Write-Log "Impossibile rimuovere ZIP esistente: $ZipPath. $($_.Exception.Message)" 'ERROR'
            throw
        }
    }

    try {
        Compress-Archive -Path (Join-Path $SourceDir '*') -DestinationPath $ZipPath -Force -ErrorAction Stop
        Write-Log "ZIP creato con Compress-Archive: $ZipPath"
        return
    } catch {
        Write-Log "Compress-Archive fallito, uso fallback .NET: $($_.Exception.Message)" 'WARN'
    }

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        [System.IO.Compression.ZipFile]::CreateFromDirectory($src, $zip, [System.IO.Compression.CompressionLevel]::Optimal, $false)
        Write-Log "ZIP creato con .NET ZipFile: $ZipPath"
    } catch {
        Write-Log "Creazione ZIP fallita anche con .NET: $($_.Exception.Message)" 'ERROR'
        throw
    }
}

# ---------------------------------
# Validazione contenuti ZIP
# ---------------------------------
function Test-ZipContents {
    param(
        [Parameter(Mandatory)][string]  $ZipPath,
        [Parameter(Mandatory)][string[]]$ExpectedRelativeFiles
    )

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        $expected = @($ExpectedRelativeFiles) |
            Where-Object { $_ -ne $null -and $_.ToString().Trim() -ne '' } |
            ForEach-Object { ($_ -replace '\\','/').TrimStart('/') }

        $fs = [System.IO.File]::Open($ZipPath,
                                     [System.IO.FileMode]::Open,
                                     [System.IO.FileAccess]::Read,
                                     [System.IO.FileShare]::Read)
        try {
            $za = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Read, $false)
            $actual = @(
                $za.Entries |
                Where-Object { $_.FullName -and ($_.FullName -notmatch '/$') } |
                ForEach-Object { ($_.FullName -replace '\\','/').TrimStart('/') }
            )
        }
        finally {
            if ($fs) { $fs.Dispose() }
        }

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
    }
    catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
} | ForEach-Object { $_.FullName.TrimStart('.','/','\') }
            $expected = $ExpectedRelativeFiles | ForEach-Object { $_.Replace('\','/').TrimStart('/') }
            $actual   = $entries | ForEach-Object { $_.Replace('\','/').TrimStart('/') }

            $missing = $expected | Where-Object { $_ -notin $actual }
            $extra   = $actual   | Where-Object { $_ -notin $expected }

            if ($missing.Count -eq 0 -and $extra.Count -eq 0) {
                Write-Log "Validazione ZIP OK: contenuti attesi presenti"
                return $true
            } else {
                if ($missing.Count -gt 0) { Write-Log "File mancanti nello ZIP: $($missing -join ', ')" 'ERROR' }
                if ($extra.Count -gt 0)   { Write-Log "File extra nello ZIP: $($extra -join ', ')"   'WARN'  }
                return $false
            }
        } finally {
            $fs.Dispose()
        }
    } catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
}

# ---------------------------------
# MAIN
# ---------------------------------
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
  <style> body{font-family:system-ui,Segoe UI,Arial;margin:32px} .card{border:1px solid #ddd;padding:16px;border-radius:12px;max-width:900px} .grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))} .badge{display:inline-block;background:#eee;padding:4px 10px;border-radius:999px;margin-right:6px} a.button{display:inline-block;margin-top:12px;border:1px solid #888;padding:8px 12px;border-radius:8px;text-decoration:none} </style>
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

1. Copia l’intera cartella `TPI_evoluto_portabile` in un percorso sicuro
   (es. C:\ oppure su una chiavetta USB).

2. Per avviare la dashboard offline:
   - Doppio clic su `START TPI.cmd`
   - Si aprirà il browser con la dashboard TPI (non serve Python, né Internet).

3. Requisiti:
   - Windows 10 o 11
   - Nessuna installazione aggiuntiva richiesta
   - Modalità **read-only**: non scrive nulla su disco

4. In caso di problemi, apri `index.html` direttamente con il browser (Edge/Chrome/Firefox).
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PRE.txt') -Content $ReadmePre

    $ReadmeProgetto = @'
# TPI_evoluto - Progetto ufficiale

Questa versione portabile contiene la dashboard base (HTML + script) in sola lettura.

Per la versione **completa con FastAPI**, logging, internazionalizzazione (IT, EN, FR, DE), ruoli
(datore di lavoro, revisore, RSPP, lavoratore, supervisore) e dashboard interattiva,
visita il repository ufficiale:

👉 GitHub: https://github.com/aicreator76/TPI_evoluto

---

## Come contribuire
- Clona il repo:
  `git clone https://github.com/aicreator76/TPI_evoluto.git`
- Lavora sui branch:
  - `feature/logging-middleware`
  - `feature/i18n`
- Apri una Pull Request verso `main`.

---

## Contenuto pacchetto portabile
- `index.html` → Dashboard offline
- `START TPI.cmd` / `start.cmd` → Avvio rapido
- `README_PRE.txt` → Guida rapida
- `README_PROGETTO.txt` → Info progetto + link GitHub
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PROGETTO.txt') -Content $ReadmeProgetto

    # --- ZIP + REPORT ---
    $ZIP = Join-Path $TARGET_ROOT 'TPI_evoluto_portabile.zip'
    New-ZipRobust -SourceDir $PKG_DIR -ZipPath $ZIP

    try {
        $sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $ZIP).Hash
        Write-Log "SHA256: $sha"
    } catch {
        Write-Log "Impossibile calcolare SHA256: $($_.Exception.Message)" 'ERROR'
        throw
    }

    $reportPath = Join-Path $TARGET_ROOT 'PACKAGE_REPORT.md'
    $report = @"
# PACKAGE REPORT

- Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Destinazione: $TARGET_ROOT
- Cartella: $PKG_DIR
- ZIP: $ZIP
- SHA256: $sha

## Metadati progetto
- Nome: TPI_evoluto
- Versione: 0.1.0-portable
- Autore: Team TPI
- GitHub: https://github.com/aicreator76/TPI_evoluto

## Verifiche
- [$([bool](Test-Path -LiteralPath $IndexFile) -as [int] -replace '^1$','x' -replace '^0$',' ')] index.html presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'start.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] start.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'START TPI.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] START TPI.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PRE.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PRE.txt presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PROGETTO.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PROGETTO.txt presente
- [x] Zip creato correttamente

## Istruzioni d’uso
- Copia `TPI_evoluto_portabile` o lo `ZIP` su destinazione finale
- Avvia `START TPI.cmd`
"@
    $report | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-Log "Generato report: $reportPath"

    # Validazione ZIP
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
.FullName -notmatch '/ | ForEach-Object { $_.FullName.TrimStart('.','/','\') }
            $expected = $ExpectedRelativeFiles | ForEach-Object { $_.Replace('\','/').TrimStart('/') }
            $actual   = $entries | ForEach-Object { $_.Replace('\','/').TrimStart('/') }

            $missing = $expected | Where-Object { $_ -notin $actual }
            $extra   = $actual   | Where-Object { $_ -notin $expected }

            if ($missing.Count -eq 0 -and $extra.Count -eq 0) {
                Write-Log "Validazione ZIP OK: contenuti attesi presenti"
                return $true
            } else {
                if ($missing.Count -gt 0) { Write-Log "File mancanti nello ZIP: $($missing -join ', ')" 'ERROR' }
                if ($extra.Count -gt 0)   { Write-Log "File extra nello ZIP: $($extra -join ', ')"   'WARN'  }
                return $false
            }
        } finally {
            $fs.Dispose()
        }
    } catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
}

# ---------------------------------
# MAIN
# ---------------------------------
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
  <style> body{font-family:system-ui,Segoe UI,Arial;margin:32px} .card{border:1px solid #ddd;padding:16px;border-radius:12px;max-width:900px} .grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))} .badge{display:inline-block;background:#eee;padding:4px 10px;border-radius:999px;margin-right:6px} a.button{display:inline-block;margin-top:12px;border:1px solid #888;padding:8px 12px;border-radius:8px;text-decoration:none} </style>
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

1. Copia l’intera cartella `TPI_evoluto_portabile` in un percorso sicuro
   (es. C:\ oppure su una chiavetta USB).

2. Per avviare la dashboard offline:
   - Doppio clic su `START TPI.cmd`
   - Si aprirà il browser con la dashboard TPI (non serve Python, né Internet).

3. Requisiti:
   - Windows 10 o 11
   - Nessuna installazione aggiuntiva richiesta
   - Modalità **read-only**: non scrive nulla su disco

4. In caso di problemi, apri `index.html` direttamente con il browser (Edge/Chrome/Firefox).
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PRE.txt') -Content $ReadmePre

    $ReadmeProgetto = @'
# TPI_evoluto - Progetto ufficiale

Questa versione portabile contiene la dashboard base (HTML + script) in sola lettura.

Per la versione **completa con FastAPI**, logging, internazionalizzazione (IT, EN, FR, DE), ruoli
(datore di lavoro, revisore, RSPP, lavoratore, supervisore) e dashboard interattiva,
visita il repository ufficiale:

👉 GitHub: https://github.com/aicreator76/TPI_evoluto

---

## Come contribuire
- Clona il repo:
  `git clone https://github.com/aicreator76/TPI_evoluto.git`
- Lavora sui branch:
  - `feature/logging-middleware`
  - `feature/i18n`
- Apri una Pull Request verso `main`.

---

## Contenuto pacchetto portabile
- `index.html` → Dashboard offline
- `START TPI.cmd` / `start.cmd` → Avvio rapido
- `README_PRE.txt` → Guida rapida
- `README_PROGETTO.txt` → Info progetto + link GitHub
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PROGETTO.txt') -Content $ReadmeProgetto

    # --- ZIP + REPORT ---
    $ZIP = Join-Path $TARGET_ROOT 'TPI_evoluto_portabile.zip'
    New-ZipRobust -SourceDir $PKG_DIR -ZipPath $ZIP

    try {
        $sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $ZIP).Hash
        Write-Log "SHA256: $sha"
    } catch {
        Write-Log "Impossibile calcolare SHA256: $($_.Exception.Message)" 'ERROR'
        throw
    }

    $reportPath = Join-Path $TARGET_ROOT 'PACKAGE_REPORT.md'
    $report = @"
# PACKAGE REPORT

- Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Destinazione: $TARGET_ROOT
- Cartella: $PKG_DIR
- ZIP: $ZIP
- SHA256: $sha

## Metadati progetto
- Nome: TPI_evoluto
- Versione: 0.1.0-portable
- Autore: Team TPI
- GitHub: https://github.com/aicreator76/TPI_evoluto

## Verifiche
- [$([bool](Test-Path -LiteralPath $IndexFile) -as [int] -replace '^1$','x' -replace '^0$',' ')] index.html presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'start.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] start.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'START TPI.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] START TPI.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PRE.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PRE.txt presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PROGETTO.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PROGETTO.txt presente
- [x] Zip creato correttamente

## Istruzioni d’uso
- Copia `TPI_evoluto_portabile` o lo `ZIP` su destinazione finale
- Avvia `START TPI.cmd`
"@
    $report | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-Log "Generato report: $reportPath"

    # Validazione ZIP
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
) } |
                ForEach-Object { (# Build-Portable.ps1
# Requisiti: Windows PowerShell 5.1+ o PowerShell 7+. Nessun privilegio elevato richiesto.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ---------------------------------
# Logging
# ---------------------------------
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

# ---------------------------------
# Helper percorsi / compatibilità
# ---------------------------------
$IsWin = [System.Environment]::OSVersion.Platform -eq 'Win32NT'

function Add-LongPathPrefix {
    param([Parameter(Mandatory)][string]$Path)
    if ($IsWin) {
        if ($Path -like '\\?\*') { return $Path }
        $full = [System.IO.Path]::GetFullPath($Path)
        if ($full.StartsWith('\\')) { return "\\?\UNC\$($full.TrimStart('\'))" }
        return "\\?\$full"
    } else {
        return $Path
    }
}

function Test-Command { param([string]$Name) $null -ne (Get-Command $Name -ErrorAction SilentlyContinue) }

# ---------------------------------
# Destinazione: D:\ poi primo rimovibile, altrimenti corrente
# ---------------------------------
function Get-PortableTarget {
    try {
        if (Test-Path 'D:\') { return 'D:\' }

        try {
            $wmi = Get-CimInstance -Class Win32_LogicalDisk -Filter "DriveType=2" -ErrorAction Stop |
                   Sort-Object DeviceID | Select-Object -First 1
            if ($wmi -and (Test-Path ($wmi.DeviceID + '\'))) { return ($wmi.DeviceID + '\') }
        } catch {}

        if (Test-Command -Name Get-Volume) {
            $vol = Get-Volume | Where-Object DriveType -eq 'Removable' | Select-Object -First 1
            if ($vol) { return ($vol.DriveLetter + ':\') }
        }

        return (Get-Location).Path + '\'
    } catch {
        return (Get-Location).Path + '\'
    }
}

# ---------------------------------
# Creazione file solo se mancanti
# ---------------------------------
function Ensure-File {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Content,
        [ValidateSet('UTF8','ASCII')][string]$Encoding = 'UTF8'
    )
    try {
        if (-not (Test-Path -LiteralPath $Path)) {
            $dir = Split-Path -Parent $Path
            if (-not (Test-Path -LiteralPath $dir)) {
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

# ---------------------------------
# ZIP robusto con fallback .NET
# ---------------------------------
function New-ZipRobust {
    param(
        [Parameter(Mandatory)][string]$SourceDir,
        [Parameter(Mandatory)][string]$ZipPath
    )
    $src = Add-LongPathPrefix -Path $SourceDir
    $zip = Add-LongPathPrefix -Path $ZipPath

    if (Test-Path -LiteralPath $ZipPath) {
        try { Remove-Item -LiteralPath $ZipPath -Force -ErrorAction Stop }
        catch {
            Write-Log "Impossibile rimuovere ZIP esistente: $ZipPath. $($_.Exception.Message)" 'ERROR'
            throw
        }
    }

    try {
        Compress-Archive -Path (Join-Path $SourceDir '*') -DestinationPath $ZipPath -Force -ErrorAction Stop
        Write-Log "ZIP creato con Compress-Archive: $ZipPath"
        return
    } catch {
        Write-Log "Compress-Archive fallito, uso fallback .NET: $($_.Exception.Message)" 'WARN'
    }

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        [System.IO.Compression.ZipFile]::CreateFromDirectory($src, $zip, [System.IO.Compression.CompressionLevel]::Optimal, $false)
        Write-Log "ZIP creato con .NET ZipFile: $ZipPath"
    } catch {
        Write-Log "Creazione ZIP fallita anche con .NET: $($_.Exception.Message)" 'ERROR'
        throw
    }
}

# ---------------------------------
# Validazione contenuti ZIP
# ---------------------------------
function Test-ZipContents {
    param(
        [Parameter(Mandatory)][string]  $ZipPath,
        [Parameter(Mandatory)][string[]]$ExpectedRelativeFiles
    )

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        $expected = @($ExpectedRelativeFiles) |
            Where-Object { $_ -ne $null -and $_.ToString().Trim() -ne '' } |
            ForEach-Object { ($_ -replace '\\','/').TrimStart('/') }

        $fs = [System.IO.File]::Open($ZipPath,
                                     [System.IO.FileMode]::Open,
                                     [System.IO.FileAccess]::Read,
                                     [System.IO.FileShare]::Read)
        try {
            $za = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Read, $false)
            $actual = @(
                $za.Entries |
                Where-Object { $_.FullName -and ($_.FullName -notmatch '/$') } |
                ForEach-Object { ($_.FullName -replace '\\','/').TrimStart('/') }
            )
        }
        finally {
            if ($fs) { $fs.Dispose() }
        }

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
    }
    catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
} | ForEach-Object { $_.FullName.TrimStart('.','/','\') }
            $expected = $ExpectedRelativeFiles | ForEach-Object { $_.Replace('\','/').TrimStart('/') }
            $actual   = $entries | ForEach-Object { $_.Replace('\','/').TrimStart('/') }

            $missing = $expected | Where-Object { $_ -notin $actual }
            $extra   = $actual   | Where-Object { $_ -notin $expected }

            if ($missing.Count -eq 0 -and $extra.Count -eq 0) {
                Write-Log "Validazione ZIP OK: contenuti attesi presenti"
                return $true
            } else {
                if ($missing.Count -gt 0) { Write-Log "File mancanti nello ZIP: $($missing -join ', ')" 'ERROR' }
                if ($extra.Count -gt 0)   { Write-Log "File extra nello ZIP: $($extra -join ', ')"   'WARN'  }
                return $false
            }
        } finally {
            $fs.Dispose()
        }
    } catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
}

# ---------------------------------
# MAIN
# ---------------------------------
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
  <style> body{font-family:system-ui,Segoe UI,Arial;margin:32px} .card{border:1px solid #ddd;padding:16px;border-radius:12px;max-width:900px} .grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))} .badge{display:inline-block;background:#eee;padding:4px 10px;border-radius:999px;margin-right:6px} a.button{display:inline-block;margin-top:12px;border:1px solid #888;padding:8px 12px;border-radius:8px;text-decoration:none} </style>
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

1. Copia l’intera cartella `TPI_evoluto_portabile` in un percorso sicuro
   (es. C:\ oppure su una chiavetta USB).

2. Per avviare la dashboard offline:
   - Doppio clic su `START TPI.cmd`
   - Si aprirà il browser con la dashboard TPI (non serve Python, né Internet).

3. Requisiti:
   - Windows 10 o 11
   - Nessuna installazione aggiuntiva richiesta
   - Modalità **read-only**: non scrive nulla su disco

4. In caso di problemi, apri `index.html` direttamente con il browser (Edge/Chrome/Firefox).
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PRE.txt') -Content $ReadmePre

    $ReadmeProgetto = @'
# TPI_evoluto - Progetto ufficiale

Questa versione portabile contiene la dashboard base (HTML + script) in sola lettura.

Per la versione **completa con FastAPI**, logging, internazionalizzazione (IT, EN, FR, DE), ruoli
(datore di lavoro, revisore, RSPP, lavoratore, supervisore) e dashboard interattiva,
visita il repository ufficiale:

👉 GitHub: https://github.com/aicreator76/TPI_evoluto

---

## Come contribuire
- Clona il repo:
  `git clone https://github.com/aicreator76/TPI_evoluto.git`
- Lavora sui branch:
  - `feature/logging-middleware`
  - `feature/i18n`
- Apri una Pull Request verso `main`.

---

## Contenuto pacchetto portabile
- `index.html` → Dashboard offline
- `START TPI.cmd` / `start.cmd` → Avvio rapido
- `README_PRE.txt` → Guida rapida
- `README_PROGETTO.txt` → Info progetto + link GitHub
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PROGETTO.txt') -Content $ReadmeProgetto

    # --- ZIP + REPORT ---
    $ZIP = Join-Path $TARGET_ROOT 'TPI_evoluto_portabile.zip'
    New-ZipRobust -SourceDir $PKG_DIR -ZipPath $ZIP

    try {
        $sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $ZIP).Hash
        Write-Log "SHA256: $sha"
    } catch {
        Write-Log "Impossibile calcolare SHA256: $($_.Exception.Message)" 'ERROR'
        throw
    }

    $reportPath = Join-Path $TARGET_ROOT 'PACKAGE_REPORT.md'
    $report = @"
# PACKAGE REPORT

- Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Destinazione: $TARGET_ROOT
- Cartella: $PKG_DIR
- ZIP: $ZIP
- SHA256: $sha

## Metadati progetto
- Nome: TPI_evoluto
- Versione: 0.1.0-portable
- Autore: Team TPI
- GitHub: https://github.com/aicreator76/TPI_evoluto

## Verifiche
- [$([bool](Test-Path -LiteralPath $IndexFile) -as [int] -replace '^1$','x' -replace '^0$',' ')] index.html presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'start.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] start.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'START TPI.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] START TPI.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PRE.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PRE.txt presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PROGETTO.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PROGETTO.txt presente
- [x] Zip creato correttamente

## Istruzioni d’uso
- Copia `TPI_evoluto_portabile` o lo `ZIP` su destinazione finale
- Avvia `START TPI.cmd`
"@
    $report | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-Log "Generato report: $reportPath"

    # Validazione ZIP
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
.FullName -replace '\\','/').TrimStart('/') }
            )
        } finally { if ($fs) { $fs.Dispose() } }
        $missing = @($expected | Where-Object { # Build-Portable.ps1
# Requisiti: Windows PowerShell 5.1+ o PowerShell 7+. Nessun privilegio elevato richiesto.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ---------------------------------
# Logging
# ---------------------------------
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

# ---------------------------------
# Helper percorsi / compatibilità
# ---------------------------------
$IsWin = [System.Environment]::OSVersion.Platform -eq 'Win32NT'

function Add-LongPathPrefix {
    param([Parameter(Mandatory)][string]$Path)
    if ($IsWin) {
        if ($Path -like '\\?\*') { return $Path }
        $full = [System.IO.Path]::GetFullPath($Path)
        if ($full.StartsWith('\\')) { return "\\?\UNC\$($full.TrimStart('\'))" }
        return "\\?\$full"
    } else {
        return $Path
    }
}

function Test-Command { param([string]$Name) $null -ne (Get-Command $Name -ErrorAction SilentlyContinue) }

# ---------------------------------
# Destinazione: D:\ poi primo rimovibile, altrimenti corrente
# ---------------------------------
function Get-PortableTarget {
    try {
        if (Test-Path 'D:\') { return 'D:\' }

        try {
            $wmi = Get-CimInstance -Class Win32_LogicalDisk -Filter "DriveType=2" -ErrorAction Stop |
                   Sort-Object DeviceID | Select-Object -First 1
            if ($wmi -and (Test-Path ($wmi.DeviceID + '\'))) { return ($wmi.DeviceID + '\') }
        } catch {}

        if (Test-Command -Name Get-Volume) {
            $vol = Get-Volume | Where-Object DriveType -eq 'Removable' | Select-Object -First 1
            if ($vol) { return ($vol.DriveLetter + ':\') }
        }

        return (Get-Location).Path + '\'
    } catch {
        return (Get-Location).Path + '\'
    }
}

# ---------------------------------
# Creazione file solo se mancanti
# ---------------------------------
function Ensure-File {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Content,
        [ValidateSet('UTF8','ASCII')][string]$Encoding = 'UTF8'
    )
    try {
        if (-not (Test-Path -LiteralPath $Path)) {
            $dir = Split-Path -Parent $Path
            if (-not (Test-Path -LiteralPath $dir)) {
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

# ---------------------------------
# ZIP robusto con fallback .NET
# ---------------------------------
function New-ZipRobust {
    param(
        [Parameter(Mandatory)][string]$SourceDir,
        [Parameter(Mandatory)][string]$ZipPath
    )
    $src = Add-LongPathPrefix -Path $SourceDir
    $zip = Add-LongPathPrefix -Path $ZipPath

    if (Test-Path -LiteralPath $ZipPath) {
        try { Remove-Item -LiteralPath $ZipPath -Force -ErrorAction Stop }
        catch {
            Write-Log "Impossibile rimuovere ZIP esistente: $ZipPath. $($_.Exception.Message)" 'ERROR'
            throw
        }
    }

    try {
        Compress-Archive -Path (Join-Path $SourceDir '*') -DestinationPath $ZipPath -Force -ErrorAction Stop
        Write-Log "ZIP creato con Compress-Archive: $ZipPath"
        return
    } catch {
        Write-Log "Compress-Archive fallito, uso fallback .NET: $($_.Exception.Message)" 'WARN'
    }

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        [System.IO.Compression.ZipFile]::CreateFromDirectory($src, $zip, [System.IO.Compression.CompressionLevel]::Optimal, $false)
        Write-Log "ZIP creato con .NET ZipFile: $ZipPath"
    } catch {
        Write-Log "Creazione ZIP fallita anche con .NET: $($_.Exception.Message)" 'ERROR'
        throw
    }
}

# ---------------------------------
# Validazione contenuti ZIP
# ---------------------------------
function Test-ZipContents {
    param(
        [Parameter(Mandatory)][string]  $ZipPath,
        [Parameter(Mandatory)][string[]]$ExpectedRelativeFiles
    )

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        $expected = @($ExpectedRelativeFiles) |
            Where-Object { $_ -ne $null -and $_.ToString().Trim() -ne '' } |
            ForEach-Object { ($_ -replace '\\','/').TrimStart('/') }

        $fs = [System.IO.File]::Open($ZipPath,
                                     [System.IO.FileMode]::Open,
                                     [System.IO.FileAccess]::Read,
                                     [System.IO.FileShare]::Read)
        try {
            $za = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Read, $false)
            $actual = @(
                $za.Entries |
                Where-Object { $_.FullName -and ($_.FullName -notmatch '/$') } |
                ForEach-Object { ($_.FullName -replace '\\','/').TrimStart('/') }
            )
        }
        finally {
            if ($fs) { $fs.Dispose() }
        }

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
    }
    catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
} | ForEach-Object { $_.FullName.TrimStart('.','/','\') }
            $expected = $ExpectedRelativeFiles | ForEach-Object { $_.Replace('\','/').TrimStart('/') }
            $actual   = $entries | ForEach-Object { $_.Replace('\','/').TrimStart('/') }

            $missing = $expected | Where-Object { $_ -notin $actual }
            $extra   = $actual   | Where-Object { $_ -notin $expected }

            if ($missing.Count -eq 0 -and $extra.Count -eq 0) {
                Write-Log "Validazione ZIP OK: contenuti attesi presenti"
                return $true
            } else {
                if ($missing.Count -gt 0) { Write-Log "File mancanti nello ZIP: $($missing -join ', ')" 'ERROR' }
                if ($extra.Count -gt 0)   { Write-Log "File extra nello ZIP: $($extra -join ', ')"   'WARN'  }
                return $false
            }
        } finally {
            $fs.Dispose()
        }
    } catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
}

# ---------------------------------
# MAIN
# ---------------------------------
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
  <style> body{font-family:system-ui,Segoe UI,Arial;margin:32px} .card{border:1px solid #ddd;padding:16px;border-radius:12px;max-width:900px} .grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))} .badge{display:inline-block;background:#eee;padding:4px 10px;border-radius:999px;margin-right:6px} a.button{display:inline-block;margin-top:12px;border:1px solid #888;padding:8px 12px;border-radius:8px;text-decoration:none} </style>
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

1. Copia l’intera cartella `TPI_evoluto_portabile` in un percorso sicuro
   (es. C:\ oppure su una chiavetta USB).

2. Per avviare la dashboard offline:
   - Doppio clic su `START TPI.cmd`
   - Si aprirà il browser con la dashboard TPI (non serve Python, né Internet).

3. Requisiti:
   - Windows 10 o 11
   - Nessuna installazione aggiuntiva richiesta
   - Modalità **read-only**: non scrive nulla su disco

4. In caso di problemi, apri `index.html` direttamente con il browser (Edge/Chrome/Firefox).
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PRE.txt') -Content $ReadmePre

    $ReadmeProgetto = @'
# TPI_evoluto - Progetto ufficiale

Questa versione portabile contiene la dashboard base (HTML + script) in sola lettura.

Per la versione **completa con FastAPI**, logging, internazionalizzazione (IT, EN, FR, DE), ruoli
(datore di lavoro, revisore, RSPP, lavoratore, supervisore) e dashboard interattiva,
visita il repository ufficiale:

👉 GitHub: https://github.com/aicreator76/TPI_evoluto

---

## Come contribuire
- Clona il repo:
  `git clone https://github.com/aicreator76/TPI_evoluto.git`
- Lavora sui branch:
  - `feature/logging-middleware`
  - `feature/i18n`
- Apri una Pull Request verso `main`.

---

## Contenuto pacchetto portabile
- `index.html` → Dashboard offline
- `START TPI.cmd` / `start.cmd` → Avvio rapido
- `README_PRE.txt` → Guida rapida
- `README_PROGETTO.txt` → Info progetto + link GitHub
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PROGETTO.txt') -Content $ReadmeProgetto

    # --- ZIP + REPORT ---
    $ZIP = Join-Path $TARGET_ROOT 'TPI_evoluto_portabile.zip'
    New-ZipRobust -SourceDir $PKG_DIR -ZipPath $ZIP

    try {
        $sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $ZIP).Hash
        Write-Log "SHA256: $sha"
    } catch {
        Write-Log "Impossibile calcolare SHA256: $($_.Exception.Message)" 'ERROR'
        throw
    }

    $reportPath = Join-Path $TARGET_ROOT 'PACKAGE_REPORT.md'
    $report = @"
# PACKAGE REPORT

- Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Destinazione: $TARGET_ROOT
- Cartella: $PKG_DIR
- ZIP: $ZIP
- SHA256: $sha

## Metadati progetto
- Nome: TPI_evoluto
- Versione: 0.1.0-portable
- Autore: Team TPI
- GitHub: https://github.com/aicreator76/TPI_evoluto

## Verifiche
- [$([bool](Test-Path -LiteralPath $IndexFile) -as [int] -replace '^1$','x' -replace '^0$',' ')] index.html presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'start.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] start.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'START TPI.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] START TPI.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PRE.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PRE.txt presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PROGETTO.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PROGETTO.txt presente
- [x] Zip creato correttamente

## Istruzioni d’uso
- Copia `TPI_evoluto_portabile` o lo `ZIP` su destinazione finale
- Avvia `START TPI.cmd`
"@
    $report | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-Log "Generato report: $reportPath"

    # Validazione ZIP
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
 -notin $actual })
        $extra   = @($actual   | Where-Object { # Build-Portable.ps1
# Requisiti: Windows PowerShell 5.1+ o PowerShell 7+. Nessun privilegio elevato richiesto.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ---------------------------------
# Logging
# ---------------------------------
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

# ---------------------------------
# Helper percorsi / compatibilità
# ---------------------------------
$IsWin = [System.Environment]::OSVersion.Platform -eq 'Win32NT'

function Add-LongPathPrefix {
    param([Parameter(Mandatory)][string]$Path)
    if ($IsWin) {
        if ($Path -like '\\?\*') { return $Path }
        $full = [System.IO.Path]::GetFullPath($Path)
        if ($full.StartsWith('\\')) { return "\\?\UNC\$($full.TrimStart('\'))" }
        return "\\?\$full"
    } else {
        return $Path
    }
}

function Test-Command { param([string]$Name) $null -ne (Get-Command $Name -ErrorAction SilentlyContinue) }

# ---------------------------------
# Destinazione: D:\ poi primo rimovibile, altrimenti corrente
# ---------------------------------
function Get-PortableTarget {
    try {
        if (Test-Path 'D:\') { return 'D:\' }

        try {
            $wmi = Get-CimInstance -Class Win32_LogicalDisk -Filter "DriveType=2" -ErrorAction Stop |
                   Sort-Object DeviceID | Select-Object -First 1
            if ($wmi -and (Test-Path ($wmi.DeviceID + '\'))) { return ($wmi.DeviceID + '\') }
        } catch {}

        if (Test-Command -Name Get-Volume) {
            $vol = Get-Volume | Where-Object DriveType -eq 'Removable' | Select-Object -First 1
            if ($vol) { return ($vol.DriveLetter + ':\') }
        }

        return (Get-Location).Path + '\'
    } catch {
        return (Get-Location).Path + '\'
    }
}

# ---------------------------------
# Creazione file solo se mancanti
# ---------------------------------
function Ensure-File {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Content,
        [ValidateSet('UTF8','ASCII')][string]$Encoding = 'UTF8'
    )
    try {
        if (-not (Test-Path -LiteralPath $Path)) {
            $dir = Split-Path -Parent $Path
            if (-not (Test-Path -LiteralPath $dir)) {
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

# ---------------------------------
# ZIP robusto con fallback .NET
# ---------------------------------
function New-ZipRobust {
    param(
        [Parameter(Mandatory)][string]$SourceDir,
        [Parameter(Mandatory)][string]$ZipPath
    )
    $src = Add-LongPathPrefix -Path $SourceDir
    $zip = Add-LongPathPrefix -Path $ZipPath

    if (Test-Path -LiteralPath $ZipPath) {
        try { Remove-Item -LiteralPath $ZipPath -Force -ErrorAction Stop }
        catch {
            Write-Log "Impossibile rimuovere ZIP esistente: $ZipPath. $($_.Exception.Message)" 'ERROR'
            throw
        }
    }

    try {
        Compress-Archive -Path (Join-Path $SourceDir '*') -DestinationPath $ZipPath -Force -ErrorAction Stop
        Write-Log "ZIP creato con Compress-Archive: $ZipPath"
        return
    } catch {
        Write-Log "Compress-Archive fallito, uso fallback .NET: $($_.Exception.Message)" 'WARN'
    }

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        [System.IO.Compression.ZipFile]::CreateFromDirectory($src, $zip, [System.IO.Compression.CompressionLevel]::Optimal, $false)
        Write-Log "ZIP creato con .NET ZipFile: $ZipPath"
    } catch {
        Write-Log "Creazione ZIP fallita anche con .NET: $($_.Exception.Message)" 'ERROR'
        throw
    }
}

# ---------------------------------
# Validazione contenuti ZIP
# ---------------------------------
function Test-ZipContents {
    param(
        [Parameter(Mandatory)][string]  $ZipPath,
        [Parameter(Mandatory)][string[]]$ExpectedRelativeFiles
    )

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        $expected = @($ExpectedRelativeFiles) |
            Where-Object { $_ -ne $null -and $_.ToString().Trim() -ne '' } |
            ForEach-Object { ($_ -replace '\\','/').TrimStart('/') }

        $fs = [System.IO.File]::Open($ZipPath,
                                     [System.IO.FileMode]::Open,
                                     [System.IO.FileAccess]::Read,
                                     [System.IO.FileShare]::Read)
        try {
            $za = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Read, $false)
            $actual = @(
                $za.Entries |
                Where-Object { $_.FullName -and ($_.FullName -notmatch '/$') } |
                ForEach-Object { ($_.FullName -replace '\\','/').TrimStart('/') }
            )
        }
        finally {
            if ($fs) { $fs.Dispose() }
        }

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
    }
    catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
} | ForEach-Object { $_.FullName.TrimStart('.','/','\') }
            $expected = $ExpectedRelativeFiles | ForEach-Object { $_.Replace('\','/').TrimStart('/') }
            $actual   = $entries | ForEach-Object { $_.Replace('\','/').TrimStart('/') }

            $missing = $expected | Where-Object { $_ -notin $actual }
            $extra   = $actual   | Where-Object { $_ -notin $expected }

            if ($missing.Count -eq 0 -and $extra.Count -eq 0) {
                Write-Log "Validazione ZIP OK: contenuti attesi presenti"
                return $true
            } else {
                if ($missing.Count -gt 0) { Write-Log "File mancanti nello ZIP: $($missing -join ', ')" 'ERROR' }
                if ($extra.Count -gt 0)   { Write-Log "File extra nello ZIP: $($extra -join ', ')"   'WARN'  }
                return $false
            }
        } finally {
            $fs.Dispose()
        }
    } catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
}

# ---------------------------------
# MAIN
# ---------------------------------
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
  <style> body{font-family:system-ui,Segoe UI,Arial;margin:32px} .card{border:1px solid #ddd;padding:16px;border-radius:12px;max-width:900px} .grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))} .badge{display:inline-block;background:#eee;padding:4px 10px;border-radius:999px;margin-right:6px} a.button{display:inline-block;margin-top:12px;border:1px solid #888;padding:8px 12px;border-radius:8px;text-decoration:none} </style>
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

1. Copia l’intera cartella `TPI_evoluto_portabile` in un percorso sicuro
   (es. C:\ oppure su una chiavetta USB).

2. Per avviare la dashboard offline:
   - Doppio clic su `START TPI.cmd`
   - Si aprirà il browser con la dashboard TPI (non serve Python, né Internet).

3. Requisiti:
   - Windows 10 o 11
   - Nessuna installazione aggiuntiva richiesta
   - Modalità **read-only**: non scrive nulla su disco

4. In caso di problemi, apri `index.html` direttamente con il browser (Edge/Chrome/Firefox).
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PRE.txt') -Content $ReadmePre

    $ReadmeProgetto = @'
# TPI_evoluto - Progetto ufficiale

Questa versione portabile contiene la dashboard base (HTML + script) in sola lettura.

Per la versione **completa con FastAPI**, logging, internazionalizzazione (IT, EN, FR, DE), ruoli
(datore di lavoro, revisore, RSPP, lavoratore, supervisore) e dashboard interattiva,
visita il repository ufficiale:

👉 GitHub: https://github.com/aicreator76/TPI_evoluto

---

## Come contribuire
- Clona il repo:
  `git clone https://github.com/aicreator76/TPI_evoluto.git`
- Lavora sui branch:
  - `feature/logging-middleware`
  - `feature/i18n`
- Apri una Pull Request verso `main`.

---

## Contenuto pacchetto portabile
- `index.html` → Dashboard offline
- `START TPI.cmd` / `start.cmd` → Avvio rapido
- `README_PRE.txt` → Guida rapida
- `README_PROGETTO.txt` → Info progetto + link GitHub
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PROGETTO.txt') -Content $ReadmeProgetto

    # --- ZIP + REPORT ---
    $ZIP = Join-Path $TARGET_ROOT 'TPI_evoluto_portabile.zip'
    New-ZipRobust -SourceDir $PKG_DIR -ZipPath $ZIP

    try {
        $sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $ZIP).Hash
        Write-Log "SHA256: $sha"
    } catch {
        Write-Log "Impossibile calcolare SHA256: $($_.Exception.Message)" 'ERROR'
        throw
    }

    $reportPath = Join-Path $TARGET_ROOT 'PACKAGE_REPORT.md'
    $report = @"
# PACKAGE REPORT

- Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Destinazione: $TARGET_ROOT
- Cartella: $PKG_DIR
- ZIP: $ZIP
- SHA256: $sha

## Metadati progetto
- Nome: TPI_evoluto
- Versione: 0.1.0-portable
- Autore: Team TPI
- GitHub: https://github.com/aicreator76/TPI_evoluto

## Verifiche
- [$([bool](Test-Path -LiteralPath $IndexFile) -as [int] -replace '^1$','x' -replace '^0$',' ')] index.html presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'start.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] start.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'START TPI.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] START TPI.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PRE.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PRE.txt presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PROGETTO.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PROGETTO.txt presente
- [x] Zip creato correttamente

## Istruzioni d’uso
- Copia `TPI_evoluto_portabile` o lo `ZIP` su destinazione finale
- Avvia `START TPI.cmd`
"@
    $report | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-Log "Generato report: $reportPath"

    # Validazione ZIP
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
 -notin $expected })
        if ($missing.Count -eq 0 -and $extra.Count -eq 0) {
            Write-Log "Validazione ZIP OK: contenuti attesi presenti"
            return $true
        } else {
            if ($missing.Count -gt 0) { Write-Log "File mancanti nello ZIP: $($missing -join ', ')" 'ERROR' }
            if ($extra.Count   -gt 0) { Write-Log "File extra nello ZIP: $($extra   -join ', ')" 'WARN'  }
            return $false
        }
    } catch {
        Write-Log "Errore nella validazione ZIP: $(# Build-Portable.ps1
# Requisiti: Windows PowerShell 5.1+ o PowerShell 7+. Nessun privilegio elevato richiesto.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ---------------------------------
# Logging
# ---------------------------------
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

# ---------------------------------
# Helper percorsi / compatibilità
# ---------------------------------
$IsWin = [System.Environment]::OSVersion.Platform -eq 'Win32NT'

function Add-LongPathPrefix {
    param([Parameter(Mandatory)][string]$Path)
    if ($IsWin) {
        if ($Path -like '\\?\*') { return $Path }
        $full = [System.IO.Path]::GetFullPath($Path)
        if ($full.StartsWith('\\')) { return "\\?\UNC\$($full.TrimStart('\'))" }
        return "\\?\$full"
    } else {
        return $Path
    }
}

function Test-Command { param([string]$Name) $null -ne (Get-Command $Name -ErrorAction SilentlyContinue) }

# ---------------------------------
# Destinazione: D:\ poi primo rimovibile, altrimenti corrente
# ---------------------------------
function Get-PortableTarget {
    try {
        if (Test-Path 'D:\') { return 'D:\' }

        try {
            $wmi = Get-CimInstance -Class Win32_LogicalDisk -Filter "DriveType=2" -ErrorAction Stop |
                   Sort-Object DeviceID | Select-Object -First 1
            if ($wmi -and (Test-Path ($wmi.DeviceID + '\'))) { return ($wmi.DeviceID + '\') }
        } catch {}

        if (Test-Command -Name Get-Volume) {
            $vol = Get-Volume | Where-Object DriveType -eq 'Removable' | Select-Object -First 1
            if ($vol) { return ($vol.DriveLetter + ':\') }
        }

        return (Get-Location).Path + '\'
    } catch {
        return (Get-Location).Path + '\'
    }
}

# ---------------------------------
# Creazione file solo se mancanti
# ---------------------------------
function Ensure-File {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Content,
        [ValidateSet('UTF8','ASCII')][string]$Encoding = 'UTF8'
    )
    try {
        if (-not (Test-Path -LiteralPath $Path)) {
            $dir = Split-Path -Parent $Path
            if (-not (Test-Path -LiteralPath $dir)) {
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

# ---------------------------------
# ZIP robusto con fallback .NET
# ---------------------------------
function New-ZipRobust {
    param(
        [Parameter(Mandatory)][string]$SourceDir,
        [Parameter(Mandatory)][string]$ZipPath
    )
    $src = Add-LongPathPrefix -Path $SourceDir
    $zip = Add-LongPathPrefix -Path $ZipPath

    if (Test-Path -LiteralPath $ZipPath) {
        try { Remove-Item -LiteralPath $ZipPath -Force -ErrorAction Stop }
        catch {
            Write-Log "Impossibile rimuovere ZIP esistente: $ZipPath. $($_.Exception.Message)" 'ERROR'
            throw
        }
    }

    try {
        Compress-Archive -Path (Join-Path $SourceDir '*') -DestinationPath $ZipPath -Force -ErrorAction Stop
        Write-Log "ZIP creato con Compress-Archive: $ZipPath"
        return
    } catch {
        Write-Log "Compress-Archive fallito, uso fallback .NET: $($_.Exception.Message)" 'WARN'
    }

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        [System.IO.Compression.ZipFile]::CreateFromDirectory($src, $zip, [System.IO.Compression.CompressionLevel]::Optimal, $false)
        Write-Log "ZIP creato con .NET ZipFile: $ZipPath"
    } catch {
        Write-Log "Creazione ZIP fallita anche con .NET: $($_.Exception.Message)" 'ERROR'
        throw
    }
}

# ---------------------------------
# Validazione contenuti ZIP
# ---------------------------------
function Test-ZipContents {
    param(
        [Parameter(Mandatory)][string]  $ZipPath,
        [Parameter(Mandatory)][string[]]$ExpectedRelativeFiles
    )

    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        $expected = @($ExpectedRelativeFiles) |
            Where-Object { $_ -ne $null -and $_.ToString().Trim() -ne '' } |
            ForEach-Object { ($_ -replace '\\','/').TrimStart('/') }

        $fs = [System.IO.File]::Open($ZipPath,
                                     [System.IO.FileMode]::Open,
                                     [System.IO.FileAccess]::Read,
                                     [System.IO.FileShare]::Read)
        try {
            $za = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Read, $false)
            $actual = @(
                $za.Entries |
                Where-Object { $_.FullName -and ($_.FullName -notmatch '/$') } |
                ForEach-Object { ($_.FullName -replace '\\','/').TrimStart('/') }
            )
        }
        finally {
            if ($fs) { $fs.Dispose() }
        }

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
    }
    catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
} | ForEach-Object { $_.FullName.TrimStart('.','/','\') }
            $expected = $ExpectedRelativeFiles | ForEach-Object { $_.Replace('\','/').TrimStart('/') }
            $actual   = $entries | ForEach-Object { $_.Replace('\','/').TrimStart('/') }

            $missing = $expected | Where-Object { $_ -notin $actual }
            $extra   = $actual   | Where-Object { $_ -notin $expected }

            if ($missing.Count -eq 0 -and $extra.Count -eq 0) {
                Write-Log "Validazione ZIP OK: contenuti attesi presenti"
                return $true
            } else {
                if ($missing.Count -gt 0) { Write-Log "File mancanti nello ZIP: $($missing -join ', ')" 'ERROR' }
                if ($extra.Count -gt 0)   { Write-Log "File extra nello ZIP: $($extra -join ', ')"   'WARN'  }
                return $false
            }
        } finally {
            $fs.Dispose()
        }
    } catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
}

# ---------------------------------
# MAIN
# ---------------------------------
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
  <style> body{font-family:system-ui,Segoe UI,Arial;margin:32px} .card{border:1px solid #ddd;padding:16px;border-radius:12px;max-width:900px} .grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))} .badge{display:inline-block;background:#eee;padding:4px 10px;border-radius:999px;margin-right:6px} a.button{display:inline-block;margin-top:12px;border:1px solid #888;padding:8px 12px;border-radius:8px;text-decoration:none} </style>
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

1. Copia l’intera cartella `TPI_evoluto_portabile` in un percorso sicuro
   (es. C:\ oppure su una chiavetta USB).

2. Per avviare la dashboard offline:
   - Doppio clic su `START TPI.cmd`
   - Si aprirà il browser con la dashboard TPI (non serve Python, né Internet).

3. Requisiti:
   - Windows 10 o 11
   - Nessuna installazione aggiuntiva richiesta
   - Modalità **read-only**: non scrive nulla su disco

4. In caso di problemi, apri `index.html` direttamente con il browser (Edge/Chrome/Firefox).
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PRE.txt') -Content $ReadmePre

    $ReadmeProgetto = @'
# TPI_evoluto - Progetto ufficiale

Questa versione portabile contiene la dashboard base (HTML + script) in sola lettura.

Per la versione **completa con FastAPI**, logging, internazionalizzazione (IT, EN, FR, DE), ruoli
(datore di lavoro, revisore, RSPP, lavoratore, supervisore) e dashboard interattiva,
visita il repository ufficiale:

👉 GitHub: https://github.com/aicreator76/TPI_evoluto

---

## Come contribuire
- Clona il repo:
  `git clone https://github.com/aicreator76/TPI_evoluto.git`
- Lavora sui branch:
  - `feature/logging-middleware`
  - `feature/i18n`
- Apri una Pull Request verso `main`.

---

## Contenuto pacchetto portabile
- `index.html` → Dashboard offline
- `START TPI.cmd` / `start.cmd` → Avvio rapido
- `README_PRE.txt` → Guida rapida
- `README_PROGETTO.txt` → Info progetto + link GitHub
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PROGETTO.txt') -Content $ReadmeProgetto

    # --- ZIP + REPORT ---
    $ZIP = Join-Path $TARGET_ROOT 'TPI_evoluto_portabile.zip'
    New-ZipRobust -SourceDir $PKG_DIR -ZipPath $ZIP

    try {
        $sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $ZIP).Hash
        Write-Log "SHA256: $sha"
    } catch {
        Write-Log "Impossibile calcolare SHA256: $($_.Exception.Message)" 'ERROR'
        throw
    }

    $reportPath = Join-Path $TARGET_ROOT 'PACKAGE_REPORT.md'
    $report = @"
# PACKAGE REPORT

- Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Destinazione: $TARGET_ROOT
- Cartella: $PKG_DIR
- ZIP: $ZIP
- SHA256: $sha

## Metadati progetto
- Nome: TPI_evoluto
- Versione: 0.1.0-portable
- Autore: Team TPI
- GitHub: https://github.com/aicreator76/TPI_evoluto

## Verifiche
- [$([bool](Test-Path -LiteralPath $IndexFile) -as [int] -replace '^1$','x' -replace '^0$',' ')] index.html presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'start.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] start.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'START TPI.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] START TPI.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PRE.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PRE.txt presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PROGETTO.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PROGETTO.txt presente
- [x] Zip creato correttamente

## Istruzioni d’uso
- Copia `TPI_evoluto_portabile` o lo `ZIP` su destinazione finale
- Avvia `START TPI.cmd`
"@
    $report | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-Log "Generato report: $reportPath"

    # Validazione ZIP
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
.Exception.Message)" 'ERROR'
        return $false
    }
} | ForEach-Object { $_.FullName.TrimStart('.','/','\') }
            $expected = $ExpectedRelativeFiles | ForEach-Object { $_.Replace('\','/').TrimStart('/') }
            $actual   = $entries | ForEach-Object { $_.Replace('\','/').TrimStart('/') }

            $missing = $expected | Where-Object { $_ -notin $actual }
            $extra   = $actual   | Where-Object { $_ -notin $expected }

            if ($missing.Count -eq 0 -and $extra.Count -eq 0) {
                Write-Log "Validazione ZIP OK: contenuti attesi presenti"
                return $true
            } else {
                if ($missing.Count -gt 0) { Write-Log "File mancanti nello ZIP: $($missing -join ', ')" 'ERROR' }
                if ($extra.Count -gt 0)   { Write-Log "File extra nello ZIP: $($extra -join ', ')"   'WARN'  }
                return $false
            }
        } finally {
            $fs.Dispose()
        }
    } catch {
        Write-Log "Errore nella validazione ZIP: $($_.Exception.Message)" 'ERROR'
        return $false
    }
}

# ---------------------------------
# MAIN
# ---------------------------------
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
  <style> body{font-family:system-ui,Segoe UI,Arial;margin:32px} .card{border:1px solid #ddd;padding:16px;border-radius:12px;max-width:900px} .grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))} .badge{display:inline-block;background:#eee;padding:4px 10px;border-radius:999px;margin-right:6px} a.button{display:inline-block;margin-top:12px;border:1px solid #888;padding:8px 12px;border-radius:8px;text-decoration:none} </style>
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

1. Copia l’intera cartella `TPI_evoluto_portabile` in un percorso sicuro
   (es. C:\ oppure su una chiavetta USB).

2. Per avviare la dashboard offline:
   - Doppio clic su `START TPI.cmd`
   - Si aprirà il browser con la dashboard TPI (non serve Python, né Internet).

3. Requisiti:
   - Windows 10 o 11
   - Nessuna installazione aggiuntiva richiesta
   - Modalità **read-only**: non scrive nulla su disco

4. In caso di problemi, apri `index.html` direttamente con il browser (Edge/Chrome/Firefox).
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PRE.txt') -Content $ReadmePre

    $ReadmeProgetto = @'
# TPI_evoluto - Progetto ufficiale

Questa versione portabile contiene la dashboard base (HTML + script) in sola lettura.

Per la versione **completa con FastAPI**, logging, internazionalizzazione (IT, EN, FR, DE), ruoli
(datore di lavoro, revisore, RSPP, lavoratore, supervisore) e dashboard interattiva,
visita il repository ufficiale:

👉 GitHub: https://github.com/aicreator76/TPI_evoluto

---

## Come contribuire
- Clona il repo:
  `git clone https://github.com/aicreator76/TPI_evoluto.git`
- Lavora sui branch:
  - `feature/logging-middleware`
  - `feature/i18n`
- Apri una Pull Request verso `main`.

---

## Contenuto pacchetto portabile
- `index.html` → Dashboard offline
- `START TPI.cmd` / `start.cmd` → Avvio rapido
- `README_PRE.txt` → Guida rapida
- `README_PROGETTO.txt` → Info progetto + link GitHub
'@
    Ensure-File -Path (Join-Path $PKG_DIR 'README_PROGETTO.txt') -Content $ReadmeProgetto

    # --- ZIP + REPORT ---
    $ZIP = Join-Path $TARGET_ROOT 'TPI_evoluto_portabile.zip'
    New-ZipRobust -SourceDir $PKG_DIR -ZipPath $ZIP

    try {
        $sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $ZIP).Hash
        Write-Log "SHA256: $sha"
    } catch {
        Write-Log "Impossibile calcolare SHA256: $($_.Exception.Message)" 'ERROR'
        throw
    }

    $reportPath = Join-Path $TARGET_ROOT 'PACKAGE_REPORT.md'
    $report = @"
# PACKAGE REPORT

- Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Destinazione: $TARGET_ROOT
- Cartella: $PKG_DIR
- ZIP: $ZIP
- SHA256: $sha

## Metadati progetto
- Nome: TPI_evoluto
- Versione: 0.1.0-portable
- Autore: Team TPI
- GitHub: https://github.com/aicreator76/TPI_evoluto

## Verifiche
- [$([bool](Test-Path -LiteralPath $IndexFile) -as [int] -replace '^1$','x' -replace '^0$',' ')] index.html presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'start.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] start.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'START TPI.cmd')) -as [int] -replace '^1$','x' -replace '^0$',' ')] START TPI.cmd presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PRE.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PRE.txt presente
- [$([bool](Test-Path -LiteralPath (Join-Path $PKG_DIR 'README_PROGETTO.txt')) -as [int] -replace '^1$','x' -replace '^0$',' ')] README_PROGETTO.txt presente
- [x] Zip creato correttamente

## Istruzioni d’uso
- Copia `TPI_evoluto_portabile` o lo `ZIP` su destinazione finale
- Avvia `START TPI.cmd`
"@
    $report | Set-Content -LiteralPath $reportPath -Encoding UTF8
    Write-Log "Generato report: $reportPath"

    # Validazione ZIP
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


