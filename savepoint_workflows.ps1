<#
E:\CLONAZIONE\tpi_evoluto\savepoint_workflows.ps1

WORKFLOWS:
- Savepoint: commit snapshot (se serve) + tag Snapshot-OK-YYYY-MM-DD (annotated) + push + (opz) Cronista
            - su branch != BaseBranch: tag = Snapshot-OK-YYYY-MM-DD-<branch-suffix> (non tocca il tag main)
- Align:     fetch + rebase origin/<branch> (solo working tree pulita)
- Feature:   crea feat/<slug> (da BaseBranch o FromCurrent) + commit start (allow-empty) + push
- Hotfix:    crea hotfix/<slug> + commit start (allow-empty) + push + tag Snapshot-OK-YYYY-MM-DD-hotfix (annotated) + (opz) Cronista
            - su branch != BaseBranch: tag = Snapshot-OK-YYYY-MM-DD-hotfix-<branch-suffix>
- Doctor:    diagnostica repo/branch/head/dirty (+ remoto se disponibile)

NOTE:
- -DryRun: esegue SOLO git di lettura (locale); stampa gli altri comandi senza eseguirli.
- Hook pre-commit: se auto-fixa file, ristage e ritenta il commit.
- Tag: se remoto è "protetto" e non sovrascrivibile, crea fallback -02/-03/... fino a -99.
#>

[CmdletBinding(DefaultParameterSetName = "Help")]
param(
  [Parameter(ParameterSetName="Savepoint", Mandatory=$true)]
  [switch]$Savepoint,

  [Parameter(ParameterSetName="Align", Mandatory=$true)]
  [switch]$Align,

  [Parameter(ParameterSetName="Feature", Mandatory=$true)]
  [string]$Feature,

  [Parameter(ParameterSetName="Hotfix", Mandatory=$true)]
  [string]$Hotfix,

  [Parameter(ParameterSetName="Doctor", Mandatory=$true)]
  [switch]$Doctor,

  [string]$Remote = "origin",
  [string]$BaseBranch = "main",

  # Feature/Hotfix: parte dal branch corrente
  [switch]$FromCurrent,

  # Cronista post-savepoint/hotfix
  [switch]$Cronista,
  [string]$CronistaDir = "E:\CLONAZIONE\CESARE_COMANDI\scripts",

  # Sicurezza operativa
  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# UTF-8 output (riduce "  " in console)
try {
  $utf8 = [System.Text.UTF8Encoding]::new($false)
  $OutputEncoding = $utf8
  [Console]::OutputEncoding = $utf8
} catch {}

function Show-Usage {
  Write-Host @"
Usage:
  pwsh .\savepoint_workflows.ps1 -Doctor   [-DryRun]
  pwsh .\savepoint_workflows.ps1 -Savepoint [-Cronista] [-Remote origin] [-BaseBranch main] [-DryRun]
  pwsh .\savepoint_workflows.ps1 -Align     [-Remote origin] [-DryRun]
  pwsh .\savepoint_workflows.ps1 -Feature "nome" [-BaseBranch main] [-Remote origin] [-FromCurrent] [-DryRun]
  pwsh .\savepoint_workflows.ps1 -Hotfix  "nome" [-BaseBranch main] [-Remote origin] [-FromCurrent] [-Cronista] [-DryRun]

Note:
  - -DryRun esegue SOLO git di lettura (locale); stampa gli altri.
  - -FromCurrent crea il branch da dove sei ORA.
  - -Cronista cerca: cronista_salva_giornata_YYYY-MM-DD.ps1 poi cronista_salva_giornata.ps1
"@ -ForegroundColor Gray
}

function Normalize-GitArgs {
  param([object]$GitArgs)

  if($null -eq $GitArgs){ return @() }

  if($GitArgs -is [System.Array]){
    $arr = @()
    foreach($x in $GitArgs){
      if($null -ne $x){ $arr += [string]$x }
    }
  } else {
    $arr = @([string]$GitArgs)
  }

  $arr = @($arr | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
  if($arr.Count -eq 0){ return @() }

  if($arr.Count -eq 1){
    $s = $arr[0].Trim()
    if($s -match "^(rev-parse|status|remote|show-ref|for-each-ref|rev-list|log|cat-file|diff|show|fetch|push|tag|checkout|commit|pull|rebase|add|ls-remote)\b" -and
       $s -match "\s"){
      return @($s -split "\s+")
    }
  }

  return @($arr)
}

function Get-GitVerb {
  param([object]$GitArgs)
  $argv = @(Normalize-GitArgs $GitArgs)
  if($argv.Count -eq 0){ return "" }

  foreach($a in $argv){
    if(-not $a.StartsWith("-")) { return $a }
  }
  return ($argv | Select-Object -First 1)
}

function Invoke-Git {
  param(
    [Parameter(Mandatory=$true)]
    [Alias("Args")]
    [object]$GitArgs,

    [switch]$AllowFail,
    [switch]$Quiet
  )

  $argv = @(Normalize-GitArgs $GitArgs)
  if($argv.Count -eq 0){
    throw "❌ Invoke-Git: argomenti vuoti (GitArgs)."
  }

  $readOnlyVerbs = @(
    "rev-parse","status","remote","show-ref","for-each-ref","rev-list",
    "log","cat-file","diff","show","ls-remote"
  )

  $verb = Get-GitVerb $argv

  if($DryRun){
    if($readOnlyVerbs -contains $verb){
      Write-Host "🟡 DRYRUN-READ git $($argv -join ' ')" -ForegroundColor Yellow
      $raw  = & git @argv 2>&1
      $code = $LASTEXITCODE
      $out  = (($raw | Out-String).TrimEnd())

      if(-not $Quiet){ if($out) { $out } }
      if((-not $AllowFail) -and ($code -ne 0)){
        throw "❌ git $($argv -join ' ') FAILED (exit=$code)`n$out"
      }
      return $out
    }

    Write-Host "🟡 DRYRUN git $($argv -join ' ')" -ForegroundColor Yellow
    $global:LASTEXITCODE = 0
    return ""
  }

  $raw  = & git @argv 2>&1
  $code = $LASTEXITCODE
  $out  = (($raw | Out-String).TrimEnd())

  if(-not $Quiet){ if($out) { $out } }
  if((-not $AllowFail) -and ($code -ne 0)){
    throw "❌ git $($argv -join ' ') FAILED (exit=$code)`n$out"
  }
  return $out
}

function Ensure-GitRepo {
  $null = Invoke-Git -GitArgs @("rev-parse","--is-inside-work-tree") -AllowFail -Quiet
  if($LASTEXITCODE -ne 0){
    throw "❌ Non sei dentro una repo git. Vai in: E:\CLONAZIONE\tpi_evoluto"
  }
}

function Get-RepoRoot { (Invoke-Git -GitArgs @("rev-parse","--show-toplevel") -Quiet).Trim() }
function Get-Branch   { (Invoke-Git -GitArgs @("rev-parse","--abbrev-ref","HEAD") -Quiet).Trim() }
function Get-Head     { (Invoke-Git -GitArgs @("rev-parse","HEAD") -Quiet).Trim() }

function Ensure-Remote {
  Invoke-Git -GitArgs @("remote","get-url",$Remote) -AllowFail -Quiet | Out-Null
  if($LASTEXITCODE -ne 0){
    $list = (Invoke-Git -GitArgs @("remote") -Quiet).Trim()
    throw "❌ Remote '$Remote' non esiste. Remote disponibili:`n$list"
  }
}

function Tag-ExistsLocal([string]$tag){
  if([string]::IsNullOrWhiteSpace($tag)) { return $false }
  Invoke-Git -GitArgs @("show-ref","--tags","--quiet","--verify","refs/tags/$tag") -AllowFail -Quiet | Out-Null
  return ($LASTEXITCODE -eq 0)
}

function Delete-TagEverywhere([string]$tag){
  if(Tag-ExistsLocal $tag){
    Invoke-Git -GitArgs @("tag","-d",$tag) | Out-Null
  }
  Invoke-Git -GitArgs @("push",$Remote,":refs/tags/$tag") -AllowFail | Out-Null
}

function Push-BranchUpstreamIfNeeded([string]$branch){
  Invoke-Git -GitArgs @("push") -AllowFail | Out-Null
  if($LASTEXITCODE -ne 0){
    Invoke-Git -GitArgs @("push","-u",$Remote,$branch) | Out-Null
  }
}

function Get-RemoteTagInfo([string]$tag){
  if($DryRun){
    return [pscustomobject]@{ Exists=$false; IsAnnotated=$false; TargetCommit=""; Unknown=$true; Raw="" }
  }

  $raw = Invoke-Git -GitArgs @("ls-remote","--tags",$Remote,$tag) -AllowFail -Quiet
  $raw = ($raw | Out-String).Trim()

  if([string]::IsNullOrWhiteSpace($raw)){
    return [pscustomobject]@{ Exists=$false; IsAnnotated=$false; TargetCommit=""; Unknown=$false; Raw="" }
  }

  $lines = $raw -split "`r?`n"
  $annot = $lines | Where-Object { $_ -match "\^\{\}$" } | Select-Object -First 1
  if($annot){
    $sha = ($annot -split "\s+")[0]
    return [pscustomobject]@{ Exists=$true; IsAnnotated=$true; TargetCommit=$sha; Unknown=$false; Raw=$raw }
  }

  $sha2 = (($lines | Select-Object -First 1) -split "\s+")[0]
  return [pscustomobject]@{ Exists=$true; IsAnnotated=$false; TargetCommit=$sha2; Unknown=$false; Raw=$raw }
}

function Find-AltTag([string]$baseTag){
  for($i=2; $i -le 99; $i++){
    $alt = "{0}-{1:00}" -f $baseTag, $i
    $rt = Get-RemoteTagInfo $alt
    if(-not $rt.Exists){ return $alt }
  }
  throw "❌ Nessun tag alternativo libero per: $baseTag (fino a -99)."
}

function Ensure-TagAnnotated([string]$tag){
  $head = Get-Head
  if([string]::IsNullOrWhiteSpace($head)){
    throw "❌ HEAD vuoto: rev-parse HEAD fallito."
  }

  $rt = Get-RemoteTagInfo $tag

  if($rt.Unknown){
    Delete-TagEverywhere $tag
    Invoke-Git -GitArgs @("tag","-a",$tag,$head,"-m","Savepoint $tag") | Out-Null
    Invoke-Git -GitArgs @("push",$Remote,$tag) | Out-Null
    return $tag
  }

  if($rt.Exists -and $rt.IsAnnotated -and ($rt.TargetCommit -eq $head)){
    Write-Host "ℹ️ Tag remoto già OK (annotated) su HEAD: $tag" -ForegroundColor DarkGray
    if(Tag-ExistsLocal $tag){ Invoke-Git -GitArgs @("tag","-d",$tag) | Out-Null }
    Invoke-Git -GitArgs @("tag","-a",$tag,$head,"-m","Savepoint $tag") | Out-Null
    return $tag
  }

  Delete-TagEverywhere $tag

  $rt2 = Get-RemoteTagInfo $tag
  if($rt2.Exists){
    $alt = Find-AltTag $tag
    Write-Host "⚠️ Tag remoto '$tag' protetto. Fallback: $alt" -ForegroundColor Yellow
    Invoke-Git -GitArgs @("tag","-a",$alt,$head,"-m","Savepoint $alt") | Out-Null
    Invoke-Git -GitArgs @("push",$Remote,$alt) | Out-Null
    return $alt
  }

  Invoke-Git -GitArgs @("tag","-a",$tag,$head,"-m","Savepoint $tag") | Out-Null
  Invoke-Git -GitArgs @("push",$Remote,$tag) | Out-Null
  return $tag
}

function Run-Cronista([string]$date){
  if(-not $Cronista){ return }

  $dated   = Join-Path $CronistaDir ("cronista_salva_giornata_{0}.ps1" -f $date)
  $generic = Join-Path $CronistaDir "cronista_salva_giornata.ps1"

  if(Test-Path -LiteralPath $dated){
    Write-Host "📝 Cronista: $dated" -ForegroundColor Cyan
    if($DryRun){ Write-Host "🟡 DRYRUN powershell -File $dated" -ForegroundColor Yellow; return }
    powershell -ExecutionPolicy Bypass -File $dated
    return
  }

  if(Test-Path -LiteralPath $generic){
    Write-Host "📝 Cronista: $generic" -ForegroundColor Cyan
    if($DryRun){ Write-Host "🟡 DRYRUN powershell -File $generic" -ForegroundColor Yellow; return }
    powershell -ExecutionPolicy Bypass -File $generic
    return
  }

  Write-Host "⚠️ Cronista richiesto ma non trovato in: $CronistaDir" -ForegroundColor Yellow
}

function Normalize-Slug([string]$name){
  $slug = $name.ToLower() -replace '[^a-z0-9\-]+','-'
  $slug = $slug -replace '-{2,}','-'
  $slug = $slug.Trim('-')
  if([string]::IsNullOrWhiteSpace($slug)){ throw "Slug vuoto: scegli un nome valido." }
  return $slug
}

function Get-BranchTagSuffix([string]$branch){
  if([string]::IsNullOrWhiteSpace($branch)){ return "" }
  $b = $branch.ToLower()
  $b = $b -replace '^refs/heads/',''
  $b = $b -replace '[/\\]+','-'
  $b = $b -replace '[^a-z0-9\-]+','-'
  $b = $b -replace '-{2,}','-'
  return $b.Trim('-')
}

function Commit-WithHookRetry {
  param(
    [Parameter(Mandatory=$true)][string]$Message,
    [switch]$AllowEmpty
  )

  $args = @("commit")
  if($AllowEmpty){ $args += "--allow-empty" }
  $args += @("-m",$Message)

  $out = Invoke-Git -GitArgs $args -AllowFail
  if($LASTEXITCODE -eq 0){ return }

  $maybeFixed =
    ($out -match "fixed mixed line endings") -or
    ($out -match "files were modified") -or
    ($out -match "auto-fix") -or
    ($out -match "hook id:") -or
    ($out -match "Normalize line endings") -or
    ($out -match "mixed-line-ending")

  if($maybeFixed){
    Write-Host "♻️ Hook ha auto-fixato file: ristage + retry commit..." -ForegroundColor Yellow
    Invoke-Git -GitArgs @("add","-A") | Out-Null

    $out2 = Invoke-Git -GitArgs $args -AllowFail
    if($LASTEXITCODE -eq 0){ return }

    if(($out2 -match "nothing to commit") -or ($out2 -match "nothing added to commit")){
      $st = (Invoke-Git -GitArgs @("status","--porcelain") -Quiet)
      if($st.Length -eq 0){ return }
    }

    throw "❌ git commit (retry) FAILED (exit=$LASTEXITCODE)`n$out2"
  }

  throw "❌ git commit FAILED (exit=$LASTEXITCODE)`n$out"
}

function Do-Savepoint {
  Ensure-GitRepo
  Ensure-Remote

  $branch = Get-Branch
  if([string]::IsNullOrWhiteSpace($branch)){ throw "❌ Branch vuoto: rev-parse --abbrev-ref HEAD fallito." }
  Write-Host "🧭 Branch: $branch" -ForegroundColor Cyan

  Invoke-Git -GitArgs @("fetch","--all","--prune","--tags") | Out-Null

  $status = (Invoke-Git -GitArgs @("status","--porcelain") -Quiet)
  $date = Get-Date -Format "yyyy-MM-dd"

  if($status.Length -gt 0){
    Write-Host "🧩 Modifiche trovate: commit snapshot." -ForegroundColor Cyan
    Invoke-Git -GitArgs @("add","-A") | Out-Null
    Commit-WithHookRetry -Message "chore(savepoint): snapshot $date"
  } else {
    Write-Host "ℹ️ Nessuna modifica locale: solo push/tag." -ForegroundColor DarkGray
  }

  Push-BranchUpstreamIfNeeded $branch

  $tagBase = "Snapshot-OK-$date"
  $tag = $tagBase

  if($branch -ne $BaseBranch){
    $suffix = Get-BranchTagSuffix $branch
    if(-not [string]::IsNullOrWhiteSpace($suffix)){
      $tag = "$tagBase-$suffix"
    }
  }

  $usedTag = Ensure-TagAnnotated $tag

  Write-Host "✅ Savepoint completato su '$branch' + tag $usedTag" -ForegroundColor Green
  Run-Cronista $date
}

function Do-Align {
  Ensure-GitRepo
  Ensure-Remote

  $dirty = (Invoke-Git -GitArgs @("status","--porcelain") -Quiet)
  if($dirty.Length -gt 0){
    $msg = "Working tree non pulita. Fai Savepoint o stash prima di Align."
    if($DryRun){
      Write-Host "⚠️ DRYRUN: $msg" -ForegroundColor Yellow
      return
    }
    throw "❌ $msg"
  }

  Invoke-Git -GitArgs @("fetch","--all","--prune","--tags") | Out-Null
  Invoke-Git -GitArgs @("--no-pager","log","--oneline","--graph","--decorate","-n","12") | Out-Null

  $branch = Get-Branch
  if([string]::IsNullOrWhiteSpace($branch)){ throw "❌ Branch vuoto: rev-parse --abbrev-ref HEAD fallito." }
  $up = "$Remote/$branch"

  Write-Host "ℹ️ Rebase su $up" -ForegroundColor Cyan
  Write-Host "ℹ️ Se conflitti: risolvi, poi 'git rebase --continue'." -ForegroundColor DarkGray
  Write-Host "ℹ️ Poi: 'git push --force-with-lease' (solo se necessario)." -ForegroundColor DarkGray

  Invoke-Git -GitArgs @("rebase",$up) | Out-Null
}

function New-Feature([string]$name) {
  Ensure-GitRepo
  Ensure-Remote

  if([string]::IsNullOrWhiteSpace($name)){ throw "Fornisci un nome: -Feature <slug>" }
  $slug = Normalize-Slug $name
  $branch = "feat/$slug"

  Invoke-Git -GitArgs @("fetch","--all","--prune","--tags") | Out-Null

  if(-not $FromCurrent){
    Invoke-Git -GitArgs @("checkout",$BaseBranch) | Out-Null
    Invoke-Git -GitArgs @("pull","--rebase",$Remote,$BaseBranch) | Out-Null
  }

  Invoke-Git -GitArgs @("checkout","-b",$branch) | Out-Null
  Commit-WithHookRetry -Message "chore: start $branch" -AllowEmpty
  Invoke-Git -GitArgs @("push","-u",$Remote,$branch) | Out-Null

  Write-Host "🌿 Branch creato: $branch" -ForegroundColor Green
}

function New-Hotfix([string]$name) {
  Ensure-GitRepo
  Ensure-Remote

  if([string]::IsNullOrWhiteSpace($name)){ throw "Fornisci un nome: -Hotfix <slug>" }
  $slug = Normalize-Slug $name
  $branch = "hotfix/$slug"

  Invoke-Git -GitArgs @("fetch","--all","--prune","--tags") | Out-Null

  if(-not $FromCurrent){
    Invoke-Git -GitArgs @("checkout",$BaseBranch) | Out-Null
    Invoke-Git -GitArgs @("pull","--rebase",$Remote,$BaseBranch) | Out-Null
  }

  Invoke-Git -GitArgs @("checkout","-b",$branch) | Out-Null
  Commit-WithHookRetry -Message "chore: start $branch" -AllowEmpty
  Invoke-Git -GitArgs @("push","-u",$Remote,$branch) | Out-Null

  $date = Get-Date -Format "yyyy-MM-dd"
  $tagBase = "Snapshot-OK-$date-hotfix"
  $tag = $tagBase

  if($branch -ne $BaseBranch){
    $suffix = Get-BranchTagSuffix $branch
    if(-not [string]::IsNullOrWhiteSpace($suffix)){
      $tag = "$tagBase-$suffix"
    }
  }

  $usedTag = Ensure-TagAnnotated $tag

  Write-Host "🚑 Hotfix creato: $branch + tag $usedTag" -ForegroundColor Green
  Run-Cronista $date
}

function Do-Doctor {
  Ensure-GitRepo

  $root = Get-RepoRoot
  $branch = Get-Branch
  $head = Get-Head
  $dirty = (Invoke-Git -GitArgs @("status","--porcelain") -Quiet)

  Write-Host "=== DOCTOR ===" -ForegroundColor Cyan
  Write-Host "Repo:   $root"
  Write-Host "Branch: $branch"
  Write-Host "HEAD:   $head"
  Write-Host ("Dirty:  " + ($(if($dirty.Length -gt 0){"SI"}else{"NO"})))

  try {
    Ensure-Remote
    $url = (Invoke-Git -GitArgs @("remote","get-url",$Remote) -Quiet).Trim()
    if($url){ Write-Host "Remote: $Remote -> $url" }
  } catch {}

  Invoke-Git -GitArgs @("--no-pager","log","-1","--oneline","--decorate") | Out-Null
}

switch ($PSCmdlet.ParameterSetName) {
  "Savepoint" { Do-Savepoint; break }
  "Align"     { Do-Align;     break }
  "Feature"   { New-Feature $Feature; break }
  "Hotfix"    { New-Hotfix  $Hotfix;  break }
  "Doctor"    { Do-Doctor;   break }
  default     { Show-Usage;  break }
}
