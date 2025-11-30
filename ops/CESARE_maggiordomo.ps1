<#
  CESARE_maggiordomo.ps1
  Maggiordomo CESARE - Console operativa del Regno di Camelot per TPI_evoluto.

  Uso consigliato:
    PS> Set-Location "E:\CLONAZIONE\tpi_evoluto"
    PS> .\ops\CESARE_maggiordomo.ps1

  Opzioni:
    -Demo   -> non lancia script esterni, solo stampa cosa farebbe
#>

[CmdletBinding()]
param(
    [switch]$Demo
)

# =========================
# Config base (repo, log, ecc.)
# =========================

# Cartella ops (dove sta questo script)
$OpsDir   = $PSScriptRoot
# Root repo (cartella padre di ops)
$RepoRoot = Split-Path $OpsDir -Parent
# Cartella log (puoi cambiarla a E:\CLONAZIONE\LOG se preferisci assoluto)
$LogDir   = Join-Path $RepoRoot "LOG"

if (-not (Test-Path $LogDir -PathType Container)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$LogFile = Join-Path $LogDir ("maggiordomo-{0:yyyy-MM-dd}.log" -f (Get-Date))

function Write-MaggiordomoLog {
    param(
        [string]$Message
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[{0}] {1}" -f $timestamp, $Message
    Add-Content -Path $LogFile -Value $line
}

# =========================
# Banner e menu
# =========================

function Show-Banner {
    Clear-Host
    Write-Host "=====================================" -ForegroundColor Yellow
    Write-Host "   CAMELOT - Console del Sovrano"      -ForegroundColor Yellow
    Write-Host "=====================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "[CESARE] Maggiordomo: attivo." -ForegroundColor Cyan
    Write-Host ""
}

function Show-Menu {
    Write-Host "Comandi rapidi disponibili:" -ForegroundColor Green
    Write-Host " 1) RIPRENDI-REGNO      -> Cruscotto + Regina + (Cronista se presente)"
    Write-Host " 2) ORCHESTRA-PRIME     -> Solo cruscotto tecnico"
    Write-Host " 3) REGINA-AELIS        -> Solo console della Regina"
    Write-Host " 4) AGENTE-SIGMA / sigma -> Consiglio tecnico locale (Gemma2)"
    Write-Host " 5) AELIS-GEMMA         -> Oracolo tecnico (Gemma3, quando scaricata)"
    Write-Host " 6) AELIS-LLAMA         -> Voce creativa (se modello llama presente)"
    Write-Host " 7) STATO-REGNO         -> Riepilogo rapido TPI/snapshot/release"
    Write-Host " Q) Esci dal Maggiordomo"
    Write-Host ""
}

function Invoke-CommandSafe {
    param(
        [string]$Name,
        [scriptblock]$Action
    )

    Write-MaggiordomoLog ("Esecuzione comando: {0}" -f $Name)

    if ($Demo) {
        Write-Host ("[DEMO] Eseguirei comando: {0}" -f $Name) -ForegroundColor Yellow
        return
    }

    try {
        & $Action
    } catch {
        Write-Host ("Errore durante l'esecuzione di [{0}]: {1}" -f $Name, $_.Exception.Message) -ForegroundColor Red
        Write-MaggiordomoLog ("ERRORE [{0}]: {1}" -f $Name, $_.Exception.Message)
    }
}

# =========================
# Azioni per ogni comando
# =========================

function Do-RiprendiRegno {
    Invoke-CommandSafe -Name "RIPRENDI-REGNO" -Action {
        Write-Host "TODO: lanciare cruscotto + Regina + Cronista." -ForegroundColor Cyan
        # Esempi futuri:
        # & "$RepoRoot\ops\CESARE_cruscotto.ps1"
        # & "$RepoRoot\ops\CESARE_regina.ps1"
    }
}

function Do-OrchestraPrime {
    Invoke-CommandSafe -Name "ORCHESTRA-PRIME" -Action {
        Write-Host "TODO: lanciare cruscotto tecnico (stato servizi, FastAPI, n8n...). " -ForegroundColor Cyan
        # & "$RepoRoot\ops\CESARE_orchestra_prime.ps1"
    }
}

function Do-ReginaAelis {
    Invoke-CommandSafe -Name "REGINA-AELIS" -Action {
        Write-Host "TODO: aprire console dedicata REGINA-AELIS (prompt comandi di alto livello)." -ForegroundColor Cyan
        # & "$RepoRoot\ops\CESARE_regina_console.ps1"
    }
}

function Do-AgenteSigma {
    Invoke-CommandSafe -Name "AGENTE-SIGMA" -Action {
        Write-Host "TODO: agganciare script sigma / Gemma2 locale." -ForegroundColor Cyan
        # & "$RepoRoot\ops\CESARE_sigma.ps1"
    }
}

function Do-AelisGemma {
    Invoke-CommandSafe -Name "AELIS-GEMMA" -Action {
        Write-Host "TODO: agganciare Gemma3 / oracolo tecnico quando disponibile." -ForegroundColor Cyan
        # & "$RepoRoot\ops\CESARE_gemma.ps1"
    }
}

function Do-AelisLlama {
    Invoke-CommandSafe -Name "AELIS-LLAMA" -Action {
        Write-Host "TODO: agganciare modello LLaMA creativo (se presente)." -ForegroundColor Cyan
        # & "$RepoRoot\ops\CESARE_llama.ps1"
    }
}

function Do-StatoRegno {
    Invoke-CommandSafe -Name "STATO-REGNO" -Action {
        Write-Host "TODO: mostrare snapshot TPI, ultimo tag, stato FastAPI/n8n, ecc." -ForegroundColor Cyan
        # & "$RepoRoot\ops\CESARE_stato_regno.ps1"
    }
}

# =========================
# Loop principale
# =========================

Show-Banner
Write-MaggiordomoLog ("Avvio Maggiordomo CESARE (Demo={0})" -f $Demo)

do {
    Show-Menu
    $input = Read-Host "Scegli un comando (es. 1, RIPRENDI-REGNO, Q per uscire)"

    # Normalizza input
    $cmd = $input.Trim()

    switch -Regex ($cmd.ToUpper()) {
        "^1$|^RIPRENDI-REGNO$" {
            Do-RiprendiRegno
        }
        "^2$|^ORCHESTRA-PRIME$" {
            Do-OrchestraPrime
        }
        "^3$|^REGINA-AELIS$" {
            Do-ReginaAelis
        }
        "^4$|^AGENTE-SIGMA$|^SIGMA$" {
            Do-AgenteSigma
        }
        "^5$|^AELIS-GEMMA$" {
            Do-AelisGemma
        }
        "^6$|^AELIS-LLAMA$" {
            Do-AelisLlama
        }
        "^7$|^STATO-REGNO$" {
            Do-StatoRegno
        }
        "^(Q|QUIT|EXIT)$" {
            Write-Host "Uscita dal Maggiordomo CESARE. Che il Regno prosperi." -ForegroundColor Green
            Write-MaggiordomoLog "Uscita richiesta dall'utente."
            break
        }
        default {
            if ($cmd -ne "") {
                Write-Host ("Comando non riconosciuto: {0}" -f $cmd) -ForegroundColor Red
            }
        }
    }

    Write-Host ""
} while ($true)
