param(
  [Parameter(Mandatory=$true)][string]$Url,
  [int]$Attempts = 12,
  [int]$TimeoutSec = 45,
  [int]$RetryDelaySec = 6
)

$ErrorActionPreference = "Stop"

$today = Get-Date -Format "yyyy-MM-dd"
$reportDir = "E:\CLONAZIONE\REPORT_DELTA"
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null
$reportPath = Join-Path $reportDir ("RENDER_PROVE_{0}.txt" -f $today)

# UTF-8 senza BOM (compatibile anche con PowerShell vecchio)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)

function Add-Line([string]$line) {
  [System.IO.File]::AppendAllText($reportPath, $line + "`r`n", $utf8NoBom)
}

function Get-Code([string]$u) {
  for($i=1; $i -le $Attempts; $i++){
    try{
      $sw = [System.Diagnostics.Stopwatch]::StartNew()
      $r  = Invoke-WebRequest -Uri $u -Method GET -TimeoutSec $TimeoutSec -UseBasicParsing
      $sw.Stop()
      return @{ ok=$true; code=[int]$r.StatusCode; ms=$sw.ElapsedMilliseconds }
    } catch {
      $msg = $_.Exception.Message.Split("`n")[0]
      Add-Line ("TRY {0}/{1} KO | {2} | {3}" -f $i,$Attempts,$u,$msg)
      if($i -lt $Attempts){ Start-Sleep -Seconds $RetryDelaySec } else { return @{ ok=$false; code=0; ms=0 } }
    }
  }
}

# calcola base (host) a partire da Url
$uObj = [Uri]$Url
$base = "{0}://{1}" -f $uObj.Scheme, $uObj.Host
if($uObj.Port -and ($uObj.Port -ne 80) -and ($uObj.Port -ne 443)) { $base = "{0}:{1}" -f $base, $uObj.Port }

# ricrea report del giorno in modo PULITO (no append di roba vecchia)
[System.IO.File]::WriteAllText($reportPath, "", $utf8NoBom)

Add-Line ("=== TS {0} ===" -f (Get-Date -Format "yyyy-MM-ddTHH:mm:ss"))
Add-Line ("base={0}" -f $base)

$checks = @(
  @{ key="healthz";    url="$base/healthz" },
  @{ key="demo";       url="$base/api/demo/products" },
  @{ key="linee_vita"; url="$base/api/linee-vita/products" },
  @{ key="inox";       url="$base/api/inox/products" },
  @{ key="openapi";    url="$base/openapi.json" }
)

foreach($c in $checks){
  $res = Get-Code $c.url
  if($res.ok){ Add-Line ("{0}={1} ms={2}" -f $c.key,$res.code,$res.ms) }
  else { Add-Line ("{0}=KO" -f $c.key) }
}

# lv_code
try {
  $lv = Invoke-RestMethod -Uri "$base/api/linee-vita/products" -Method GET -TimeoutSec $TimeoutSec
  $lvCode = $null
  if($lv -and $lv.items -and $lv.items.Count -gt 0){ $lvCode = $lv.items[0].code }
  if($lvCode){
    $res = Get-Code "$base/api/linee-vita/products/$lvCode"
    if($res.ok){ Add-Line ("lv_code={0} code={1} ms={2}" -f $res.code,$lvCode,$res.ms) } else { Add-Line ("lv_code=KO code={0}" -f $lvCode) }
  } else { Add-Line "lv_code=SKIP (no items)" }
} catch { Add-Line ("lv_code=ERR {0}" -f $_.Exception.Message.Split("`n")[0]) }

# inox_code
try {
  $ix = Invoke-RestMethod -Uri "$base/api/inox/products" -Method GET -TimeoutSec $TimeoutSec
  $ixCode = $null
  if($ix -and $ix.items -and $ix.items.Count -gt 0){ $ixCode = $ix.items[0].code }
  if($ixCode){
    $res = Get-Code "$base/api/inox/products/$ixCode"
    if($res.ok){ Add-Line ("inox_code={0} code={1} ms={2}" -f $res.code,$ixCode,$res.ms) } else { Add-Line ("inox_code=KO code={0}" -f $ixCode) }
  } else { Add-Line "inox_code=SKIP (no items)" }
} catch { Add-Line ("inox_code=ERR {0}" -f $_.Exception.Message.Split("`n")[0]) }

# openapi summary (NO mega-json in report)
try {
  $spec = Invoke-RestMethod -Uri "$base/openapi.json" -Method GET -TimeoutSec $TimeoutSec
  $pathsCount = 0
  if($spec -and $spec.paths){ $pathsCount = $spec.paths.PSObject.Properties.Name.Count }
  Add-Line ("openapi_title={0}" -f $spec.info.title)
  Add-Line ("openapi_version={0}" -f $spec.info.version)
  Add-Line ("openapi_paths_count={0}" -f $pathsCount)
} catch { Add-Line ("openapi_parse=ERR {0}" -f $_.Exception.Message.Split("`n")[0]) }

Add-Line ("DONE {0}" -f (Get-Date -Format "yyyy-MM-ddTHH:mm:ss"))

Write-Host ("OK: report scritto in {0}" -f $reportPath)
