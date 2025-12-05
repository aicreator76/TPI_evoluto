$csvPath = "E:\CLONAZIONE\tpi_evoluto\docs\catalogo\COMMERCIALE_2_0\catalogo_dpi_comm2_part6_scorrevoli_TPI.csv"
$csvData = Get-Content $csvPath -Raw

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/dpi/csv/save" `
    -Method POST `
    -Body $csvData `
    -ContentType "text/plain"

Write-Host "Import COMMERCIALE 2.0 – part 6 (DISPOSITIVI SCORREVOLI) completato."
