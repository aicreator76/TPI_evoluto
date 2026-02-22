param(
  [string]$Root = "E:\CLONAZIONE\REPORT_DELTA\LIBRERIA_DPI"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# =========================
# PATHS
# =========================
$Inbox        = Join-Path $Root "_INBOX"
$IndexManuali = Join-Path $Root "INDICE\MANUALI_INDEX.csv"
$IndexEvidenze= Join-Path $Root "INDICE\EVIDENZE_INDEX.csv"

New-Item -ItemType Directory -Force -Path $Inbox | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Root "INDICE") | Out-Null

# =========================
# HELPERS
# =========================
function Ensure-Index([string]$Path, [string]$Header) {
  if (!(Test-Path $Path)) { $Header | Set-Content -Encoding UTF8 $Path }
}

function CsvLine([string[]]$Fields) {
  # CSV safe con doppi apici (e rimpiazzo " interni)
  '"' + (($Fields | ForEach-Object { ($_ -replace '"','''') }) -join '","') + '"'
}

function Normalize-Slug([string]$s) {
  if ([string]::IsNullOrWhiteSpace($s)) { return "" }
  $x = $s.Trim().ToUpper()
  $x = $x -replace '\s+','_'
  $x = $x -replace '[^A-Z0-9_\-]','_'
  $x = $x -replace '_+','_'
  return $x.Trim('_')
}

function Safe-Dest([string]$dest) {
  if (!(Test-Path $dest)) { return $dest }
  $dir  = Split-Path $dest
  $base = [IO.Path]::GetFileNameWithoutExtension($dest)
  $ext  = [IO.Path]::GetExtension($dest)
  $stamp= Get-Date -Format "yyyyMMdd_HHmmss"
  return (Join-Path $dir ("{0}_DUP_{1}{2}" -f $base,$stamp,$ext))
}

function Suggest-Tipo([string]$name) {
  $n = $name.ToLowerInvariant()
  if ($n -match 'konform|conform|declaration|dichiarazione|\bce\b|doc\b|eu-?konform|konformit') { return "CE" }
  if ($n -match 'gebrauchsanleitung|manual|istruz|pru|prüfbuch|anleitung') { return "MANUALE" }
  return $null
}

function Prompt-Default([string]$label, [string]$default) {
  $v = Read-Host ("{0} [{1}]" -f $label,$default)
  if ([string]::IsNullOrWhiteSpace($v)) { return $default }
  return $v
}

function Validate-Date([string]$s) {
  # accetta YYYY-MM-DD
  if ($s -match '^\d{4}-\d{2}-\d{2}$') { return $true }
  return $false
}

# =========================
# ACTIONS
# =========================
function Add-DpiManual {
  param(
    [Parameter(Mandatory)] [string]$PdfIn,
    [Parameter(Mandatory)] [string]$Categoria,
    [Parameter(Mandatory)] [string]$Produttore,
    [Parameter(Mandatory)] [string]$Modello,
    [Parameter(Mandatory)] [string]$VersioneData,
    [ValidateSet("MODELLO","SERIE","FAMIGLIA")] [string]$ApplicabileA="MODELLO",
    [string]$Note="",
    [ValidateSet("MOVE","COPY")] [string]$Action="MOVE"
  )

  if (!(Test-Path $PdfIn)) { throw "PDF non trovato: $PdfIn" }
  if (!(Validate-Date $VersioneData)) { throw "VersioneData non valida (YYYY-MM-DD): $VersioneData" }

  $Categoria  = Normalize-Slug $Categoria
  $Produttore = Normalize-Slug $Produttore
  $Modello    = Normalize-Slug $Modello

  $destDir = Join-Path $Root ("MANUALI\{0}\{1}\{2}" -f $Categoria,$Produttore,$Modello)
  New-Item -ItemType Directory -Force -Path $destDir | Out-Null

  $fname = "MANUALE_{0}_{1}_v{2}.pdf" -f $Produttore,$Modello,$VersioneData
  $dest  = Safe-Dest (Join-Path $destDir $fname)

  if ($Action -eq "COPY") { Copy-Item -Force $PdfIn $dest } else { Move-Item -Force $PdfIn $dest }
  $hash = (Get-FileHash -Algorithm SHA256 $dest).Hash

  Ensure-Index $IndexManuali "Categoria,Produttore,Modello,VersioneData,File,FullPath,SHA256,ApplicabileA,Note"
  Add-Content -Encoding UTF8 $IndexManuali (CsvLine @(
    $Categoria,$Produttore,$Modello,$VersioneData,(Split-Path $dest -Leaf),$dest,$hash,$ApplicabileA,$Note
  ))

  Write-Host "OK MANUALE -> $dest"
}

function Add-DpiEvidenceCE {
  param(
    [Parameter(Mandatory)] [string]$PdfIn,
    [Parameter(Mandatory)] [string]$Categoria,
    [Parameter(Mandatory)] [string]$Produttore,
    [Parameter(Mandatory)] [string]$Modello,
    [Parameter(Mandatory)] [string]$VersioneData,
    [string]$Note="",
    [ValidateSet("MOVE","COPY")] [string]$Action="MOVE"
  )

  if (!(Test-Path $PdfIn)) { throw "PDF non trovato: $PdfIn" }
  if (!(Validate-Date $VersioneData)) { throw "VersioneData non valida (YYYY-MM-DD): $VersioneData" }

  $Categoria  = Normalize-Slug $Categoria
  $Produttore = Normalize-Slug $Produttore
  $Modello    = Normalize-Slug $Modello

  $destDir = Join-Path $Root ("EVIDENZE\DPI\{0}\{1}\{2}\CE" -f $Categoria,$Produttore,$Modello)
  New-Item -ItemType Directory -Force -Path $destDir | Out-Null

  $fname = "DICHIARAZIONE_CE_{0}_{1}_v{2}.pdf" -f $Produttore,$Modello,$VersioneData
  $dest  = Safe-Dest (Join-Path $destDir $fname)

  if ($Action -eq "COPY") { Copy-Item -Force $PdfIn $dest } else { Move-Item -Force $PdfIn $dest }
  $hash = (Get-FileHash -Algorithm SHA256 $dest).Hash

  Ensure-Index $IndexEvidenze "Tipo,Categoria,Produttore,Modello,VersioneData,File,FullPath,SHA256,Note"
  Add-Content -Encoding UTF8 $IndexEvidenze (CsvLine @(
    "CE",$Categoria,$Produttore,$Modello,$VersioneData,(Split-Path $dest -Leaf),$dest,$hash,$Note
  ))

  Write-Host "OK CE -> $dest"
}

# =========================
# UI POWER (BATCH V3)
# =========================
Write-Host ""
Write-Host "=== INTAKE DPI LIBRERIA (BATCH V3) ==="
Write-Host "ROOT : $Root"
Write-Host "INBOX: $Inbox"
Write-Host ""

$files = Get-ChildItem $Inbox -File -Filter *.pdf -ErrorAction SilentlyContinue | Sort-Object LastWriteTime
if (!$files) {
  Write-Host "INBOX vuota. Fine."
  exit 0
}

Write-Host "PDF trovati:"
$files | ForEach-Object { Write-Host (" - {0}" -f $_.Name) }
Write-Host ""

$Action = (Read-Host "Azione file (MOVE/COPY) [Enter=MOVE]").Trim().ToUpper()
if ([string]::IsNullOrWhiteSpace($Action)) { $Action = "MOVE" }
if ($Action -notin @("MOVE","COPY")) { throw "Azione non valida: $Action" }

# stato “ultimo valore”
$last = @{
  Tipo="MANUALE"
  Categoria=""
  Produttore=""
  Modello=""
  VersioneData=(Get-Date -Format "yyyy-MM-dd")
  ApplicabileA="MODELLO"
  Note=""
}

$summary = New-Object System.Collections.Generic.List[string]

foreach ($f in $files) {
  Write-Host ""
  Write-Host ("=== FILE: {0} ===" -f $f.Name)
  Write-Host "Invio = mantiene valore precedente. (S=skip, Q=esci, O=open)"
  Write-Host ""

  $suggest = Suggest-Tipo $f.Name
  if ($suggest) { $last.Tipo = $suggest }

  $cmd = (Read-Host "Comando [Enter=continua] (S/Q/O)").Trim().ToUpper()
  if ($cmd -eq "Q") { break }
  if ($cmd -eq "S") { $summary.Add(("SKIP,{0}" -f $f.Name)); continue }
  if ($cmd -eq "O") { Start-Process $f.FullName }

  $tipo = Prompt-Default "Tipo (MANUALE/CE)" $last.Tipo
  $tipo = $tipo.Trim().ToUpper()

  $cat  = Prompt-Default "Categoria (es: SISTEMA_RETRATTILE)" $last.Categoria
  $prod = Prompt-Default "Produttore (es: IKAR)" $last.Produttore
  $mod  = Prompt-Default "Modello (es: HRA_12)" $last.Modello

  $ver  = Prompt-Default "VersioneData YYYY-MM-DD" $last.VersioneData
  if (!(Validate-Date $ver)) { throw "VersioneData non valida (YYYY-MM-DD): $ver" }

  $note = Prompt-Default "Note (opzionale)" $last.Note

  if ($tipo -eq "CE") {
    Add-DpiEvidenceCE -PdfIn $f.FullName -Categoria $cat -Produttore $prod -Modello $mod -VersioneData $ver -Note $note -Action $Action
  } else {
    $app = Prompt-Default "ApplicabileA (MODELLO/SERIE/FAMIGLIA)" $last.ApplicabileA
    $app = $app.Trim().ToUpper()
    if ($app -notin @("MODELLO","SERIE","FAMIGLIA")) { $app = "MODELLO" }

    Add-DpiManual -PdfIn $f.FullName -Categoria $cat -Produttore $prod -Modello $mod -VersioneData $ver -ApplicabileA $app -Note $note -Action $Action
    $last.ApplicabileA = $app
  }

  # aggiorna last
  $last.Tipo = $tipo
  $last.Categoria = $cat
  $last.Produttore = $prod
  $last.Modello = $mod
  $last.VersioneData = $ver
  $last.Note = $note

  $summary.Add(("OK,{0},{1},{2},{3},{4},{5}" -f $f.Name,$tipo,$cat,$prod,$mod,$ver))
}

Write-Host ""
Write-Host "OK BATCH COMPLETATO."
Write-Host (" - {0}" -f $IndexManuali)
Write-Host (" - {0}" -f $IndexEvidenze)
Write-Host ""
Write-Host "RIEPILOGO:"
$summary | ForEach-Object { Write-Host (" - " + $_) }
