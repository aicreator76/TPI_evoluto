param(
    [string]$SrcCsv = "E:\CLONAZIONE\tpi_evoluto\docs\catalogo\COMMERCIALE_2_0\catalogo_dpi_comm2_part1_raw.csv",
    [string]$DstCsv = "E:\CLONAZIONE\tpi_evoluto\docs\catalogo\COMMERCIALE_2_0\catalogo_dpi_comm2_part1_TPI.csv",
    [string]$ApiUrl = "http://127.0.0.1:8000/api/dpi/csv/save"
)

Write-Host "=== TPI – COMMERCIALE 2.0 → CSV TPI + IMPORT ===" -ForegroundColor Cyan

if (!(Test-Path $SrcCsv)) {
    Write-Error "Sorgente CSV non trovata: $SrcCsv"
    exit 1
}

$rows = Import-Csv -Path $SrcCsv -Delimiter ';'
Write-Host ("Righe lette dal CSV sorgente: {0}" -f $rows.Count)

if ($rows.Count -eq 0) {
    Write-Error "Nessuna riga nel CSV sorgente, fermo tutto."
    exit 1
}

$rowsTpi = $rows | ForEach-Object {
    $codice      = $_.codice_articolo
    $nomeBreve   = $_.nome_breve
    $catMacro    = $_.categoria_macro
    $descBreve   = $_.descrizione_breve

    # Descrizione commerciale TPI: nome + descrizione
    $descrizione = "$nomeBreve - $descBreve"

    [pscustomobject]@{
        codice      = $codice
        descrizione = $descrizione
        prezzo      = ""
        gruppo      = $catMacro
    }
}

$rowsTpi | Export-Csv -Path $DstCsv -NoTypeInformation -Encoding UTF8

Write-Host "Creato CSV TPI compatibile:"
Write-Host "  $DstCsv"

$csvBody = Get-Content $DstCsv -Raw

Write-Host "Chiamo API TPI:"
Write-Host "  $ApiUrl"

$response = Invoke-RestMethod `
    -Uri $ApiUrl `
    -Method POST `
    -Body $csvBody `
    -ContentType "text/plain"

Write-Host "=== RISPOSTA BACKEND ==="
$response | Format-List *
