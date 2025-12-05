param(
    [string]$RootPath = "E:\CLONAZIONE\tpi_evoluto"
)

$comm2Dir = Join-Path $RootPath "docs\catalogo\COMMERCIALE_2_0"

$files = @(
    "catalogo_dpi_comm2_part1_TPI.csv",
    "catalogo_dpi_comm2_part2_funi_TPI.csv",
    "catalogo_dpi_comm2_part3_accessori_TPI.csv",
    "catalogo_dpi_comm2_part4_retrattile_TPI.csv",
    "catalogo_dpi_comm2_part5_posizionamento_TPI.csv",
    "catalogo_dpi_comm2_part6_scorrevoli_TPI.csv"
)

Write-Host "=== LYNX - FIX TASSONOMIA COMMERCIALE 2.0 ===" -ForegroundColor Cyan

foreach ($file in $files) {

    $path = Join-Path $comm2Dir $file

    if (-not (Test-Path $path)) {
        Write-Host "File non trovato, salto: $path" -ForegroundColor DarkYellow
        continue
    }

    Write-Host ""
    Write-Host "Elaboro: $path" -ForegroundColor Green

    $rows = Import-Csv -Path $path

    if (-not $rows -or $rows.Count -eq 0) {
        Write-Host "  Nessuna riga dati, salto." -ForegroundColor DarkYellow
        continue
    }

    $updated = 0

    foreach ($row in $rows) {
        # Assicuro che le colonne esistano
        if (-not ($row.PSObject.Properties.Name -contains "famiglia_dpi")) {
            $row | Add-Member -NotePropertyName "famiglia_dpi" -NotePropertyValue ""
        }
        if (-not ($row.PSObject.Properties.Name -contains "linea_modello")) {
            $row | Add-Member -NotePropertyName "linea_modello" -NotePropertyValue ""
        }

        # Se linea_modello e' vuoto, usa nome_breve
        if ([string]::IsNullOrWhiteSpace($row.linea_modello) -and -not [string]::IsNullOrWhiteSpace($row.nome_breve)) {
            $row.linea_modello = $row.nome_breve
            $updated++
        }

        # famiglia_dpi: se e' vuoto rimane vuoto (logiche avanzate in V3)
    }

    # Esporto sovrascrivendo il file
    $rows | Export-Csv -Path $path -NoTypeInformation -Encoding UTF8

    Write-Host "  Aggiornate linea_modello su $updated righe." -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=== LYNX - FIX TASSONOMIA COMMERCIALE 2.0 COMPLETATO ===" -ForegroundColor Cyan
