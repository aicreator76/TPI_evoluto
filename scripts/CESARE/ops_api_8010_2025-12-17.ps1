param(
  [string]$Repo      = "E:\CLONAZIONE\tpi_evoluto",
  [int]   $Port      = 8010,
  [string]$Bind      = "127.0.0.1",
  [ValidateSet("MENU","RUN","SMOKE","HOTRELOAD","TAIL","STOP","STATUS")]
  [string]$Action    = "MENU"
)

$ErrorActionPreference = "Stop"
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)

$logDir = "E:\CLONAZIONE\LOG"
$bkDir  = "E:\CLONAZIONE\BACKUP_EMERGENZA"
$ts     = (Get-Date).ToString("yyyy-MM-dd_HH-mm-ss")
$base   = "http://$Bind`:$Port"

$lastMeta = Join-Path $logDir ("uvicorn_{0}_LAST.txt" -f $Port)

function Ensure-Dirs {
  New-Item -ItemType Directory -Force -Path $logDir,$bkDir,(Join-Path $Repo "app\data") | Out-Null
}

function Get-ListenerPid {
  try {
    $c = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop | Select-Object -First 1
    if($c){ return [int]$c.OwningProcess }
  } catch {}
  return $null
}

function Stop-Api {
  $pid = Get-ListenerPid
  if(-not $pid){
    Write-Host "STOP_OK NO_LISTENER_$Port"
    return
  }
  Stop-Process -Id $pid -Force
  Start-Sleep -Milliseconds 300
  Write-Host "STOP_OK pid=$pid"
}

function Start-Api {
  Ensure-Dirs

  # Prefer venv python if exists
  $pyVenv = Join-Path $Repo ".venv\Scripts\python.exe"
  if (Test-Path $pyVenv) { $py = $pyVenv } else { $py = "python" }


  $outLog = Join-Path $logDir ("uvicorn_{0}_{1}.out.log" -f $Port,$ts)
  $errLog = Join-Path $logDir ("uvicorn_{0}_{1}.err.log" -f $Port,$ts)

  # Force UTF-8 for python logs too
  $env:PYTHONUTF8 = "1"

  $args = @("-m","uvicorn","app.main:app","--host",$Bind,"--port",$Port,"--reload","--reload-dir",$Repo)

  $p = Start-Process -FilePath $py -ArgumentList $args -WorkingDirectory $Repo `
        -RedirectStandardOutput $outLog -RedirectStandardError $errLog -PassThru

  @"
TS=$ts
PID=$($p.Id)
REPO=$Repo
BASE=$base
OUT=$outLog
ERR=$errLog
"@ | Set-Content -Encoding utf8 $lastMeta

  Write-Host "RUN_OK pid=$($p.Id) out=$outLog err=$errLog meta=$lastMeta"
}

function Wait-Ready {
  $deadline = (Get-Date).AddSeconds(20)
  $urls = @("$base/healthz", "$base/health", "$base/api/ops/healthz")
  while((Get-Date) -lt $deadline){
    foreach($u in $urls){
      try {
        $r = Invoke-WebRequest $u -UseBasicParsing -TimeoutSec 2
        if($r.StatusCode -eq 200){ return $true }
      } catch {}
    }
    Start-Sleep -Milliseconds 300
  }
  return $false
}

function Smoke {
  $open = (curl.exe -s -o NUL -w "%{http_code}" "$base/openapi.json")
  $docs = (curl.exe -s -o NUL -w "%{http_code}" "$base/docs")
  $api  = (curl.exe -s -o NUL -w "%{http_code}" "$base/api/demo/products")
  $mir  = (curl.exe -s -o NUL -w "%{http_code}" "$base/demo/products")
  Write-Host "SMOKE openapi=$open docs=$docs api_demo=$api demo=$mir"

  if($api -eq "200"){
    Invoke-RestMethod "$base/api/demo/products" | ConvertTo-Json -Depth 8
  } elseif($mir -eq "200"){
    Invoke-RestMethod "$base/demo/products" | ConvertTo-Json -Depth 8
  } else {
    Write-Host "SMOKE_FAIL -> usa TAIL (vedi log) : $lastMeta"
  }
}

function Tail {
  if(Test-Path $lastMeta){
    $m = Get-Content $lastMeta -ErrorAction SilentlyContinue
    $out = ($m | Where-Object { $_ -like "OUT=*" }) -replace "^OUT=",""
    $err = ($m | Where-Object { $_ -like "ERR=*" }) -replace "^ERR=",""
    Write-Host "TAIL_META -> $lastMeta"
    if(Test-Path $err){ Write-Host "---- ERR (tail 120) ----"; Get-Content $err -Tail 120 }
    else { Write-Host "ERR_LOG_NOT_FOUND -> $err" }
    if(Test-Path $out){ Write-Host "---- OUT (tail 80) ----"; Get-Content $out -Tail 80 }
    else { Write-Host "OUT_LOG_NOT_FOUND -> $out" }
    return
  }

  $latest = Get-ChildItem $logDir -Filter ("uvicorn_{0}_*.err.log" -f $Port) -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Desc | Select-Object -First 1
  if($latest){
    Write-Host "TAIL_LATEST -> $($latest.FullName)"
    Get-Content $latest.FullName -Tail 160
  } else {
    Write-Host "TAIL_FAIL -> nessun log trovato in $logDir"
  }
}

function HotReload {
  Ensure-Dirs
  $data = Join-Path $Repo "app\data\demo_products.json"
  if(-not (Test-Path $data)){
    Write-Host "HOTRELOAD_FAIL data_missing=$data"
    return
  }

  $bk = Join-Path $bkDir ("HOTRELOAD_DEMO_{0}" -f $ts)
  New-Item -ItemType Directory -Force -Path $bk | Out-Null
  Copy-Item $data (Join-Path $bk "demo_products.json") -Force

  $json = Get-Content $data -Raw -Encoding utf8 | ConvertFrom-Json
  if($json.Count -gt 0){
    if(-not $json[0].tags){ $json[0] | Add-Member -NotePropertyName tags -NotePropertyValue @() }
    $json[0].tags += ("hotreload-{0}" -f $ts)
  }
  ($json | ConvertTo-Json -Depth 12) | Set-Content -Encoding utf8 $data

  Start-Sleep -Milliseconds 500
  Write-Host "HOTRELOAD_PATCHED data=$data backup=$bk"

  Smoke

  # restore
  Copy-Item (Join-Path $bk "demo_products.json") $data -Force
  Write-Host "HOTRELOAD_RESTORE_OK data=$data"
}

function Status {
  $pid = Get-ListenerPid
  if($pid){ Write-Host "STATUS LISTEN_$Port pid=$pid base=$base" }
  else { Write-Host "STATUS NO_LISTENER_$Port base=$base" }
  if(Test-Path $lastMeta){ Write-Host "META -> $lastMeta" }
}

function Menu {
  Write-Host ""
  Write-Host "OPS API $Port  ($Repo)"
  Write-Host "1 RUN   2 SMOKE   3 HOTRELOAD   4 TAIL   5 STOP   6 STATUS   0 EXIT"
  $k = Read-Host "Scelta"
  switch($k){
    "1" { Start-Api; Start-Sleep -Seconds 1; if(-not (Wait-Ready)){ Write-Host "READY_FAIL"; Tail }; Smoke }
    "2" { Smoke }
    "3" { HotReload }
    "4" { Tail }
    "5" { Stop-Api }
    "6" { Status }
    default { return }
  }
  Menu
}

# DISPATCH
switch($Action){
  "RUN"      { Start-Api; Start-Sleep -Seconds 1; if(-not (Wait-Ready)){ Write-Host "READY_FAIL"; Tail }; Smoke }
  "SMOKE"    { Smoke }
  "HOTRELOAD"{ HotReload }
  "TAIL"     { Tail }
  "STOP"     { Stop-Api }
  "STATUS"   { Status }
  default    { Menu }
}
