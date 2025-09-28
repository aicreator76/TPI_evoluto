# FINAL_START_ALL.ps1
# Usa: Salva in C:\TPI_evoluto\FINAL_START_ALL.ps1
# Esegui (da normale PowerShell): 
# Start-Process powershell -Verb runAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File "C:\TPI_evoluto\FINAL_START_ALL.ps1"'

[CmdletBinding()]
param()

# ------------------ CONFIGURAZIONE ------------------
$RepoPath        = "C:\TPI_evoluto"
$BackupDest      = "D:\TPI_evoluto_backup"
$VenvActivate    = ".\.venv\Scripts\Activate.ps1"   # relativo a $RepoPath
$PythonExe       = ".\.venv\Scripts\python.exe"     # relativo a $RepoPath
$UvicornHost     = "127.0.0.1"
$UvicornPort     = 8000
$LogDirName      = "logs"
$LogFileName     = "tpi_server.log"
$DoInstallReqs   = $false    # se true esegue pip install -r requirements.txt
$DoGitPush       = $true     # se true tenta git add/commit/push (ti chiede conferma/mess)
$OpenBrowser     = $true     # apre browser a http://127.0.0.1:8000
$UvicornReload   = $true     # --reload flag
# ----------------------------------------------------

function Write-Info($m){ Write-Host $m -ForegroundColor Cyan }
function Write-OK($m){ Write-Host $m -ForegroundColor Green }
function Write-Warn($m){ Write-Host $m -ForegroundColor Yellow }
function Write-Err($m){ Write-Host $m -ForegroundColor Red }

# Elevazione: se non admin, rilancia come admin
function Ensure-Elevated {
    $id = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $p = New-Object System.Security.Principal.WindowsPrincipal($id)
    if (-not $p.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Warn "Non sei amministratore: rilancio lo script come Amministratore..."
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = "powershell"
        $escaped = $MyInvocation.MyCommand.Path -replace '"','`"'
        $psi.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$escaped`""
        $psi.Verb = "runas"
        try {
            [System.Diagnostics.Process]::Start($psi) | Out-Null
        } catch {
            Write-Err "Elevazione annullata o fallita. Esco."
        }
        exit
    } else {
        Write-OK "Eseguito con privilegi amministrativi."
    }
}

# Backup con robocopy
function Do-Backup {
    param($src, $dst)
    Write-Info "=== Eseguo backup da $src a $dst ==="
    if (-not (Test-Path $src)) { Write-Err "Origine non trovata: $src"; return }
    if (-not (Test-Path $dst)) { New-Item -ItemType Directory -Path $dst -Force | Out-Null ; Write-Info "Creato $dst" }
    $roboArgs = @("$src", $dst, "*.*", "/MIR", "/COPY:DAT", "/R:3", "/W:5", "/NFL","/NDL")
    $p = Start-Process -FilePath "robocopy" -ArgumentList $roboArgs -NoNewWindow -Wait -PassThru
    if ($p.ExitCode -le 3) {
        Write-OK "Backup completato (robocopy exit $($p.ExitCode))."
    } else {
        Write-Warn "robocopy exit code $($p.ExitCode) — verificare file mancanti o errori."
    }
}

# Attiva venv se esiste
function Activate-Venv {
    param($path)
    if (Test-Path $path) {
        Write-Info "Attivo virtualenv: $path"
        & powershell -NoProfile -ExecutionPolicy Bypass -Command ". `"$path`""  # attivazione in subshell
        # Nota: l'attivazione qui serve per comandi eseguiti visualmente. Usiamo python esplicito per Start-Process.
    } else {
        Write-Warn "Virtualenv non trovato in $path"
    }
}

# Installa requirements (opzionale)
function Install-Requirements {
    param($repoPath)
    $req = Join-Path $repoPath "requirements.txt"
    if (Test-Path $req) {
        Write-Info "Installazione dependencies da requirements.txt"
        & git -C $repoPath --version > $null 2>&1
        if (Test-Path (Join-Path $repoPath $PythonExe)) {
            & "$repoPath\$PythonExe" -m pip install -r $req
        } else {
            # fallback a python in PATH
            python -m pip install -r $req
        }
    } else {
        Write-Warn "requirements.txt non trovato in $repoPath"
    }
}

# Git workflow semplice: pull -> status -> add/commit/push (opzionale)
function Git-Flow {
    param($repoPath)
    if (-not (Test-Path (Join-Path $repoPath ".git"))) {
        Write-Warn "Cartella $repoPath non è un repo git (manca .git)."
        return
    }
    Push-Location $repoPath
    try {
        Write-Info "git fetch origin"
        & git fetch origin
        Write-Info "git status"
        & git status -s

        if ($DoGitPush) {
            $toCommit = & git status --porcelain
            if ($toCommit) {
                Write-Info "Ci sono modifiche locali. Mostro le modifiche brevi:"
                & git status -s
                $msg = Read-Host "Inserisci messaggio di commit (o INVIO per annullare il commit)"
                if ([string]::IsNullOrWhiteSpace($msg)) {
                    Write-Warn "Commit annullato dall'utente."
                } else {
                    & git add -A
                    & git commit -m $msg
                    Write-Info "Eseguo git pull --rebase"
                    & git pull --rebase origin HEAD
                    Write-Info "Eseguo git push"
                    & git push origin HEAD
                    Write-OK "Push completato."
                }
            } else {
                Write-Info "Nessuna modifica locale da committare."
            }
        } else {
            Write-Info "Skip git push (DoGitPush=false)."
        }
    } catch {
        Write-Err "Errore git: $($_.Exception.Message)"
    } finally {
        Pop-Location
    }
}

# Avvia uvicorn in finestra separata (log su file)
function Start-Uvicorn {
    param($repoPath,$pythonExe,$host,$port,$logDirName,$logFileName,$reload)
    $logDir = Join-Path $repoPath $logDirName
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
    $logFile = Join-Path $logDir $logFileName

    $args = @("-m","uvicorn","app.main:app","--host",$host,"--port",$port.ToString())
    if ($reload) { $args += "--reload" }

    if (Test-Path (Join-Path $repoPath $pythonExe)) {
        $pythonPath = Join-Path $repoPath $pythonExe
    } else {
        $pythonPath = "python"  # fallback
    }

    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = $pythonPath
    $startInfo.Arguments = ($args -join " ")
    $startInfo.UseShellExecute = $true
    $startInfo.RedirectStandardOutput = $false
    $startInfo.RedirectStandardError = $false

    Write-Info "Avvio server uvicorn in nuova finestra. Log: $logFile"
    # Start-Process con redirect su file via cmd /c (più compatibile)
    $cmd = "cmd.exe /c `"$pythonPath $($args -join ' ') 1>>`"$logFile`" 2>>&1`""
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c","start","UvicornServer",$cmd
    Start-Sleep -Seconds 2
}

# MAIN
Ensure-Elevated

# 1) Vai nella repo
if (-not (Test-Path $RepoPath)) { Write-Err "RepoPath non trovato: $RepoPath"; exit 1 }
Set-Location $RepoPath
Write-OK "Cartella corrente: $(Get-Location)"

# 2) Backup
Do-Backup -src "$RepoPath\" -dst $BackupDest

# 3) Install reqs (opzionale)
if ($DoInstallReqs) { Install-Requirements -repoPath $RepoPath }

# 4) Git flow
Git-Flow -repoPath $RepoPath

# 5) Start uvicorn
Start-Uvicorn -repoPath $RepoPath -pythonExe $PythonExe -host $UvicornHost -port $UvicornPort -logDirName $LogDirName -logFileName $LogFileName -reload $UvicornReload

# 6) Apri browser
if ($OpenBrowser) {
    $url = "http://$UvicornHost`:$UvicornPort"
    Write-Info "Apro il browser su $url"
    Start-Process $url
}

Write-OK "=== FINAL_START_ALL completed ==="
