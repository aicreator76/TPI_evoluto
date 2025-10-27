param(
  [switch]$Savepoint,
  [switch]$Align,
  [string]$Feature,
  [string]$Hotfix
)

function Get-Branch { (git rev-parse --abbrev-ref HEAD).Trim() }

function Do-Savepoint {
  git fetch --all --prune
  if ((git status --porcelain).Length -gt 0) {
    git add -A
    $date = Get-Date -Format "yyyy-MM-dd"
    git commit -m "chore(savepoint): snapshot $date"
    try { git push } catch { git push -u origin (Get-Branch) }
  } else {
    Write-Host "ℹ️ Nessuna modifica locale: solo push/tag."
    try { git push } catch { git push -u origin (Get-Branch) }
  }
  $tag = "Snapshot-OK-" + (Get-Date -Format "yyyy-MM-dd")
  # ricrea tag del giorno idempotente
  if (git rev-parse $tag 2>$null) {
    git tag -d $tag | Out-Null
    git push origin :refs/tags/$tag | Out-Null
  }
  git tag -a $tag -m "Savepoint $tag"
  git push origin $tag
  Write-Host "✅ Savepoint completato su '$(Get-Branch)' + tag $tag"
}

function Do-Align {
  git fetch --all --prune
  git --no-pager log --oneline --graph --decorate -n 12
  $up = "origin/" + (Get-Branch)
  Write-Host "ℹ️ Rebase interattivo su $up (ESC per annullare merge-tool)."
  git rebase $up
  Write-Host "ℹ️ Se conflitti: risolvi, poi 'git rebase --continue'."
  Write-Host "ℹ️ Infine: 'git push --force-with-lease'"
}

function New-Feature([string]$name) {
  if (-not $name) { throw "Fornisci un nome: -Feature <slug>" }
  $slug = $name.ToLower() -replace '[^a-z0-9\-]+','-'
  git checkout -b "feat/$slug"
  git commit --allow-empty -m "chore: start feat/$slug"
  git push -u origin "feat/$slug"
  Write-Host "🌿 Branch creato: feat/$slug"
}

function New-Hotfix([string]$name) {
  if (-not $name) { throw "Fornisci un nome: -Hotfix <slug>" }
  $slug = $name.ToLower() -replace '[^a-z0-9\-]+','-'
  git checkout -b "hotfix/$slug"
  git commit --allow-empty -m "chore: start hotfix/$slug"
  git push -u origin "hotfix/$slug"
  $tag = "Snapshot-OK-" + (Get-Date -Format "yyyy-MM-dd") + "-hotfix"
  git tag -a $tag -m "Hotfix start $tag"
  git push origin $tag
  Write-Host "🚑 Hotfix creato: hotfix/$slug + tag $tag"
}

if ($Savepoint) { Do-Savepoint; exit 0 }
if ($Align)     { Do-Align;     exit 0 }
if ($Feature)   { New-Feature $Feature; exit 0 }
if ($Hotfix)    { New-Hotfix $Hotfix;   exit 0 }

Write-Host @"
Usage:
  pwsh .\savepoint_workflows.ps1 -Savepoint     # commit/tag del giorno
  pwsh .\savepoint_workflows.ps1 -Align         # rebase su origin/<branch>
  pwsh .\savepoint_workflows.ps1 -Feature nome  # crea feat/<nome>
  pwsh .\savepoint_workflows.ps1 -Hotfix nome   # crea hotfix/<nome>
"@
