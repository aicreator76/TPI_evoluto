Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repo = "E:\CLONAZIONE\tpi_evoluto"
$releaseRoot = "E:\CLONAZIONE\RELEASE_TPI"
$logRoot = "E:\CLONAZIONE\LOG\BUILD"

$ts = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$day = Get-Date -Format "yyyy-MM-dd"

New-Item -ItemType Directory -Force -Path $releaseRoot | Out-Null
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null

$relDir = Join-Path $releaseRoot $day
New-Item -ItemType Directory -Force -Path $relDir | Out-Null

$log = Join-Path $logRoot "CESARE_BUILD_TPI_APK_$ts.txt"

"=== CESARE_BUILD_TPI_APK START $ts ===" | Tee-Object -FilePath $log
"REPO    : $repo" | Tee-Object -FilePath $log -Append
"RELEASE : $relDir" | Tee-Object -FilePath $log -Append
"" | Tee-Object -FilePath $log -Append

# === OUTPUT FILES (2 file richiesti) ===
$apkOut = Join-Path $relDir ("TPI_demo_APK_" + $ts + ".apk")
$apkSha = $apkOut + ".sha256"

"APK_OUT : $apkOut" | Tee-Object -FilePath $log -Append
"APK_SHA : $apkSha" | Tee-Object -FilePath $log -Append
"" | Tee-Object -FilePath $log -Append

"--- CREATE APK PLACEHOLDER ---" | Tee-Object -FilePath $log -Append

$apkPayload = @"
TPI APK PLACEHOLDER
TIME=$ts
NOTE=Pipeline APK non configurata. Questo file serve come artefatto temporaneo.
REPO=$repo
"@

$apkPayload | Out-File -FilePath $apkOut -Encoding ascii

"--- SHA256 ---" | Tee-Object -FilePath $log -Append
certutil -hashfile "$apkOut" SHA256 | Tee-Object -FilePath $log -Append | Out-Null

$hashLine = (certutil -hashfile "$apkOut" SHA256 | Select-String -Pattern "^[0-9a-fA-F]{64}$").Line
if (-not $hashLine) { throw "SHA256 non estratto: controlla output certutil nel log: $log" }
$hashLine | Out-File -FilePath $apkSha -Encoding ascii

$report = Join-Path $relDir ("BUILD_REPORT_APK_" + $ts + ".txt")
@"
OK APK STUB (artefatti creati)
TIME   : $ts
REPO   : $repo
RELEASE: $relDir
APK    : $apkOut
SHA256 : $apkSha
LOG    : $log
"@ | Out-File -FilePath $report -Encoding utf8

"OK: REPORT $report" | Tee-Object -FilePath $log -Append
"=== CESARE_BUILD_TPI_APK END ===" | Tee-Object -FilePath $log -Append

Write-Host "OK APK stub creato."
Write-Host "APK   :" $apkOut
Write-Host "SHA256:" $apkSha
Write-Host "LOG   :" $log
exit 0
