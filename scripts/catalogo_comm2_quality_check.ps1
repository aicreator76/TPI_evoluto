param(
    [string]$RootPath = "E:\CLONAZIONE\tpi_evoluto"
)

$catalogDir = Join-Path $RootPath "docs\catalogo\COMMERCIALE_2_0"
$reportDir  = Join-Path $RootPath "REPORT_DELTA"

if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir | Out-Null
}

$timestamp  = Get-Date -Format "yyyyMMdd_HHmmss"
$reportPath = Join-Path $reportDir "catalogo_comm2_quality_$timestamp.csv"

$results = @()

function Add-Result {
    param(
        [string]$File,
        [string]$Codice,
        [string]$Livello,
        [string]$Messaggio
    )

    $script:results += [PSCustomObject]@{
        file            = $File
        codice_articolo = $Codice
        livello         = $Livello
        messaggio       = $Messaggio
    }
}

$files = Get-ChildItem $catalogDir -Filter "*_TPI.csv"

foreach ($file in $files) {

    $csvPath = $file.FullName
    Write-Host "Valuto file: $csvPath"

    try {
        $rows = Import-Csv $csvPath
    }
    catch {
        Add-Result -File $file.Name -Codice "" -Livello "ERRORE_IMPORT" -Messaggio $_.Exception.Message
        continue
    }

    if (-not $rows -or $rows.Count -eq 0) {
        Add-Result -File $file.Name -Codice "" -Livello "INFO" -Messaggio "File senza righe dati"
        continue
    }

    $firstRow = $rows[0]

    $requiredCols = @(
        "codice_articolo",
        "nome_breve",
        "categoria_macro",
        "descrizione_breve",
        "norme_en",
        "famiglia_dpi",
        "linea_modello"
    )

    foreach ($col in $requiredCols) {
        if (-not ($firstRow.PSObject.Properties.Name -contains $col)) {
            Add-Result -File $file.Name -Codice "" -Livello "ERRORE_SCHEMA" -Messaggio "Colonna mancante: $col"
        }
    }

    $hasFamiglia = $firstRow.PSObject.Properties.Name -contains "famiglia_dpi"
    $hasLinea    = $firstRow.PSObject.Properties.Name -contains "linea_modello"

    foreach ($row in $rows) {

        $codice = $row.codice_articolo
        $nome   = $row.nome_breve
        $cat    = $row.categoria_macro
        $desc   = $row.descrizione_breve
        $norme  = $row.norme_en

        $fam   = $null
        $linea = $null

        if ($hasFamiglia) {
            $fam = $row.famiglia_dpi
        }

        if ($hasLinea) {
            $linea = $row.linea_modello
        }

        if ([string]::IsNullOrWhiteSpace($codice)) {
            Add-Result -File $file.Name -Codice "" -Livello "ERRORE_DATO" -Messaggio "codice_articolo vuoto"
        }

        if ([string]::IsNullOrWhiteSpace($nome)) {
            Add-Result -File $file.Name -Codice $codice -Livello "ERRORE_DATO" -Messaggio "nome_breve vuoto"
        }

        if ([string]::IsNullOrWhiteSpace($cat)) {
            Add-Result -File $file.Name -Codice $codice -Livello "ERRORE_DATO" -Messaggio "categoria_macro vuota"
        }

        if ([string]::IsNullOrWhiteSpace($desc)) {
            Add-Result -File $file.Name -Codice $codice -Livello "WARN" -Messaggio "descrizione_breve vuota"
        }

        if ($hasFamiglia -and [string]::IsNullOrWhiteSpace($fam)) {
            Add-Result -File $file.Name -Codice $codice -Livello "WARN" -Messaggio "famiglia_dpi vuota"
        }

        if ($hasLinea -and [string]::IsNullOrWhiteSpace($linea)) {
            Add-Result -File $file.Name -Codice $codice -Livello "WARN" -Messaggio "linea_modello vuota"
        }

        if ([string]::IsNullOrWhiteSpace($norme)) {
            Add-Result -File $file.Name -Codice $codice -Livello "WARN" -Messaggio "norme_en vuote"
        }
        elseif ($norme -notmatch "EN\s*\d") {
            Add-Result -File $file.Name -Codice $codice -Livello "WARN" -Messaggio "norme_en formato sospetto: $norme"
        }
    }
}

if ($results.Count -eq 0) {
    Write-Host "Nessuna anomalia trovata. Catalogo COMMERCIALE 2.0 OK."
}
else {
    $results | Export-Csv -Path $reportPath -NoTypeInformation -Encoding UTF8
    Write-Host "Report qualitÃ  generato:"
    Write-Host "  $reportPath"
}
