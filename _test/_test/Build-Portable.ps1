# Build-Portable.ps1
# Requisiti: Windows PowerShell 5.1+ o PowerShell 7+, nessun privilegio elevato richiesto.
# Uso: powershell -ExecutionPolicy Bypass -File .\Build-Portable.ps1
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ---------------------------
# Utility di logging
# ---------------------------
$Script:LogFile = Join-Path (Get-Location) 'Build-Portable.log'
function Write-Log {
    param(
        [Parameter(Mandatory)] [string] $Message,
        [ValidateSet('INFO','WARN','ERROR')] [string] $Level = 'INFO'
    )
    $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "$ts [$Level] $Message"
    Write-Host $line
    try { Add-Content -LiteralPath $Script:LogFile -Value $line } catch {}
}

# ---------------------------
# Helper percorsi/compatibilità
# ---------------------------
# Rilevamento Windows anche su PowerShell 5.1
$Script:IsWindows = ($PSVersionTable.PSEdition -eq 'Desktop') -or ($env:OS -eq 'Windows_NT')

function Add-LongPathPrefix {
    param([Parameter(Mandatory)][string]$Path)
    if ($Script:IsWindows) {
        if ($Path -like '\\?\*') { return $Path }
        $full = [System.IO.Path]::GetFullPath($Path)
        if ($full.StartsWith('\\')) { return "\\?\UNC\$($full.TrimStart('\'))" }
        return "\\?\$full"
    } else {
        return $Path
    }
}

function Test-Command {
    param([string]$Name)
    $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

# ---------------------------
# Individua destinazione: D:\, poi primo drive rimovibile, altrimenti corrente
# ---------------------------
function Get-PortableTarget {
    try {
        if (Test-Path 'D:\') { return 'D:\' }

        # Metodo 1: WMI/CIM (affidabile anche con permessi limitati)
        try {
            $wmi = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DriveType=2" -ErrorAction Stop |
                   Sort-Object DeviceID | Select-Object -First 1
            if ($wmi -and (Test-Path ($wmi.DeviceID + '\'))) { return ($wmi.DeviceID + '\') }
        } catch {}

        # Metodo 2: Get-Volume (se disponibile)
        if (Test-Command -Name Get-Volume) {
            $vol = Get-Volume | Where-Object DriveType -eq 'Removable' | Select-Object -First 1
            if ($vol) { return ($vol.DriveLetter + ':\') }
        }

        # Fallback: cartella corrente
        return (Get-Location).Path + '\'
    } catch {
        return (Get-Location).Path + '\'
    }
}

# ---------------------------
# Creazione file solo se mancanti
# ---------------------------
function Ensure-File {
    param(
        [Parameter(Mandatory)][string] $Path,
        [Parameter(Mandatory)][string] $Content,
        [ValidateSet('UTF8','ASCII')] [string] $Encoding = 'UTF8'
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

# ---------------------------
# ZIP robusto con fallback .NET
# ---------------------------
function New-ZipRobust {
    param(
        [Parameter(Mandatory)][string] $SourceDir,
        [Parameter(Mandatory)][string] $ZipPath
    )
    $src = Add-LongPathPrefix -Path $SourceDir
    $zip = Add-LongPathPrefix -Path $ZipPath

    if (Test-Path -LiteralPath $ZipPath) {
        try { Remove-Item -LiteralPath $ZipPath -Force -ErrorAction Stop } catch {
            Write-Log "Impossibile rimuovere ZIP esistente: $ZipPath. $($_.Exception.Message)" 'ERROR'
            throw
        }
    }

    # Tentativo 1: Compress-Archive
    try {
        Compress-Archive -Path (Join-Path $SourceDir '*') -DestinationPath $ZipPath -Force -ErrorAction Stop
        Write-Log "ZIP creato con Compress-Archive: $ZipPath"
        return
    } catch {
        Write-Log "Compress-Archive fallito, attivo fallback .NET: $($_.Exception.Message)" 'WARN'
    }

    # Tentativo 2: .NET ZipFile
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        [System.IO.Compression.ZipFile]::CreateFromDirectory($src, $zip, [System.IO.Compression.CompressionLevel]::Optimal, $false)
        Write-Log "ZIP creato con .NET ZipFile: $ZipPath"
    } catch {
        Write-Log "Creazione ZIP fallita anche con .NET: $($_.Exception.Message)" 'ERROR'
        throw
    }
}

# ---------------------------
# Validazione contenuti dello ZIP (esattamente i file previsti)
# ---------------------------
function Test-ZipContents {
    param(
        [Parameter(Mandatory)][string] $ZipPath,
        [Parameter(Mandatory)][string[]] $ExpectedRelativeFiles
    )
    try {
        Add-Type -AssemblyName System.IO.Compression.FileSystem -ErrorAction SilentlyContinue
        $zipAbs = Add-LongPathPrefix -Path $ZipPath
        $fs = [System.IO.File]::OpenRead($zipAbs)
        try {
            $za = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Read)
            $entries = $za.Entries | Where-Object { $_.FullName -notmatch '/$' } | ForEach-Object { $_.FullName.TrimStart('.','/','\') }
            $expected = $ExpectedRelativeFiles | ForEach-Object { $_.Replace('\','/').TrimStart('/') }
            $actual   = $entries | ForEach-Object { $_.Replace('\','/').TrimStart('/') }

            $missing = $expected | Where-Object { $_ -notin $actual }
            $extra   = $actual   | Where-Object { $_ -notin $expected }

            if ($missing.Count -eq 0 -and $extra.Count -eq 0) {
                Write-Lo
