<#
  CESARE_GH_issue.ps1
  Assistente per creare Issue GitHub pulite e coerenti per TPI_evoluto.

  Requisiti:
  - PowerShell
  - GitHub CLI installata e autenticata (`gh auth login`)
  - Da lanciare dentro la cartella del repo (E:\CLONAZIONE\tpi_evoluto)
    oppure usare il parametro -Repo "owner/repo"
#>

[CmdletBinding()]
param(
    [string]$Repo,
    [switch]$DryRun,
    [switch]$Agente0
)

function Test-GhInstalled {
    try {
        gh --version | Out-Null
        return $true
    } catch {
        return $false
    }
}

if (-not (Test-GhInstalled)) {
    Write-Error "GitHub CLI (gh) non trovata. Installa gh da https://cli.github.com e riprova."
    exit 1
}

# Se Repo non è passato, proviamo a dedurlo dal contesto corrente
if (-not $Repo) {
    try {
        $repoInfoJson = gh repo view --json nameWithOwner 2>$null
        if (-not $repoInfoJson) {
            throw "Nessuna informazione repo trovata."
        }
        $repoInfo = $repoInfoJson | ConvertFrom-Json
        $Repo = $repoInfo.nameWithOwner   # es. aicreator76/TPI_evoluto
    } catch {
        Write-Error "Impossibile dedurre il repo corrente. Specifica -Repo ""owner/repo"". Dettaglio: $($_.Exception.Message)"
        exit 1
    }
}

Write-Host ""
Write-Host ("CESARE_GH_issue - Repo corrente: {0}" -f $Repo) -ForegroundColor Cyan
Write-Host ""

# =========================
# 1) Recupero Milestone via gh api
# =========================

Write-Host "Recupero le milestone aperte da GitHub..." -ForegroundColor Yellow

# Attenzione all'&: lo escapiamo con il backtick `
$apiPath = "repos/$Repo/milestones?state=open`&per_page=100"
$milestonesJson = gh api $apiPath 2>$null

if (-not $milestonesJson) {
    Write-Error "Nessuna milestone aperta trovata su $Repo o errore nella chiamata gh api."
    exit 1
}

try {
    $milestones = $milestonesJson | ConvertFrom-Json
} catch {
    Write-Error "Errore nel parsing JSON delle milestone. Output gh api non valido."
    Write-Host $milestonesJson
    exit 1
}

# Normalizza a array
if ($milestones -isnot [System.Array]) {
    $milestones = @($milestones)
}

if (-not $milestones -or $milestones.Count -eq 0) {
    Write-Error "Nessuna milestone aperta trovata su $Repo (lista vuota)."
    exit 1
}

$selectedMilestone = $null

if ($Agente0) {
    # Proviamo a prendere automaticamente una milestone che inizia con "M2"
    $selectedMilestone = $milestones | Where-Object { $_.title -like "M2*" } | Select-Object -First 1

    if (-not $selectedMilestone) {
        # fallback: prima milestone
        $selectedMilestone = $milestones[0]
    }

    Write-Host ""
    Write-Host ("[Agente0] Milestone scelta automaticamente: {0}" -f $selectedMilestone.title) -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Seleziona la milestone:" -ForegroundColor Green

    for ($i = 0; $i -lt $milestones.Count; $i++) {
        $idx   = $i + 1
        $title = $milestones[$i].title
        $desc  = $milestones[$i].description

        if ($desc -and $desc.Length -gt 60) {
            $desc = $desc.Substring(0,57) + "..."
        }

        if (-not $desc) { $desc = "" }

        Write-Host ("[{0}] {1}  {2}" -f $idx, $title, $desc)
    }

    [int]$choice = 0
    while ($choice -lt 1 -or $choice -gt $milestones.Count) {
        $choice = Read-Host "Numero della milestone"
    }

    $selectedMilestone = $milestones[$choice - 1]
}

$milestoneTitle = $selectedMilestone.title

Write-Host ""
Write-Host ("Milestone scelta: {0}" -f $milestoneTitle) -ForegroundColor Cyan

# =========================
# 2) Prefisso titolo (M1/M2/M3)
# =========================

$parts = $milestoneTitle -split '\s+'
if ($parts.Count -gt 0 -and $parts[0]) {
    $milestoneCode = $parts[0]
} else {
    $milestoneCode = "M?"
}
$prefix = "[" + $milestoneCode + "]"

# =========================
# 3) Titolo breve Issue
# =========================

Write-Host ""

if ($Agente0) {
    $suggestedTitle = "Agente 0 - integrazione n8n per notifiche DPI"
    $inputTitle = Read-Host "Titolo breve dell'Issue (INVIO per usare suggerimento: $suggestedTitle)"
    if ([string]::IsNullOrWhiteSpace($inputTitle)) {
        $titoloBreve = $suggestedTitle
    } else {
        $titoloBreve = $inputTitle
    }
} else {
    $titoloBreve = Read-Host "Titolo breve dell'Issue (es. CRUD DPI con stati principali)"
}

if (-not $titoloBreve) {
    Write-Error "Titolo breve vuoto. Interrotto."
    exit 1
}

$fullTitle = "$prefix $titoloBreve"

Write-Host ""
Write-Host ("Titolo completo Issue: {0}" -f $fullTitle) -ForegroundColor Cyan

# =========================
# 4) Scelta template da ops\issue_templates
# =========================

$templateFolder = Join-Path (Get-Location) "ops\issue_templates"

if (-not (Test-Path $templateFolder -PathType Container)) {
    Write-Error "Cartella template non trovata: $templateFolder. Assicurati di avere ops\issue_templates sul repo."
    exit 1
}

$templates = Get-ChildItem -Path $templateFolder -Filter *.md
if (-not $templates -or $templates.Count -eq 0) {
    Write-Error "Nessun template .md trovato in $templateFolder."
    exit 1
}

$selectedTemplate = $null

if ($Agente0) {
    $selectedTemplate = $templates | Where-Object { $_.Name -eq "M2-orchestratore0.md" } | Select-Object -First 1
    if ($selectedTemplate) {
        Write-Host ("[Agente0] Template scelto automaticamente: {0}" -f $selectedTemplate.Name) -ForegroundColor Green
    }
}

if (-not $selectedTemplate) {
    Write-Host ""
    Write-Host "Template disponibili:" -ForegroundColor Green
    for ($i = 0; $i -lt $templates.Count; $i++) {
        $idx = $i + 1
        Write-Host ("[{0}] {1}" -f $idx, $templates[$i].Name)
    }

    [int]$tchoice = 0
    while ($tchoice -lt 1 -or $tchoice -gt $templates.Count) {
        $tchoice = Read-Host "Numero del template"
    }

    $selectedTemplate = $templates[$tchoice - 1]
}

$bodyFile = $selectedTemplate.FullName

Write-Host ("Usero il template: {0}" -f $selectedTemplate.Name) -ForegroundColor Cyan

# =========================
# 5) Label
# =========================

Write-Host ""

[string[]]$defaultLabels = @()

if ($Agente0) {
    Write-Host "Label di default: area:backend, area:orchestrator, type:feature, priority:high" -ForegroundColor Green
    $defaultLabels = @("area:backend","area:orchestrator","type:feature","priority:high")
} else {
    Write-Host "Label di default: area:backend, type:feature, priority:high" -ForegroundColor Green
    $defaultLabels = @("area:backend","type:feature","priority:high")
}

$labelInput = Read-Host "Label (separate da virgola, INVIO per usare default)"

[string[]]$labels = @()
if ([string]::IsNullOrWhiteSpace($labelInput)) {
    $labels = $defaultLabels
} else {
    $tmp = $labelInput.Split(",")
    foreach ($l in $tmp) {
        $val = $l.Trim()
        if ($val -ne "") {
            $labels += $val
        }
    }
}

Write-Host ""
Write-Host "Creazione Issue su $Repo" -ForegroundColor Yellow
Write-Host "Titolo:    $fullTitle"
Write-Host "Milestone: $milestoneTitle"
Write-Host "Body:      $bodyFile"
Write-Host ("Label:     {0}" -f ($labels -join ", "))
Write-Host ""

# =========================
# 6) Comando gh finale
# =========================

$ghArgs = @(
    "issue","create",
    "-R",$Repo,
    "--title",$fullTitle,
    "--milestone",$milestoneTitle,
    "--body-file",$bodyFile
)

foreach ($lbl in $labels) {
    $ghArgs += @("--label", $lbl)
}

if ($DryRun) {
    Write-Host "[DRY-RUN] Comando che verrebbe eseguito:" -ForegroundColor Yellow
    Write-Host ("gh {0}" -f ($ghArgs -join " "))
} else {
    Write-Host ("Eseguo: gh {0}" -f ($ghArgs -join " ")) -ForegroundColor Yellow
    gh @ghArgs
}

Write-Host ""
Write-Host "CESARE_GH_issue - Done." -ForegroundColor Cyan
