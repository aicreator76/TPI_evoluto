Param(
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

Write-Host "Invio part6 SCORREVOLI (debug)..." -ForegroundColor Cyan

# Percorso CSV SCORREVOLI
$csvPath = "E:\CLONAZIONE\tpi_evoluto\docs\catalogo\COMMERCIALE_2_0\catalogo_dpi_comm2_part6_scorrevoli_TPI.csv"

if (-not (Test-Path $csvPath)) {
    Write-Host "ERRORE: CSV non trovato: $csvPath" -ForegroundColor Red
    exit 1
}

try {
    # === COSTRUZIONE MULTIPART FORM-DATA MANUALE (compatibile PowerShell 5.1) ===

    $boundary = "----TPIBOUNDARY_" + ([System.Guid]::NewGuid().ToString("N"))
    $lf = "`r`n"

    $fileName    = [System.IO.Path]::GetFileName($csvPath)
    $fileContent = [System.IO.File]::ReadAllText($csvPath, [System.Text.Encoding]::UTF8)

    $sb = New-Object System.Text.StringBuilder

    # Parte "file"
    [void]$sb.Append("--$boundary$lf")
    [void]$sb.Append("Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"$lf")
    [void]$sb.Append("Content-Type: text/csv$lf$lf")
    [void]$sb.Append($fileContent)
    [void]$sb.Append("$lf--$boundary--$lf")

    $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($sb.ToString())

    $urlSave = "$BaseUrl/api/dpi/csv/save"

    Write-Host "POST $urlSave (multipart/form-data)..." -ForegroundColor Yellow

    $response = Invoke-RestMethod `
        -Uri $urlSave `
        -Method Post `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $bodyBytes

    Write-Host "=== RISPOSTA BACKEND (POST /api/dpi/csv/save) ===" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 6

} catch {
    Write-Host "ERRORE durante il POST /api/dpi/csv/save:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.Exception.InnerException) {
        Write-Host "Dettaglio interno:" -ForegroundColor DarkRed
        Write-Host $_.Exception.InnerException.Message -ForegroundColor DarkRed
    }
    exit 1
}

# (FACOLTATIVO) Verifica catalogo globale
try {
    $urlCatalog = "$BaseUrl/api/dpi/csv/catalogo"
    Write-Host "`nGET $urlCatalog..." -ForegroundColor Yellow
    $catalogo = Invoke-RestMethod -Uri $urlCatalog -Method Get

    Write-Host "=== VERIFICA CATALOGO DPI ===" -ForegroundColor Cyan
    if ($catalogo -is [System.Array]) {
        Write-Host ("Totale DPI in catalogo: {0}" -f $catalogo.Count)
    } else {
        Write-Host "Risposta catalogo (JSON):"
        $catalogo | ConvertTo-Json -Depth 4
    }
} catch {
    Write-Host "ATTENZIONE: errore nella verifica catalogo (GET /api/dpi/csv/catalogo)" -ForegroundColor DarkYellow
    Write-Host $_.Exception.Message -ForegroundColor DarkYellow
}

Write-Host "DEBUG SCORREVOLI completato." -ForegroundColor Cyan
