#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Rerun failed GitHub Actions workflow runs
.DESCRIPTION
    Uses GitHub CLI to find and rerun failed workflow runs on the current or specified branch
.PARAMETER MaxReruns
    Maximum number of failed runs to rerun (default: 3)
.PARAMETER Branch
    Branch name (default: current branch)
.EXAMPLE
    ./rerun_failed.ps1
    ./rerun_failed.ps1 -MaxReruns 5
    ./rerun_failed.ps1 -Branch "main"
#>

param(
    [int]$MaxReruns = 3,
    [string]$Branch = ""
)

# Check if gh CLI is installed
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI (gh) is not installed. Please install it from https://cli.github.com/"
    exit 1
}

# Check if authenticated
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Not authenticated with GitHub CLI. Run 'gh auth login' first."
    exit 1
}

# Get current branch if not specified
if ([string]::IsNullOrWhiteSpace($Branch)) {
    try {
        $Branch = git rev-parse --abbrev-ref HEAD 2>$null
        if ($LASTEXITCODE -ne 0) {
            $Branch = "main"
            Write-Warning "Could not detect current branch, using 'main'"
        }
    } catch {
        $Branch = "main"
        Write-Warning "Could not detect current branch, using 'main'"
    }
}

Write-Host "🔍 Searching for failed workflow runs on branch: $Branch" -ForegroundColor Cyan
Write-Host "📊 Maximum reruns: $MaxReruns" -ForegroundColor Cyan

# Get failed workflow runs
try {
    $runsJson = gh run list --branch $Branch --status failure --limit $MaxReruns --json databaseId,name,conclusion,headBranch,workflowName
    $runs = $runsJson | ConvertFrom-Json
} catch {
    Write-Error "Failed to fetch workflow runs: $_"
    exit 1
}

if ($runs.Count -eq 0) {
    Write-Host "✅ No failed workflow runs found on branch '$Branch'" -ForegroundColor Green
    exit 0
}

Write-Host "📋 Found $($runs.Count) failed run(s):" -ForegroundColor Yellow
foreach ($run in $runs) {
    Write-Host "  • $($run.workflowName) - Run #$($run.databaseId)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "🔄 Rerunning failed jobs..." -ForegroundColor Cyan

$rerunCount = 0
foreach ($run in $runs) {
    try {
        Write-Host "  ⏳ Rerunning: $($run.workflowName) (ID: $($run.databaseId))" -ForegroundColor White
        gh run rerun $run.databaseId --failed 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    ✓ Rerun queued successfully" -ForegroundColor Green
            $rerunCount++
        } else {
            Write-Host "    ✗ Failed to rerun" -ForegroundColor Red
        }
        
        # Small delay to avoid rate limiting
        Start-Sleep -Milliseconds 500
    } catch {
        Write-Warning "  Failed to rerun workflow $($run.databaseId): $_"
    }
}

Write-Host ""
Write-Host "🎉 Rerun complete! Queued $rerunCount out of $($runs.Count) workflow(s)" -ForegroundColor Green
Write-Host "💡 Check status at: https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/actions" -ForegroundColor Cyan
