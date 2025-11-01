param(
  [Parameter(Mandatory=$true)]
  [string]$FullRepo # es. "aicreator76/TPI_evoluto"
)

$ErrorActionPreference="Stop"

function Require-GH {
  if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw "GitHub CLI 'gh' non trovato. Installa da https://cli.github.com/ e riesegui." }
  try { gh auth status | Out-Null } catch { throw "Esegui 'gh auth login' prima di continuare." }
}

function Get-Json($cmd){
  $out = Invoke-Expression $cmd
  if (-not $out) { return $null }
  return $out | ConvertFrom-Json
}

Require-GH

# === Raccolta dati ===
$repo    = Get-Json "gh api repos/$FullRepo"
$protect = Get-Json "gh api repos/$FullRepo/branches/main/protection"
$flows   = Get-Json "gh api repos/$FullRepo/actions/workflows?per_page=100"
$runs    = Get-Json "gh api repos/$FullRepo/actions/runs?branch=main&per_page=1"

# Esistenza file/percorsi via Contents API (200 → esiste)
function Test-ContentExists($path){
  try { gh api repos/$FullRepo/contents/$path | Out-Null; return $true } catch { return $false }
}
$hasCODEOWNERS   = Test-ContentExists ".github/CODEOWNERS"
$hasPRTemplate   = Test-ContentExists ".github/PULL_REQUEST_TEMPLATE.md"
$hasIssueBug     = Test-ContentExists ".github/ISSUE_TEMPLATE/bug_report.yml"
$hasEditorconfig = Test-ContentExists ".editorconfig"
$hasCIYml        = Test-ContentExists ".github/workflows/ci.yml"

# Workflow "CI" presente?
$hasWorkflowCI = $false
if ($flows -and $flows.workflows) {
  $hasWorkflowCI = $flows.workflows | Where-Object { $_.name -eq "CI" } | ForEach-Object { $true } | Select-Object -First 1
  if (-not $hasWorkflowCI) { $hasWorkflowCI = $false }
}

# Ultimo run su main (se presente)
$lastRunStatus = $null
$lastRunConclusion = $null
if ($runs -and $runs.workflow_runs -and $runs.workflow_runs.Count -gt 0) {
  $lastRunStatus     = $runs.workflow_runs[0].status
  $lastRunConclusion = $runs.workflow_runs[0].conclusion
}

# Protezioni branch main
$bp_strict         = $false
$bp_contexts       = @()
$bp_approvals      = 0
$bp_dismiss_stale  = $false
$bp_admins         = $false
if ($protect) {
  $bp_strict        = [bool]$protect.required_status_checks.strict
  if ($protect.required_status_checks.contexts) { $bp_contexts = @($protect.required_status_checks.contexts) } else { $bp_contexts = @() }
  if ($protect.required_pull_request_reviews) {
    $bp_approvals     = [int]$protect.required_pull_request_reviews.required_approving_review_count
    $bp_dismiss_stale = [bool]$protect.required_pull_request_reviews.dismiss_stale_reviews
  }
  $bp_admins        = [bool]$protect.enforce_admins.enabled
}

# Flag repo
$flag_auto_merge       = [bool]$repo.allow_auto_merge
$flag_update_branch    = [bool]$repo.allow_update_branch
$flag_delete_on_merge  = [bool]$repo.delete_branch_on_merge
$default_branch        = $repo.default_branch

# Security & analysis (solo informativo: alcune feature non disponibili su repo personali)
$sec = $repo.security_and_analysis
$dependabot_updates = $null
if ($sec) { $dependabot_updates = $sec.dependabot_security_updates.status }

# === Regole di conformità ===
$non = New-Object System.Collections.Generic.List[string]

if ($default_branch -ne "main") { $non.Add("default_branch != main") }
if (-not $bp_strict) { $non.Add("branch_protection.strict=false") }
if (-not ($bp_contexts -contains "CI")) { $non.Add("required_check 'CI' mancante su main") }
if ($bp_approvals -lt 2) { $non.Add("approvals<2 su main") }
if (-not $bp_dismiss_stale) { $non.Add("dismiss_stale_reviews=false su main") }
if (-not $bp_admins) { $non.Add("enforce_admins=false su main") }

if (-not $flag_delete_on_merge) { $non.Add("delete_branch_on_merge=false") }
# Policy merge: consentiamo solo squash (requisito consigliato)
if ($repo.squash_merge_allowed -ne $true) { $non.Add("squash_merge disabilitato") }
if ($repo.rebase_merge_allowed -eq $true) { $non.Add("rebase_merge abilitato") }
if ($repo.merge_commit_allowed -eq $true) { $non.Add("merge_commit abilitato") }

# Governance file
if (-not $hasCODEOWNERS)   { $non.Add("manca .github/CODEOWNERS") }
if (-not $hasPRTemplate)   { $non.Add("manca .github/PULL_REQUEST_TEMPLATE.md") }
if (-not $hasIssueBug)     { $non.Add("manca .github/ISSUE_TEMPLATE/bug_report.yml") }
if (-not $hasEditorconfig) { $non.Add("manca .editorconfig") }

# CI
if (-not $hasCIYml)   { $non.Add("manca .github/workflows/ci.yml") }
if (-not $hasWorkflowCI) { $non.Add("workflow con name 'CI' non trovato") }
if ($lastRunConclusion -and $lastRunConclusion -ne "success") { $non.Add("ultimo run CI su main non success") }

# Status complessivo
$status = "ok"
if ($non.Count -gt 0) {
  # separa tra error/warn: se tocca branch protection/CI → fail
  $isFail = $non | Where-Object {
    $_ -match "branch_protection" -or
    $_ -match "required_check" -or
    $_ -match "approvals<2" -or
    $_ -match "workflow" -or
    $_ -match "ultimo run CI"
  }
  if ($isFail) { $status = "fail" } else { $status = "warn" }
}

# Suggerimenti rapidi
$suggerimenti = @()
if ($non -contains "required_check 'CI' mancante su main") { $suggerimenti += "Aggiungi 'CI' tra i required checks del branch main." }
if ($non -contains "approvals<2 su main") { $suggerimenti += "Imposta required_approving_review_count=2." }
if ($non -contains "dismiss_stale_reviews=false su main") { $suggerimenti += "Abilita dismiss_stale_reviews." }
if ($non -contains "enforce_admins=false su main") { $suggerimenti += "Abilita enforce_admins=true." }
if ($non -contains "manca .github/CODEOWNERS") { $suggerimenti += "Aggiungi CODEOWNERS con i manutentori su /data/cataloghi/* e /ops/*." }
if ($non -contains "manca .github/PULL_REQUEST_TEMPLATE.md") { $suggerimenti += "Aggiungi un PR template con checklist CI/approvals." }
if ($non -contains "manca .github/ISSUE_TEMPLATE/bug_report.yml") { $suggerimenti += "Aggiungi issue template bug_report.yml." }
if ($non -contains "manca .editorconfig") { $suggerimenti += "Aggiungi .editorconfig per formati coerenti." }
if ($non -contains "manca .github/workflows/ci.yml") { $suggerimenti += "Aggiungi ci.yml con name: CI e job basilari." }
if ($non -contains "workflow con name 'CI' non trovato") { $suggerimenti += "Assicurati che ci.yml abbia 'name: CI'." }
if ($non -contains "ultimo run CI su main non success") { $suggerimenti += "Rerun/risolvi il fallimento CI su main." }
if ($non -contains "delete_branch_on_merge=false") { $suggerimenti += "Abilita delete_branch_on_merge." }
if ($non -contains "squash_merge disabilitato") { $suggerimenti += "Abilita solo squash merge." }
if ($non -contains "rebase_merge abilitato") { $suggerimenti += "Disabilita rebase merge." }
if ($non -contains "merge_commit abilitato") { $suggerimenti += "Disabilita merge commit." }

# Output JSON (≤120 parole nella summary non lo forziamo strict, ma restiamo concisi)
$result = [pscustomobject]@{
  status = $status
  summary = if ($status -eq "ok") { "Hardening conforme: branch protection, CI e governance a posto." }
            elseif ($status -eq "warn") { "Hardening quasi conforme: presenti piccole avvertenze da sistemare." }
            else { "Hardening NON conforme: correggere le regole chiave (branch protection/CI/governance)." }
  non_compliance = $non
  details = [pscustomobject]@{
    default_branch   = $default_branch
    branch_protection = [pscustomobject]@{
      strict=$bp_strict; contexts=$bp_contexts; approvals=$bp_approvals; dismiss_stale=$bp_dismiss_stale; enforce_admins=$bp_admins
    }
    repo_flags = [pscustomobject]@{
      allow_auto_merge=$flag_auto_merge; allow_update_branch=$flag_update_branch; delete_branch_on_merge=$flag_delete_on_merge
    }
    ci = [pscustomobject]@{
      has_ci_yml=$hasCIYml; has_workflow_CI=$hasWorkflowCI; last_run_status=$lastRunStatus; last_run_conclusion=$lastRunConclusion
    }
    files = [pscustomobject]@{
      CODEOWNERS=$hasCODEOWNERS; PR_TEMPLATE=$hasPRTemplate; ISSUE_BUG=$hasIssueBug; editorconfig=$hasEditorconfig
    }
    security_and_analysis = [pscustomobject]@{
      dependabot_security_updates=$dependabot_updates
    }
  }
  suggestions = $suggerimenti
}

$result | ConvertTo-Json -Depth 10
