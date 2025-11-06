[CmdletBinding()]
param(
  [switch]$VerboseMode
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Section {
  param($msg)
  Write-Host ""
  Write-Host "==> $msg" -ForegroundColor Cyan
}

function Exec {
  param($cmd, [string[]]$args)
  if ($VerboseMode) { Write-Host "RUN:" $cmd $args }
  & $cmd @args
  return $LASTEXITCODE
}

# 0) root git + prerequisiti
Write-Section "Rilevo root Git"
$gitRoot = (& git rev-parse --show-toplevel).Trim()
if (-not $gitRoot) { Write-Error "Non sembra una repository Git."; exit 100 }
Set-Location $gitRoot

foreach ($bin in @('git','pre-commit')) {
  if (-not (Get-Command $bin -ErrorAction SilentlyContinue)) {
    Write-Error "Comando mancante: $bin"
    exit 101
  }
}

# 1) validazione YAML (solo se l'hook esiste)
Write-Section "Validazione YAML (se configurato)"
$hasCheckYaml = (Test-Path ".pre-commit-config.yaml") -and (Select-String -Path ".pre-commit-config.yaml" -Pattern "id:\s*check-yaml" -Quiet)
if ($hasCheckYaml) {
  $rcYaml = Exec 'pre-commit' @('run','check-yaml','-a')
  if ($rcYaml -ne 0) { Write-Error "check-yaml ha trovato problemi."; exit 1 }
} else {
  Write-Host "Hook check-yaml non presente: salto la validazione YAML." -ForegroundColor Yellow
}

# 2) tutti gli hook (puo' modificare file)
Write-Section "Esecuzione pre-commit run -a"
$pcRc = Exec 'pre-commit' @('run','-a')
if ($pcRc -ne 0) {
  Write-Warning "Alcuni hook hanno modificato file o fallito."
  Write-Warning "Suggerito: git add -A ; ripeti il commit e/o rilancia lo script."
}

# 3) verifica .secrets.baseline (JSON valido + staged se modificato)
$baselinePath = Join-Path $gitRoot '.secrets.baseline'
Write-Section "Verifica baseline: $baselinePath"

if (-not (Test-Path $baselinePath)) {
  Write-Error ".secrets.baseline non trovato. Genera la baseline prima."
  exit 2
}

try {
  $raw = Get-Content -Raw $baselinePath -Encoding UTF8
  $null = $raw | ConvertFrom-Json
  Write-Host "Baseline JSON valida" -ForegroundColor Green
}
catch {
  Write-Error (".secrets.baseline non e' JSON valido: {0}" -f $_.Exception.Message)
  exit 3
}

$hasWorktreeChanges = -not [string]::IsNullOrWhiteSpace((& git diff --name-only -- $baselinePath))
$hasStagedChanges   = -not [string]::IsNullOrWhiteSpace((& git diff --cached --name-only -- $baselinePath))
$isUntracked        = -not [string]::IsNullOrWhiteSpace((& git ls-files --others --exclude-standard -- $baselinePath))

if ($isUntracked -or $hasWorktreeChanges) {
  Write-Error ".secrets.baseline ha modifiche NON staged. Esegui:  git add .secrets.baseline"
  exit 4
}

if ($hasStagedChanges) {
  Write-Host "Baseline modificata ed e' STAGED" -ForegroundColor Green
} else {
  Write-Host "Baseline invariata rispetto a HEAD" -ForegroundColor Green
}

Write-Section "Completato"
if ($pcRc -eq 0) {
  Write-Host "Tutti i controlli sono OK." -ForegroundColor Green
  exit 0
} else {
  Write-Warning "pre-commit ha richiesto modifiche. Dopo git add -A ripeti il commit e rilancia lo script."
  exit 5
}