[CmdletBinding(DefaultParameterSetName = 'Help')]
param(
  # Azioni (mutuamente esclusive)
  [Parameter(ParameterSetName='Savepoint', Mandatory=$true)]
  [switch]$Savepoint,

  [Parameter(ParameterSetName='Align', Mandatory=$true)]
  [switch]$Align,

  [Parameter(ParameterSetName='Feature', Mandatory=$true)]
  [string]$Feature,

  [Parameter(ParameterSetName='Hotfix', Mandatory=$true)]
  [string]$Hotfix,

  [Parameter(ParameterSetName='Doctor', Mandatory=$true)]
  [switch]$Doctor,

  # Opzioni
  [string]$Remote = 'origin',
  [string]$BaseBranch = 'main',

  # Feature/Hotfix: parte dal branch corrente (utile se hai modifiche locali)
  [switch]$FromCurrent,

  # Cronista post-savepoint/hotfix
  [switch]$Cronista,
  [string]$CronistaDir = 'E:\CLONAZIONE\CESARE_COMANDI\scripts',

  # Sicurezza operativa
  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Normalize-GitArgs {
  param([object]$GitArgs)

  if($null -eq $GitArgs){ return [string[]]@() }

  $arr = @()

  # se è IEnumerable (ma non string), lo espandiamo
  if(($GitArgs -is [System.Collections.IEnumerable]) -and -not ($GitArgs -is [string])){
    foreach($x in $GitArgs){
      if($null -ne $x){ $arr += [string]$x }
    }
  } else {
    $arr = @([string]$GitArgs)
  }

  # elimina vuoti
  $arr = @($arr | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

  # se è UNA stringa e sembra un comando "verb ..." la splittiamo
  if($arr.Count -eq 1){
    $s = $arr[0].Trim()
    if(
      ($s -match '^(rev-parse|status|remote|show-ref|for-each-ref|rev-list|log|cat-file|diff|show|fetch|push|tag|checkout|commit|pull|rebase|add|ls-remote)\b') -and
      ($s -match '\s')
    ){
      $arr = @($s -split '\s+')
    }
  }

  return [string[]]$arr
}

function Get-GitVerb {
  param([object]$GitArgs)
  $argv = Normalize-GitArgs $GitArgs
  foreach($a in $argv){
    if(-not $a.StartsWith('-')) { return $a }
  }
  return ($argv | Select-Object -First 1)
}

function Invoke-Git {
  param(
    [Parameter(Mandatory=$true)]
    [Alias('Args')]
    [object]$GitArgs,

    [switch]$AllowFail,
    [switch]$Quiet
  )

  $argv = Normalize-GitArgs $GitArgs
  if($argv.Length -eq 0){
    throw '❌ Invoke-Git: argomenti vuoti (GitArgs).'
  }

  # SOLO LETTURA LOCALE (safe in DryRun)
  $readOnlyVerbs = @(
    'rev-parse','status','remote','show-ref','for-each-ref','rev-list',
    'log','cat-file','diff','show'
  )

  $verb = Get-GitVerb $argv

  if($DryRun){
    if($readOnlyVerbs -contains $verb){
      Write-Host ("🟡 DRYRUN-READ git " + ($argv -join ' ')) -ForegroundColor Yellow
      $raw  = & git @argv 2>&1
      $code = $LASTEXITCODE
      $out  = (($raw | Out-String).TrimEnd())

      if(-not $Quiet){ if($out) { $out } }
      if((-not $AllowFail) -and ($code -ne 0)){
        throw "❌ git $($argv -join ' ') FAILED (exit=$code)`n$out"
      }
      return $out
    }

    Write-Host ("🟡 DRYRUN git " + ($argv -join ' ')) -ForegroundColor Yellow
    $global:LASTEXITCODE = 0
    return ''
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
  $null = Invoke-Git -GitArgs @('rev-parse','--is-inside-work-tree') -AllowFail -Quiet
  if($LASTEXITCODE -ne 0){
    throw '❌ Non sei dentro una repo git. Vai in: E:\CLONAZIONE\tpi_evoluto'
  }
}

function Get-RepoRoot { (Invoke-Git -GitArgs @('rev-parse','--show-toplevel') -Quiet).Trim() }
function Get-Branch   { (Invoke-Git -GitArgs @('rev-parse','--abbrev-ref','HEAD') -Quiet).Trim() }
function Get-Head     { (Invoke-Git -GitArgs @('rev-parse','HEAD') -Quiet).Trim() }

function Ensure-Remote {
  Invoke-Git -GitArgs @('remote','get-url',$Remote) -AllowFail -Quiet | Out-Null
  if($LASTEXITCODE -ne 0){
    $list = (Invoke-Git -GitArgs @('remote') -Quiet).Trim()
    throw "❌ Remote '$Remote' non esiste. Remote disponibili:`n$list"
  }
}

function Tag-ExistsLocal {
  param([string]$tag)
  if([string]::IsNullOrWhiteSpace($tag)) { return $false }
  Invoke-Git -GitArgs @('show-ref','--tags','--quiet','--verify',"refs/tags/$tag") -AllowFail -Quiet | Out-Null
  return ($LASTEXITCODE -eq 0)
}

function Delete-TagEverywhere {
  param([string]$tag)

  if(Tag-ExistsLocal $tag){
    Invoke-Git -GitArgs @('tag','-d',$tag) | Out-Null
  }
  # best-effort remoto
  Invoke-Git -GitArgs @('push',$Remote,":refs/tags/$tag") -AllowFail | Out-Null
}

function Push-BranchUpstreamIfNeeded {
  param([string]$branch)

  Invoke-Git -GitArgs @('push') -AllowFail | Out-Null
  if($LASTEXITCODE -ne 0){
    Invoke-Git -GitArgs @('push','-u',$Remote,$branch) | Out-Null
  }
}

function Get-RemoteTagInfo {
  param([string]$tag)

  # In DryRun NON tocchiamo rete (ls-remote). Segniamo Unknown.
  if($DryRun){
    return [pscustomobject]@{
      Exists=$false; IsAnnotated=$false; TargetCommit=''; Unknown=$true; Raw=''
    }
  }

  $raw = Invoke-Git -GitArgs @('ls-remote','--tags',$Remote,$tag) -AllowFail -Quiet
  $raw = ($raw | Out-String).Trim()

  if([string]::IsNullOrWhiteSpace($raw)){
    return [pscustomobject]@{
      Exists=$false; IsAnnotated=$false; TargetCommit=''; Unknown=$false; Raw=''
    }
  }

  $lines = $raw -split "`r?`n"
  $annot = $lines | Where-Object { $_ -match "\^\{\}$" } | Select-Object -First 1
  if($annot){
    $sha = ($annot -split '\s+')[0]
    return [pscustomobject]@{
      Exists=$true; IsAnnotated=$true; TargetCommit=$sha; Unknown=$false; Raw=$raw
    }
  }

  $sha2 = (($lines | Select-Object -First 1) -split '\s+')[0]
  return [pscustomobject]@{
    Exists=$true; IsAnnotated=$false; TargetCommit=$sha2; Unknown=$false; Raw=$raw
  }
}

function Ensure-TagAnnotated {
  param([string]$tag)

  $head = Get-Head
  if([string]::IsNullOrWhiteSpace($head)){
    throw '❌ HEAD vuoto: rev-parse HEAD fallito.'
  }

  $rt = Get-RemoteTagInfo $tag

  # DryRun / Unknown: facciamo la procedura standard (stampa i comandi, non esegue)
  if($rt.Unknown){
    Delete-TagEverywhere $tag
    Invoke-Git -GitArgs @('tag','-a',$tag,$head,'-m',"Savepoint $tag") | Out-Null
    Invoke-Git -GitArgs @('push',$Remote,$tag) | Out-Null
    return
  }

  # Se remoto già annotated e punta a HEAD: ok. Ricreiamo locale annotated e stop.
  if($rt.Exists -and $rt.IsAnnotated -and ($rt.TargetCommit -eq $head)){
    Write-Host "ℹ️ Tag remoto già OK (annotated) su HEAD: $tag" -ForegroundColor DarkGray
    if(Tag-ExistsLocal $tag){ Invoke-Git -GitArgs @('tag','-d',$tag) | Out-Null }
    Invoke-Git -GitArgs @('tag','-a',$tag,$head,'-m',"Savepoint $tag") | Out-Null
    return
  }

  # Altrimenti: delete local+remote, poi ricrea/pusha
  Delete-TagEverywhere $tag

  # Se non riesce a cancellare remoto per policy, lo rileggiamo e blocchiamo
  $rt2 = Get-RemoteTagInfo $tag
  if($rt2.Exists){
    throw "❌ Impossibile sovrascrivere il tag remoto '$tag' (policy/permessi). Rimuovilo manualmente o usa suffisso (-02)."
  }

  Invoke-Git -GitArgs @('tag','-a',$tag,$head,'-m',"Savepoint $tag") | Out-Null
  Invoke-Git -GitArgs @('push',$Remote,$tag) | Out-Null
}

function Run-Cronista {
  param([string]$date)

  if(-not $Cronista){ return }

  $dated   = Join-Path $CronistaDir ("cronista_salva_giornata_{0}.ps1" -f $date)
  $generic = Join-Path $CronistaDir 'cronista_salva_giornata.ps1'

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

function Normalize-Slug {
  param([string]$name)

  $slug = $name.ToLower() -replace '[^a-z0-9\-]+','-'
  $slug = $slug -replace '-{2,}','-'
  $slug = $slug.Trim('-')

  if([string]::IsNullOrWhiteSpace($slug)){
    throw 'Slug vuoto: scegli un nome valido.'
  }
  return $slug
}

function Do-Savepoint {
  Ensure-GitRepo
  Ensure-Remote

  $branch = Get-Branch
  if([string]::IsNullOrWhiteSpace($branch)){
    throw '❌ Branch vuoto: rev-parse --abbrev-ref HEAD fallito.'
  }
  Write-Host "🧭 Branch: $branch" -ForegroundColor Cyan

  Invoke-Git -GitArgs @('fetch','--all','--prune','--tags') | Out-Null

  $status = (Invoke-Git -GitArgs @('status','--porcelain') -Quiet)
  $date = Get-Date -Format 'yyyy-MM-dd'

  if($status.Length -gt 0){
    Write-Host '🧩 Modifiche trovate: commit snapshot.' -ForegroundColor Cyan
    Invoke-Git -GitArgs @('add','-A') | Out-Null
    Invoke-Git -GitArgs @('commit','-m',"chore(savepoint): snapshot $date") | Out-Null
  } else {
    Write-Host 'ℹ️ Nessuna modifica locale: solo push/tag.' -ForegroundColor DarkGray
  }

  Push-BranchUpstreamIfNeeded $branch

  $tag = "Snapshot-OK-$date"
  Ensure-TagAnnotated $tag

  Write-Host "✅ Savepoint completato su '$branch' + tag $tag" -ForegroundColor Green
  Run-Cronista $date
}

function Do-Align {
  Ensure-GitRepo
  Ensure-Remote

  $dirty = (Invoke-Git -GitArgs @('status','--porcelain') -Quiet)
  if($dirty.Length -gt 0){
    $msg = 'Working tree non pulita. Fai Savepoint o stash prima di Align.'
    if($DryRun){
      Write-Host "⚠️ DRYRUN: $msg" -ForegroundColor Yellow
      return
    }
    throw "❌ $msg"
  }

  Invoke-Git -GitArgs @('fetch','--all','--prune','--tags') | Out-Null
  Invoke-Git -GitArgs @('--no-pager','log','--oneline','--graph','--decorate','-n','12') | Out-Null

  $branch = Get-Branch
  if([string]::IsNullOrWhiteSpace($branch)){
    throw '❌ Branch vuoto: rev-parse --abbrev-ref HEAD fallito.'
  }
  $up = "$Remote/$branch"

  Write-Host "ℹ️ Rebase su $up" -ForegroundColor Cyan
  Write-Host "ℹ️ Se conflitti: risolvi, poi 'git rebase --continue'." -ForegroundColor DarkGray
  Write-Host "ℹ️ Poi: 'git push --force-with-lease' (solo se necessario)." -ForegroundColor DarkGray

  Invoke-Git -GitArgs @('rebase',$up) | Out-Null
}

function New-Feature {
  param([string]$name)

  Ensure-GitRepo
  Ensure-Remote

  $slug = Normalize-Slug $name
  $branch = "feat/$slug"

  Invoke-Git -GitArgs @('fetch','--all','--prune','--tags') | Out-Null

  if(-not $FromCurrent){
    Invoke-Git -GitArgs @('checkout',$BaseBranch) | Out-Null
    Invoke-Git -GitArgs @('pull','--rebase',$Remote,$BaseBranch) | Out-Null
  }

  Invoke-Git -GitArgs @('checkout','-b',$branch) | Out-Null
  Invoke-Git -GitArgs @('commit','--allow-empty','-m',"chore: start $branch") | Out-Null
  Invoke-Git -GitArgs @('push','-u',$Remote,$branch) | Out-Null

  Write-Host "🌿 Branch creato: $branch" -ForegroundColor Green
}

function New-Hotfix {
  param([string]$name)

  Ensure-GitRepo
  Ensure-Remote

  $slug = Normalize-Slug $name
  $branch = "hotfix/$slug"

  Invoke-Git -GitArgs @('fetch','--all','--prune','--tags') | Out-Null

  if(-not $FromCurrent){
    Invoke-Git -GitArgs @('checkout',$BaseBranch) | Out-Null
    Invoke-Git -GitArgs @('pull','--rebase',$Remote,$BaseBranch) | Out-Null
  }

  Invoke-Git -GitArgs @('checkout','-b',$branch) | Out-Null
  Invoke-Git -GitArgs @('commit','--allow-empty','-m',"chore: start $branch") | Out-Null
  Invoke-Git -GitArgs @('push','-u',$Remote,$branch) | Out-Null

  $date = Get-Date -Format 'yyyy-MM-dd'
  $tag = "Snapshot-OK-$date-hotfix"
  Ensure-TagAnnotated $tag

  Write-Host "🚑 Hotfix creato: $branch + tag $tag" -ForegroundColor Green
  Run-Cronista $date
}

function Do-Doctor {
  Ensure-GitRepo

  $root = Get-RepoRoot
  $branch = Get-Branch
  $head = Get-Head
  $dirty = (Invoke-Git -GitArgs @('status','--porcelain') -Quiet)

  Write-Host '=== DOCTOR ===' -ForegroundColor Cyan
  Write-Host "Repo:   $root"
  Write-Host "Branch: $branch"
  Write-Host "HEAD:   $head"
  Write-Host ('Dirty:  ' + ($(if($dirty.Length -gt 0){'SI'}else{'NO'})))

  Invoke-Git -GitArgs @('--no-pager','log','-1','--oneline','--decorate') | Out-Null
}

# ROUTING
if ($Doctor)   { Do-Doctor;   exit 0 }
if ($Savepoint){ Do-Savepoint; exit 0 }
if ($Align)    { Do-Align;    exit 0 }
if ($Feature)  { New-Feature $Feature; exit 0 }
if ($Hotfix)   { New-Hotfix  $Hotfix;  exit 0 }

Write-Host @"
Usage:
  pwsh .\savepoint_workflows.ps1 -Doctor   [-DryRun]
  pwsh .\savepoint_workflows.ps1 -Savepoint [-Cronista] [-Remote origin] [-DryRun]
  pwsh .\savepoint_workflows.ps1 -Align     [-Remote origin] [-DryRun]
  pwsh .\savepoint_workflows.ps1 -Feature "nome" [-BaseBranch main] [-Remote origin] [-FromCurrent] [-DryRun]
  pwsh .\savepoint_workflows.ps1 -Hotfix  "nome" [-BaseBranch main] [-Remote origin] [-FromCurrent] [-Cronista] [-DryRun]

Note:
  - -DryRun esegue SOLO git di lettura (locale), stampa gli altri.
  - -FromCurrent crea il branch da dove sei ORA.
  - -Cronista cerca: cronista_salva_giornata_YYYY-MM-DD.ps1 poi cronista_salva_giornata.ps1
"@ -ForegroundColor Gray
