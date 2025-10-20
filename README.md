# TPI_evoluto## API

### /api/dpi/csv/template (GET, HEAD)
CSV sicuro per Excel/Windows: **BOM UTF-8** + **CRLF**.
Headers: Content-Type: text/csv; charset=utf-8 · Content-Disposition: attachment; filename="dpi_template.csv"

Prima riga:

Test rapidi:
`ash
curl -i http://127.0.0.1:8010/api/dpi/csv/template
curl -fS http://127.0.0.1:8010/api/dpi/csv/template -o dpi_template.csv
# PowerShell (BOM): (Get-Content -Encoding Byte -TotalCount 3 .\dpi_template.csv) | % { '{0:X2}' -f  }
