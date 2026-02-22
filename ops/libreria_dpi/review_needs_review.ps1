param(
  [string]$Root = "E:\CLONAZIONE\REPORT_DELTA\LIBRERIA_DPI",
  [string]$Folder = "E:\CLONAZIONE\REPORT_DELTA\LIBRERIA_DPI\_INBOX_NEEDS_REVIEW",
  [ValidateSet("MOVE","COPY")] [string]$Action = "MOVE",
  [string]$VersioneData = (Get-Date -Format "yyyy-MM-dd"),
  [switch]$DedupByHash = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# -------------------------
# PATHS
# -------------------------
$InboxReview = Join-Path $Root "_INBOX_NEEDS_REVIEW"
$DupHashDir  = Join-Path $Root "_DUPLICATI_HASH"
$IndexManuali  = Join-Path $Root "INDICE\MANUALI_INDEX.csv"
$IndexEvidenze = Join-Path $Root "INDICE\EVIDENZE_INDEX.csv"
$LogDir = Join-Path $Root "INDICE\LOG"

New-Item -ItemType Directory -Force -Path $Root, $InboxReview, $DupHashDir, $LogDir | Out-Null

$LogPath = Join-Path $LogDir ("review_fix_{0}_{1}.csv" -f (Get-Date -Format "yyyy-MM-dd_HHmmss"), $Action)

# -------------------------
# HELPERS
# -------------------------
function Ensure-Index([string]$Path, [string]$Header) {
  if (!(Test-Path $Path)) { $Header | Set-Content -Encoding UTF8 $Path }
}

function CsvLine([string[]]$Fields) {
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

function DeUmlaut([string]$s) {
  if ([string]::IsNullOrWhiteSpace($s)) { return "" }
  $x = $s
  try {
    $x = $x.Replace(([string][char]0x00C4),'AE').Replace(([string][char]0x00D6),'OE').Replace(([string][char]0x00DC),'UE')  # ÄÖÜ
    $x = $x.Replace(([string][char]0x00DF),'SS')                                                                           # ß
    $x = $x.Replace(([string][char]0x00E4),'AE').Replace(([string][char]0x00F6),'OE').Replace(([string][char]0x00FC),'UE')  # äöü
  } catch { return $s }
  return $x
}

function Safe-Dest([string]$dest) {
  if (!(Test-Path $dest)) { return $dest }
  $dir = Split-Path $dest
  $base = [IO.Path]::GetFileNameWithoutExtension($dest)
  $ext = [IO.Path]::GetExtension($dest)
  $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
  return (Join-Path $dir ("{0}_DUP_{1}{2}" -f $base,$stamp,$ext))
}

function CopyOrMove([string]$src, [string]$dst, [ValidateSet("MOVE","COPY")] [string]$mode) {
  if ($mode -eq "COPY") { Copy-Item -LiteralPath $src -Destination $dst -Force }
  else { Move-Item -LiteralPath $src -Destination $dst -Force }
}

function Prompt-Keep([string]$label, [string]$prev) {
  $v = Read-Host ("{0} [{1}]" -f $label,$prev)
  if ([string]::IsNullOrWhiteSpace($v)) { return $prev }
  return $v
}

# -------------------------
# HASH INDEX (per dedup)
# -------------------------
function Load-HashIndex {
  $map = @{}   # hash -> FullPath
  foreach($p in @($IndexManuali,$IndexEvidenze)) {
    if (!(Test-Path $p)) { continue }
    try {
      $rows = Import-Csv -LiteralPath $p
      foreach($r in $rows) {
        if ($null -eq $r) { continue }
        $h = ""
        $fp = ""
        if ($r.PSObject.Properties.Name -contains "SHA256") { $h = [string]$r.SHA256 }
        if ($r.PSObject.Properties.Name -contains "FullPath") { $fp = [string]$r.FullPath }
        if ([string]::IsNullOrWhiteSpace($h)) { continue }
        if (-not $map.ContainsKey($h)) { $map[$h] = $fp }
      }
    } catch {
      # CSV sporco? non blocchiamo la review
    }
  }
  return $map
}

$KnownHashes = Load-HashIndex

# -------------------------
# GUESSERS (PS5 safe)
# -------------------------
function Guess-Tipo([string]$path){
  $n = (DeUmlaut([IO.Path]::GetFileNameWithoutExtension($path))).ToUpper()
  if($n -match 'KONFORM|KONFORMIT|DECLAR|DICHIARAZION|CE\b|EU\b|DOC\b'){ return "CE" }
  return "MANUALE"
}

function Guess-Produttore([string]$path){
  $p = $path.ToUpper()
  if($p -match '\\TEUF' -or $p -match 'TEUFELBERGER|TEUF\b|FALLSORB|ERGO|MULTIGRIP|BANDSCHLINGE'){ return "TEUFELBERGER" }
  if($p -match '\\IKAR' -or $p -match 'IKAR\b|HWB|HWPB|HRA|ACB|DB[-_ ]?A2|ABS\s*3A'){ return "IKAR" }
  return ""
}

function Guess-Modello([string]$path){
  $n0 = (DeUmlaut([IO.Path]::GetFileNameWithoutExtension($path))).ToUpper()

  # IKAR: HWB/HWPB/HRA/HRAE con 2,8 -> 28
  if($n0 -match '\b(HWB|HWPB|HRA|HRAE|HRA_E|HRA-?E)\s*[-_ ]*([0-9]{1,3})(?:[.,]([0-9]{1,2}))?\b'){
    $pref=$matches[1]; $a=$matches[2]; $b=$matches[3]
    if([string]::IsNullOrWhiteSpace($b)){ $m = ("{0}_{1}" -f $pref,$a) }
    else { $m = ("{0}_{1}{2}" -f $pref,$a,$b) }
    if($n0 -match '\bDW\b'){ $m = $m + "_DW" }
    if($m -eq "HRA_12" -and $n0 -match '\bHRA\s*12\s*E\b'){ $m = "HRA_12_E" }
    return (Normalize-Slug $m)
  }

  # IKAR: ACB 1,8 / ACB 1-8
  if($n0 -match '\bACB\s*[-_ ]*([0-9]{1,3})[,\.-]([0-9])\b'){
    return (Normalize-Slug ("ACB_{0}{1}" -f $matches[1],$matches[2]))
  }
  if($n0 -match '\bACB\s*[-_ ]*([0-9]{1,3})\b'){
    return (Normalize-Slug ("ACB_{0}" -f $matches[1]))
  }

  # IKAR: DB-A2
  if($n0 -match '\bDB\s*[-_ ]*A2\b'){ return "DB_A2" }

  # IKAR: ABS 3A + varianti
  if($n0 -match '\bABS\s*3A\b'){
    $suffix = ""
    if($n0 -match '\bWHSL\b'){ $suffix += "_WHSL" }
    if($n0 -match '\bWHPL\b'){ $suffix += "_WHPL" }
    if($n0 -match '(\bWH\b|_WH_)'){ $suffix += "_WH" }
    if($n0 -match '(\bW\b|_W_)'){ $suffix += "_W" }
    return (Normalize-Slug ("ABS_3A{0}" -f $suffix))
  }

  # Manuale generico
  if($n0 -match 'HOEHENSICHERUNGSGERAET|HOHENSICHERUNGSGERAET|HOEHENSICHERUNGSGERAETE|HOHENSICHERUNGSGERAETE'){
    return "HOEHENSICHERUNGSGERAETE"
  }

  # TEUF keywords
  if($n0 -match '\bBANDSCHLINGE\b'){ return "BANDSCHLINGE" }
  if($n0 -match '\bERGO[-_ ]?CLICK\b'){ return "ERGO_CLICK" }
  if($n0 -match '\bMULTIGRIP\b'){ return "MULTIGRIP" }
  if($n0 -match '\bFALLSORB\b'){ return "FALLSORB" }
  if($n0 -match 'INSTRUCTION[-_ ]MANUAL'){ return "INSTRUCTION_MANUAL" }

  return ""
}

function Guess-Categoria([string]$prod,[string]$mod,[string]$path){
  # IKAR retrattili / componenti
  if($mod -match '^(HWB|HWPB|HRA|ABS_3A|HOEHENSICHERUNGSGERAETE|ACB_|DB_A2)'){ return "SISTEMA_RETRATTILE" }

  # TEUF mapping base (aggiustabile a mano)
  if($prod -eq "TEUFELBERGER"){
    if($mod -match 'FALLSORB'){ return "CORDINO_Y_ASSORBITORE" }
    if($mod -match 'MULTIGRIP'){ return "CORDINO_POSIZIONAMENTO" }
    if($mod -match 'BANDSCHLINGE'){ return "CORDINO_POSIZIONAMENTO" }
    if($mod -match 'ERGO_CLICK'){ return "MOSCHETTONE" }
    if($mod -match 'INSTRUCTION_MANUAL'){ return "CORDINO_Y_ASSORBITORE" }
  }

  return ""
}

# -------------------------
# ADDERS (scrivono indici)
# -------------------------
function Add-Manual([string]$src,[string]$cat,[string]$prod,[string]$mod,[string]$ver,[string]$note){
  $cat = Normalize-Slug $cat
  $prod = Normalize-Slug $prod
  $mod = Normalize-Slug $mod

  $destDir = Join-Path $Root ("MANUALI\{0}\{1}\{2}" -f $cat,$prod,$mod)
  New-Item -ItemType Directory -Force -Path $destDir | Out-Null

  $fname = "MANUALE_{0}_{1}_v{2}.pdf" -f $prod,$mod,$ver
  $dest  = Safe-Dest (Join-Path $destDir $fname)

  CopyOrMove $src $dest $Action

  $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $dest).Hash
  Ensure-Index $IndexManuali "Categoria,Produttore,Modello,VersioneData,File,FullPath,SHA256,ApplicabileA,Note"
  Add-Content -Encoding UTF8 $IndexManuali (CsvLine @($cat,$prod,$mod,$ver,(Split-Path $dest -Leaf),$dest,$hash,"MODELLO",$note))

  return @($dest,$hash)
}

function Add-CE([string]$src,[string]$cat,[string]$prod,[string]$mod,[string]$ver,[string]$note){
  $cat = Normalize-Slug $cat
  $prod = Normalize-Slug $prod
  $mod = Normalize-Slug $mod

  $destDir = Join-Path $Root ("EVIDENZE\DPI\{0}\{1}\{2}\CE" -f $cat,$prod,$mod)
  New-Item -ItemType Directory -Force -Path $destDir | Out-Null

  $fname = "DICHIARAZIONE_CE_{0}_{1}_v{2}.pdf" -f $prod,$mod,$ver
  $dest  = Safe-Dest (Join-Path $destDir $fname)

  CopyOrMove $src $dest $Action

  $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $dest).Hash
  Ensure-Index $IndexEvidenze "Tipo,Categoria,Produttore,Modello,VersioneData,File,FullPath,SHA256,Note"
  Add-Content -Encoding UTF8 $IndexEvidenze (CsvLine @("CE",$cat,$prod,$mod,$ver,(Split-Path $dest -Leaf),$dest,$hash,$note))

  return @($dest,$hash)
}

# -------------------------
# LOG HEADER
# -------------------------
"Timestamp,Status,Tipo,Categoria,Produttore,Modello,VersioneData,Source,Dest,SHA256,Note" | Set-Content -Encoding UTF8 $LogPath

Write-Host ""
Write-Host "=== REVIEW FIXER (NEEDS_REVIEW) ==="
Write-Host ("Folder: " + $Folder)
Write-Host ("Action: " + $Action + " | VersioneData: " + $VersioneData + " | DedupByHash: " + $DedupByHash)
Write-Host ("LOG: " + $LogPath)
Write-Host ""

if(!(Test-Path $Folder)){ throw "Manca folder: $Folder" }

$pdfs = Get-ChildItem -LiteralPath $Folder -File -Filter *.pdf -ErrorAction SilentlyContinue | Sort-Object Name
if(!$pdfs){
  Write-Host "Folder vuota. Fine."
  exit 0
}

Write-Host "Trovati:"
$pdfs | ForEach-Object { Write-Host (" - " + $_.Name) }

# preset iniziale per evitare “IKAR rimane appiccicato su TEUF”
$folderUpper = $Folder.ToUpper()
$startProd = ""
if($folderUpper -match 'TEUF'){ $startProd = "TEUFELBERGER" }
elseif($folderUpper -match 'IKAR'){ $startProd = "IKAR" }

$last = @{
  Tipo="MANUALE"
  Categoria="SISTEMA_RETRATTILE"
  Produttore=$startProd
  Modello=""
  VersioneData=$VersioneData
  Note="REVIEW_FIX"
}

[int]$ok=0; [int]$skipDup=0; [int]$err=0; [int]$i=0

foreach($f in $pdfs){
  $i++
  Write-Host ""
  Write-Host ("=== FILE {0}/{1}: {2} ===" -f $i,$pdfs.Count,$f.Name)

  try{
    $srcHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $f.FullName).Hash

    if($DedupByHash -and $KnownHashes.ContainsKey($srcHash)){
      $prodHint = Guess-Produttore $f.FullName
      if([string]::IsNullOrWhiteSpace($prodHint)){ $prodHint = "UNKNOWN" }
      $dupDir = Join-Path $DupHashDir (Join-Path $VersioneData (Join-Path "MANUAL_REVIEW" $prodHint))
      New-Item -ItemType Directory -Force -Path $dupDir | Out-Null
      $dupDest = Safe-Dest (Join-Path $dupDir $f.Name)
      CopyOrMove $f.FullName $dupDest $Action
      $skipDup++

      Add-Content -Encoding UTF8 $LogPath (CsvLine @(
        (Get-Date -Format "yyyy-MM-dd HH:mm:ss"),"SKIP_DUP_HASH","","","","",$VersioneData,$f.FullName,$dupDest,$srcHash,("DUP_HASH of: " + $KnownHashes[$srcHash])
      ))

      Write-Host ("SKIP_DUP_HASH -> " + $dupDest)
      continue
    }

    # guess per default
    $gTipo = Guess-Tipo $f.FullName
    $gProd = Guess-Produttore $f.FullName
    $gMod  = Guess-Modello $f.FullName
    $gCat  = Guess-Categoria $gProd $gMod $f.FullName

    if([string]::IsNullOrWhiteSpace($gTipo)){ $gTipo = $last.Tipo }
    if([string]::IsNullOrWhiteSpace($gProd)){ $gProd = $last.Produttore }
    if([string]::IsNullOrWhiteSpace($gMod)){  $gMod  = $last.Modello }
    if([string]::IsNullOrWhiteSpace($gCat)){  $gCat  = $last.Categoria }

    if([string]::IsNullOrWhiteSpace($gProd)){ $gProd = "IKAR" }

    Write-Host ("Source hint Produttore: " + (Guess-Produttore $f.FullName))

    Write-Host "Invio = tiene il valore precedente. Scrivi 'Q' su Tipo per uscire."
    $tipo = Prompt-Keep "Tipo (MANUALE/CE)" $gTipo
    if($tipo.ToUpper() -eq "Q"){ break }
    $tipo = $tipo.ToUpper()

    $cat  = Prompt-Keep "Categoria" $gCat
    $prod = Prompt-Keep "Produttore" $gProd
    $mod  = Prompt-Keep "Modello" $gMod
    $ver  = Prompt-Keep "VersioneData" $last.VersioneData
    $note = Prompt-Keep "Note" $last.Note

    $cat  = Normalize-Slug $cat
    $prod = Normalize-Slug $prod
    $mod  = Normalize-Slug $mod

    if([string]::IsNullOrWhiteSpace($cat) -or [string]::IsNullOrWhiteSpace($mod)){
      throw "Categoria o Modello vuoti: non posso importare."
    }

    if($tipo -eq "CE"){
      $res = Add-CE $f.FullName $cat $prod $mod $ver $note
    } else {
      $res = Add-Manual $f.FullName $cat $prod $mod $ver $note
    }

    $dest = $res[0]
    $hash = $res[1]
    if(-not $KnownHashes.ContainsKey($hash)){ $KnownHashes[$hash] = $dest }

    Add-Content -Encoding UTF8 $LogPath (CsvLine @(
      (Get-Date -Format "yyyy-MM-dd HH:mm:ss"),"OK",$tipo,$cat,$prod,$mod,$ver,$f.FullName,$dest,$hash,$note
    ))

    Write-Host ("OK -> " + $dest)
    $ok++

    $last.Tipo = $tipo
    $last.Categoria = $cat
    $last.Produttore = $prod
    $last.Modello = $mod
    $last.VersioneData = $ver
    $last.Note = $note
  }
  catch{
    $err++
    Add-Content -Encoding UTF8 $LogPath (CsvLine @(
      (Get-Date -Format "yyyy-MM-dd HH:mm:ss"),"ERROR","","","","",$VersioneData,$f.FullName,"","",($_.Exception.Message -replace "`r|`n"," ")
    ))
    Write-Host ("ERROR: " + $_.Exception.Message)
  }
}

Write-Host ""
Write-Host ("OK: {0} | SKIP_DUP_HASH: {1} | ERROR: {2}" -f $ok,$skipDup,$err)
Write-Host ("Log: " + $LogPath)
Write-Host "DONE."
