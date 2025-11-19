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
    [string]$Repo,          # es: "aicreator76/TPI_evoluto" (opzionale, se non lanciato dentro il repo)
    [switch]$DryRun         # se presente, NON crea l'issue, ma mostra solo cosa farebbe
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
        $repoInfo = gh repo view --json nameWithOwner | ConvertFrom-Json
        $Repo = $repoInfo.nameWithOwner   # es. aicreator76/TPI_evoluto
    } catch {
        Write-Error "Impossibile dedurre il repo corrente. Specifica -Repo ""owner/repo""."
        exit 1
    }
}

Write-Host "CESARE_GH_issue – Repo corrente: $Repo" -ForegroundColor Cyan
Write-Host ""

# =========================
# 1) Recupero Milestone via gh api
# =========================

Write-Host "Recupero le milestone aperte da GitHub..." -ForegroundColor Yellow

# es: repos/aicreator76/TPI_evoluto/milestones?state=open&per_page=100
$milestonesJson = gh api "repos/$Repo/milestones?state=open&per_page=100" 2>$null

if (-not $milestonesJson) {
    Write-Error "Nessuna milestone aperta trovata su $Repo. Controlla che esistano (M1, M2, M3) e che gh sia autenticato."
    exit 1
}

try {
    $milestones = $milestonesJson | ConvertFrom-Json
} catch {
    Write-Error "Errore nel parsing JSON delle milestone. Output gh api non valido."
    Write-Host $milestonesJson
    exit 1
}

if (-not $milestones -or $milestones.Count -eq 0) {
    Write-Error "Nessuna milestone aperta trovata su $Repo (lista vuota)."
    exit 1
}

Write-Host ""
Write-Host "Seleziona la milestone:" -ForegroundColor Green

for ($i = 0; $i -lt $milestones.Count; $i++) {
    $idx = $i + 1
    $title = $milestones[$i].title
    $desc  = $milestones[$i].description
    if ($desc -and $desc.Length -gt 60) {
        $desc = $desc.Substring(0,57) + "..."
    }
    Write-Host ("[{0}] {1}  {2}" -f $idx, $title, ($desc ?? ""))
}

[int]$choice = 0
while ($choice -lt 1 -or $choice -gt $milestones.Count) {
    $choice = Read-Host "Numero della milestone"
}

$selectedMilestone = $milestones[$choice - 1]
$milestoneTitle    = $selectedMilestone.title

Write-Host ""
Write-Host "Milestone scelta: $milestoneTitle" -ForegroundColor Cyan

# =========================
# 2) Prefisso titolo (M1/M2/M3)
# =========================

$milestoneCode = ($milestoneTitle -split '\s+')[0]  # es. "M1"
if (-not $milestoneCode) { $milestoneCode = "M?" }
$prefix = "[{0}]" -f $milestoneCode

# =========================
# 3) Titolo breve Issue
# =========================

Write-Host ""
$titoloBreve = Read-Host "Inserisci il titolo breve dell'Issue (es. CRUD DPI con stati principali)"

if (-not $titoloBreve) {
    Write-Error "Titolo breve vuoto. Interrotto."
    exit 1
}

$fullTitle = "$prefix $titoloBreve"

Write-Host ""
Write-Host "Titolo completo Issue: $fullTitle" -ForegroundColor Cyan

# =========================
# 4) Scelta template da ops\issue_templates
# =========================

$templateFolder = Join-Path (Get-Location) "ops\issue_templates"

if (-not (Test-Path $templateFolder)) {
    Write-Error "Cartella template non trovata: $templateFolder. Assicurati di avere ops\\issue_templates sul repo."
    exit 1
}

$templates = Get-ChildItem -Path $templateFolder -Filter *.md
if (-not $templates) {
    Write-Error "Nessun template .md trovato in $templateFolder."
    exit 1
}

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
$bodyFile = $selectedTemplate.FullName
Write-Host "Userò il template: $($selectedTemplate.Name)" -ForegroundColor Cyan

# =========================
# 5) Label
# =========================

Write-Host ""
Write-Host "Label di default: area:backend, type:feature, priority:high" -ForegroundColor Green
$labelInput = Read-Host "Inserisci le label separate da virgola (INVIO per usare default)"

if ([string]::IsNullOrWhiteSpace($labelInput)) {
    $labels = @("area:backend","type:feature","priority:high")
} else {
    $labels = $labelInput.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
}

Write-Host ""
Write-Host "Creazione Issue su $Repo" -ForegroundColor Yellow
Write-Host "Titolo:    $fullTitle"
Write-Host "Milestone: $milestoneTitle"
Write-Host "Body:      $bodyFile"
Write-Host "Label:     $($labels -join ', ')"
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
    Write-Host "gh $($ghArgs -join ' ')"
} else {
    Write-Host "Eseguo: gh $($ghArgs -join ' ')" -ForegroundColor Yellow
    gh @ghArgs
}

Write-Host ""
Write-Host "CESARE_GH_issue – Done." -ForegroundColor Cyan
