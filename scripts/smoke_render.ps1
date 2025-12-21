param(
  [Parameter(Mandatory=$true)]
  [string]$Url,

  [int]$Attempts = 10,
  [int]$TimeoutSec = 45,
  [int]$RetryDelaySec = 6
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Date e path report (SEMPE in E:\CLONAZIONE\REPORT_DELTA\...)
$today = Get-Date -Format "yyyy-MM-dd"
$reportDir = "E:\CLONAZIONE\REPORT_DELTA"
$reportPath = Join-Path $reportDir ("RENDER_PROVE_{0}.txt" -f $today)

if (!(Test-Path $reportDir)) {
  New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

function Add-Line([string]$line) {
  $line | Out-File -FilePath $reportPath -Encoding UTF8 -Append
}

Add-Line ("=" * 90)
Add-Line ("RENDER SMOKE TEST  |  {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
Add-Line ("URL={0}" -f $Url)
Add-Line ("Attempts={0} TimeoutSec={1} RetryDelaySec={2}" -f $Attempts, $TimeoutSec, $RetryDelaySec)
Add-Line ("ReportPath={0}" -f $reportPath)
Add-Line ("=" * 90)

for ($i = 1; $i -le $Attempts; $i++) {
  $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  $sw = [System.Diagnostics.Stopwatch]::StartNew()

  try {
    # GET (NON HEAD) + timeout
    $resp = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec $TimeoutSec -UseBasicParsing
    $sw.Stop()

    $code = [int]$resp.StatusCode
    $len  = 0
    if ($null -ne $resp.Content) { $len = $resp.Content.Length }

    $preview = ""
    if ($null -ne $resp.Content -and $resp.Content.Length -gt 0) {
      $preview = $resp.Content.Substring(0, [Math]::Min(180, $resp.Content.Length)).Replace("`r"," ").Replace("`n"," ")
    }

    Add-Line ("[{0}] TRY {1}/{2}  OK  HTTP={3}  ms={4}  bytes={5}  preview='{6}'" -f $ts, $i, $Attempts, $code, $sw.ElapsedMilliseconds, $len, $preview)
    Start-Sleep -Seconds 1
  }
  catch {
    $sw.Stop()
    $msg = $_.Exception.Message.Replace("`r"," ").Replace("`n"," ")
    Add-Line ("[{0}] TRY {1}/{2}  KO  ms={3}  err='{4}'" -f $ts, $i, $Attempts, $sw.ElapsedMilliseconds, $msg)

    # Retry delay (cold start Render) — backoff leggero
    Start-Sleep -Seconds ($RetryDelaySec + [Math]::Min(12, $i))
  }
}

Add-Line ("DONE | {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
Add-Line ("=" * 90)

Write-Host "OK: report scritto in $reportPath"
