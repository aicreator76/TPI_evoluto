[CmdletBinding()]
param(
  [int]$Limit = 10,
  [string]$Branch = ""
)

if (-not $env:GH_TOKEN) { Write-Error "GH_TOKEN env var is required"; exit 1 }
if ([string]::IsNullOrEmpty($Branch)) { $Branch = (git rev-parse --abbrev-ref HEAD) }

Write-Host "Rerunning up to $Limit failed workflow runs on branch '$Branch'..."

$repo = "${env:GITHUB_REPOSITORY}"
if (-not $repo) {
  $originUrl = git config --get remote.origin.url
  if ($originUrl -match "github.com[:/](.+?)/(.+?)(\.git)?$") {
    $repo = "$($Matches[1])/$($Matches[2])"
  } else {
    Write-Error "Cannot infer repository slug. Set GITHUB_REPOSITORY."
    exit 1
  }
}

$failedRuns = gh api -H "Accept: application/vnd.github+json" `
  "/repos/$repo/actions/runs?branch=$Branch&status=failure&per_page=50" `
  | ConvertFrom-Json

$ids = @()
foreach ($run in $failedRuns.workflow_runs) {
  if ($ids.Count -ge $Limit) { break }
  $ids += $run.id
}

if ($ids.Count -eq 0) {
  Write-Host "No failed runs to rerun."
  exit 0
}

foreach ($id in $ids) {
  Write-Host "Rerunning workflow run id: $id"
  gh api -X POST -H "Accept: application/vnd.github+json" "/repos/$repo/actions/runs/$id/rerun"
}
