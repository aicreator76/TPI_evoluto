param(
  [string]$BaseUrl = "http://127.0.0.1:8000",
  [string]$TmpCsv  = ".\_tmp_catalogo.csv"
)

function Use-Curl {
  return (Get-Command curl.exe -ErrorAction SilentlyContinue) -ne $null
}

function Remove-Aliases {
  Remove-Item alias:curl -ErrorAction SilentlyContinue
  Remove-Item alias:wget -ErrorAction SilentlyContinue
}

function New-SampleCsv {
  @"
codice,descrizione,gruppo,nota
DPI001,Casco base,HSE,ok
DPI002,Imbracatura,OPS,ok
"@ | Set-Content -Path $TmpCsv -Encoding UTF8
}

Write-Host "== TPI quick tests ==" -ForegroundColor Cyan
Remove-Aliases
New-SampleCsv

Write-Host "`n[1] /version" -ForegroundColor Yellow
Invoke-WebRequest -Uri "$BaseUrl/version"

Write-Host "`n[2] /healthz" -ForegroundColor Yellow
Invoke-WebRequest -Uri "$BaseUrl/healthz"

if (Use-Curl) {
  Write-Host "`n[3] import-file (curl.exe)" -ForegroundColor Yellow
  curl.exe -F "file=@$TmpCsv" "$BaseUrl/api/dpi/csv/import-file"

  Write-Host "`n[4] export HSE -> export_HSE.csv (curl.exe)" -ForegroundColor Yellow
  curl.exe -L "$BaseUrl/api/dpi/csv/export?gruppo=HSE" -o export_HSE.csv
} else {
  Write-Host "`n[3] import-file (Invoke-WebRequest)" -ForegroundColor Yellow
  $Form = @{ file = Get-Item -Path $TmpCsv; gruppo = "HSE" }
  Invoke-WebRequest -Uri "$BaseUrl/api/dpi/csv/import-file" -Method Post -Form $Form

  Write-Host "`n[4] export HSE -> export_HSE.csv (Invoke-WebRequest)" -ForegroundColor Yellow
  Invoke-WebRequest -Uri "$BaseUrl/api/dpi/csv/export?gruppo=HSE" -OutFile ".\export_HSE.csv"
}

Write-Host "`n== Done =="
