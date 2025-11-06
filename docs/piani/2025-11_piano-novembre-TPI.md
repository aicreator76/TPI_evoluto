# Piano novembre TPI — Cabina di Regia (AELIS)

## Stato attuale
- CSV catalogo **OK**: template/save/catalogo/export operativi
- File test: docs/http/api-tests.http
- PR #42 in **auto-merge (squash)** quando i check vanno verdi

## Comandi rapidi (PowerShell)
- Template:  Invoke-RestMethod http://127.0.0.1:8000/api/dpi/csv/template
- Save CSV:  Invoke-RestMethod -Uri http://127.0.0.1:8000/api/dpi/csv/save -Method Post -ContentType 'text/csv' -Body \
- Catalogo:  Invoke-RestMethod http://127.0.0.1:8000/api/dpi/csv/catalogo
- Export:    Invoke-WebRequest http://127.0.0.1:8000/api/dpi/csv/export -OutFile .\catalogo_export.csv

## Prossime mosse (AELIS Orchestrator)
1. Badge in README ✅
2. Chiudere PR #42 (auto-merge) ✅ in attesa dei check
3. Preparare **route /import-file** (UploadFile) + validazioni soft
4. Esporti aggiuntivi: CSV per gruppi e price-list
5. Docs: mini sezione “Cataloghi DPI” (uso da desktop e da CI)

— AELIS
