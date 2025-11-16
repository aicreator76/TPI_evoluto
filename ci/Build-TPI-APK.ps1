param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectRoot,
    [Parameter(Mandatory=$true)]
    [string]$ReleaseRoot,
    [Parameter(Mandatory=$true)]
    [string]$Date,
    [Parameter(Mandatory=$true)]
    [string]$Version
)

Write-Host "=== Build-TPI-APK ==="
Write-Host "ProjectRoot = $ProjectRoot"
Write-Host "ReleaseRoot = $ReleaseRoot"
Write-Host "Date        = $Date"
Write-Host "Version     = $Version"

# Cartella output: RELEASE_TPI\<DATA>\ANDROID
$apkOut = Join-Path $ReleaseRoot (Join-Path $Date "ANDROID")
New-Item -ItemType Directory -Path $apkOut -Force | Out-Null

# Per ora: artefatto placeholder (da sostituire con build reale Flutter/Android)
$apkName = "Camelot_TPI_{0}-ANDROID.apk" -f $Version
$apkPath = Join-Path $apkOut $apkName

"Placeholder build Android per TPI (ver. $Version, data $Date)" | Set-Content -Path $apkPath -Encoding UTF8

Write-Host "Creato artefatto APK placeholder: $apkPath"
