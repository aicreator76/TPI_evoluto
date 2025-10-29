param(
  [string]$Owner = "aicreator76",
  [string]$Repo  = "TPI_evoluto",
  [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"
$FullRepo = "$Owner/$Repo"

function Require-GH {
  if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI 'gh' non trovato. Installa da https://cli.github.com/ e riesegui."
  }
  try { gh auth status | Out-Null } catch { throw "Esegui 'gh auth login' prima di continuare." }
}
Require-GH

Write-Host "→ Repo: $FullRepo  |  Branch: $Branch"

# 1) Branch protection
@"
{
  "required_status_checks": { "strict": true, "contexts": ["CI"] },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 2,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
"@ | gh api -X PUT repos/$FullRepo/branches/$Branch/protection --input - | Out-Null
Write-Host "✓ Branch protection applicata"

# 2) Merge policy: solo squash + delete branch
@"
{
  "allow_squash_merge": true,
  "allow_merge_commit": false,
  "allow_rebase_merge": false,
  "delete_branch_on_merge": true
}
"@ | gh api -X PATCH repos/$FullRepo --input - | Out-Null
Write-Host "✓ Merge policy impostata (solo squash + delete branch)"

# 3) CODEOWNERS
New-Item -ItemType Directory -Force ".github" | Out-Null
@"
# Richiede approver su cartelle sensibili
/data/cataloghi/*  @$Owner
/ops/*             @$Owner
"@ | Set-Content -Encoding UTF8 ".github/CODEOWNERS"
Write-Host "✓ CODEOWNERS generato"

# 4) Templates PR/Issue
New-Item -ItemType Directory -Force ".github/ISSUE_TEMPLATE" | Out-Null
@"
## Descrizione
<!-- cosa cambia e perché -->

## Checklist
- [ ] Conventional Commits
- [ ] CI verde
- [ ] Docs/Changelog aggiornati (se serve)
"@ | Set-Content -Encoding UTF8 ".github/PULL_REQUEST_TEMPLATE.md"

@"
name: Bug report
labels: bug
body:
  - type: textarea
    attributes: { label: Problema, description: Cosa non funziona }
"@ | Set-Content -Encoding UTF8 ".github/ISSUE_TEMPLATE/bug_report.yml"

@"
name: Feature request
labels: feat
body:
  - type: textarea
    attributes: { label: Proposta, description: Cosa vuoi ottenere }
"@ | Set-Content -Encoding UTF8 ".github/ISSUE_TEMPLATE/feature_request.yml"
Write-Host "✓ Template PR/Issue creati"

# 5) Labels (idempotenti: --force)
$labels = @(
  @{name="bug";      color="d73a4a"; description="Bug"},
  @{name="feat";     color="a2eeef"; description="Feature"},
  @{name="docs";     color="0075ca"; description="Documentazione"},
  @{name="ci";       color="cfd3d7"; description="CI/CD"},
  @{name="chore";    color="ffffff"; description="Chore"},
  @{name="refactor"; color="c5def5"; description="Refactor"},
  @{name="perf";     color="f7c6c7"; description="Performance"},
  @{name="test";     color="e4e669"; description="Testing"},
  @{name="breaking"; color="b60205"; description="Breaking change"}
)
foreach ($l in $labels) {
  gh label create $l.name --color $l.color --description $l.description --repo $FullRepo --force 2>$null | Out-Null
}
Write-Host "✓ Label canonicali presenti/aggiornati"

# 6) Badge CI nel README (se manca) + normalizza UTF-8 LF (no BOM)
$readme = "README.md"
if (Test-Path $readme) {
  $raw = Get-Content -Raw $readme
  if ($raw -notmatch "\[CI\]\(https://github.com/$Owner/$Repo/actions/workflows/ci\.yml/badge\.svg\)") {
    $raw = $raw -replace "^(# .+?)\r?\n", "`$0![CI](https://github.com/$Owner/$Repo/actions/workflows/ci.yml/badge.svg)`r`n"
  }
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($readme, ($raw -replace "`r`n","`n"), $utf8NoBom)
  Write-Host "✓ README badge CI verificato/aggiunto"
} else {
  Write-Host "• README.md non trovato: salto badge"
}

git add .github/CODEOWNERS .github/PULL_REQUEST_TEMPLATE.md .github/ISSUE_TEMPLATE/*.yml 2>$null
if (Test-Path $readme) { git add README.md 2>$null }
if ((git diff --cached --name-only) -ne $null) {
  git commit -m "ci/docs(guardian): protections, merge policy, templates, labels, README badge" 2>$null
  git push 2>$null
  Write-Host "✓ Commit & push governance completati"
} else {
  Write-Host "• Nessuna modifica da committare"
}

# 7) Avvio CI (se workflow si chiama 'CI')
try {
  gh workflow run CI --repo $FullRepo | Out-Null
  Write-Host "✓ CI avviata su $FullRepo"
} catch {
  Write-Host "• CI non avviata (verifica il nome del workflow)"
}

Write-Host "DONE."
