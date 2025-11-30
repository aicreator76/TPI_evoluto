<#
  CESARE_stato_regno.ps1
  Riepilogo rapido dello stato del Regno TPI_evoluto:
  - Git: ultimo tag, ultimo commit, stato working tree
  - Issue per milestone M1/M2/M3
  - Servizi locali: FastAPI (uvicorn), n8n
#>

[CmdletBinding()]
param()

$OpsDir   = $PSScriptRoot
if (-not $OpsDir) {
    # fallback nel caso PSScriptRoot non sia valorizzato
    $OpsDir = Split-Path -Parent $MyInvocation.MyCommand.Path
}
$RepoRoot = Split-Path $OpsDir -Parent

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host ("==== {0} ====" -f $Title) -ForegroundColor Yellow
}

Write-Host "STATO-REGNO - panoramica rapida" -ForegroundColor Cyan
Write-Host ("Root repo: {0}" -f $RepoRoot)
Write-Host ""

# =========================
# Git / Snapshot
# =========================
Write-Section "Git / Snapshot"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "git non trovato nel PATH. Salto sezione Git." -ForegroundColor DarkYellow
} else {
    $oldLocation = Get-Location
    try {
        Set-Location $RepoRoot

        $lastTag = git describe --tags --abbrev=0 2>$null
        if (-not $lastTag) { $lastTag = "(nessun tag trovato)" }
        Write-Host ("Ultimo tag:    {0}" -f $lastTag)

        $lastCommit = git log -1 --oneline 2>$null
        if ($lastCommit) {
            Write-Host ("Ultimo commit: {0}" -f $lastCommit)
        } else {
            Write-Host "Ultimo commit: (non disponibile)"
        }

        # Stato working tree (pulito / modifiche locali)
        $statusShort = git status --short 2>$null
        if ([string]::IsNullOrWhiteSpace($statusShort)) {
            Write-Host "Working tree:  pulito" -ForegroundColor Green
        } else {
            Write-Host "Working tree:  modifiche locali presenti:" -ForegroundColor DarkYellow
            $statusShort -split "`n" | ForEach-Object {
                if ($_ -ne "") { Write-Host ("  {0}" -f $_) }
            }
        }
    } finally {
        Set-Location $oldLocation
    }
}

# =========================
# Issue chiave M1/M2/M3 (via gh)
# =========================
Write-Section "Issue chiave (M1/M2/M3)"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "gh non trovato nel PATH. Salto riepilogo issue." -ForegroundColor DarkYellow
} else {
    $oldLocation = Get-Location
    try {
        Set-Location $RepoRoot

        $repoInfoJson = gh repo view --json nameWithOwner 2>$null
        if ($repoInfoJson) {
            $repoInfo = $repoInfoJson | ConvertFrom-Json
            $repo     = $repoInfo.nameWithOwner
            Write-Host ("Repo: {0}" -f $repo)

            $milestones = @("M1","M2","M3")
            foreach ($m in $milestones) {
                $issuesJson = gh issue list `
                    -R $repo `
                    --state open `
                    --search $m `
                    --limit 50 `
                    --json number,title,state 2>$null

                if ($issuesJson) {
                    $issues = $issuesJson | ConvertFrom-Json

                    # normalizza ad array
                    if ($null -eq $issues) {
                        $issuesArray = @()
                    } elseif ($issues -is [System.Array]) {
                        $issuesArray = $issues
                    } else {
                        $issuesArray = @($issues)
                    }

                    $count = $issuesArray.Count
                    Write-Host (" {0}: {1} issue aperte" -f $m, $count)

                    # Mostra le prime 3 issue come anteprima
                    $top = $issuesArray | Select-Object -First 3
                    foreach ($i in $top) {
                        Write-Host ("   # {0} - {1}" -f $i.number, $i.title)
                    }
                } else {
                    Write-Host (" {0}: nessuna issue trovata o errore gh." -f $m)
                }
            }
        } else {
            Write-Host "Impossibile leggere informazioni repo da gh." -ForegroundColor DarkYellow
        }
    } finally {
        Set-Location $oldLocation
    }
}

# =========================
# Servizi locali (processi)
# =========================
Write-Section "Servizi locali"

function Show-ServiceStatus {
    param(
        [string]$Name,
        [string]$Friendly
    )

    $proc = Get-Process -Name $Name -ErrorAction SilentlyContinue
    if ($proc) {
        $pids = ($proc | Select-Object -ExpandProperty Id) -join ","
        Write-Host (" {0}: ATTIVO (PID {1})" -f $Friendly, $pids) -ForegroundColor Green
    } else {
        Write-Host (" {0}: NON in esecuzione" -f $Friendly) -ForegroundColor Red
    }
}

# Nota: se uvicorn gira come python.exe, qui potresti dover adattare a Name "python"
Show-ServiceStatus -Name "uvicorn" -Friendly "FastAPI / uvicorn"
Show-ServiceStatus -Name "n8n"     -Friendly "n8n orchestratore"

Write-Host ""
Write-Host "Fine STATO-REGNO." -ForegroundColor Cyan
