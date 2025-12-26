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

$log = Join-Path $logRoot ("CESARE_BUILD_TPI_WIN_" + $ts + ".txt")

"=== CESARE_BUILD_TPI_WIN START $ts ===" | Tee-Object -FilePath $log
"REPO    : $repo" | Tee-Object -FilePath $log -Append
"RELEASE : $relDir" | Tee-Object -FilePath $log -Append
"" | Tee-Object -FilePath $log -Append

# === OUTPUT FILES (2 file richiesti) ===
$exeOut = Join-Path $relDir ("TPI_demo_WIN_" + $ts + ".exe")
$exeSha = $exeOut + ".sha256"

"EXE_OUT : $exeOut" | Tee-Object -FilePath $log -Append
"EXE_SHA : $exeSha" | Tee-Object -FilePath $log -Append
"" | Tee-Object -FilePath $log -Append

"--- CREATE EXE PLACEHOLDER ---" | Tee-Object -FilePath $log -Append

# Stub binario “finto” ma valido come file (non eseguibile reale)
$payload = @"
TPI WIN EXE PLACEHOLDER
TIME=$ts
NOTE=Pipeline WIN non configurata. Questo file serve come artefatto temporaneo.
REPO=$repo
"@

# Scrivo bytes (così non hai problemi di encoding)
[System.IO.File]::WriteAllBytes($exeOut, [System.Text.Encoding]::ASCII.GetBytes($payload))

"--- SHA256 ---" | Tee-Object -FilePath $log -Append
certutil -hashfile "$exeOut" SHA256 | Tee-Object -FilePath $log -Append | Out-Null

$hashLine = (certutil -hashfile "$exeOut" SHA256 | Select-String -Pattern "^[0-9a-fA-F]{64}$").Line
if (-not $hashLine) { throw "SHA256 non estratto: controlla output certutil nel log: $log" }
$hashLine | Out-File -FilePath $exeSha -Encoding ascii

$report = Join-Path $relDir ("BUILD_REPORT_WIN_" + $ts + ".txt")
@"
OK WIN STUB (artefatti creati)
TIME   : $ts
REPO   : $repo
RELEASE: $relDir
EXE    : $exeOut
SHA256 : $exeSha
LOG    : $log
"@ | Out-File -FilePath $report -Encoding utf8

"OK: REPORT $report" | Tee-Object -FilePath $log -Append
"=== CESARE_BUILD_TPI_WIN END ===" | Tee-Object -FilePath $log -Append

Write-Host "OK WIN stub creato."
Write-Host "EXE   :" $exeOut
Write-Host "SHA256:" $exeSha
Write-Host "LOG   :" $log
exit 0
