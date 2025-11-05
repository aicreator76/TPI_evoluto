# Catalogo DPI – Overview

Il **Catalogo DPI** è un sistema di gestione centralizzato per Dispositivi di Protezione Individuale (DPI), accessibile tramite API REST.

## Router CSV: `/api/dpi/csv/`

Il router CSV offre endpoint completi per la gestione del catalogo:

- **Template CSV**: scarica un template CSV vuoto
- **Import**: carica file CSV con validazione soft
- **Export**: esporta il catalogo in vari formati
- **Metriche**: visualizza statistiche del catalogo
- **Report HTML**: dashboard web interattiva

## Funzionalità principali

### 1. Import CSV con validazione
- Supporto multi-encoding (UTF-8, UTF-8-sig, CP1252, Latin-1)
- Validazione soft: separa righe accettate da righe rifiutate
- Merge intelligente: aggiorna elementi esistenti o ne aggiunge di nuovi
- Audit trail: salva copie dei file importati con timestamp

### 2. Export filtrato
- Filtro per gruppo DPI
- Selezione colonne personalizzata (alias predefiniti: `short`, `listino`, `full`)
- Export in formato CSV standard

### 3. Report HTML interattivo
- Dashboard con metriche aggregate
- Visualizzazione tabellare del catalogo
- Filtri per gruppo
- Anteprima configurabile (limite righe)

## Esempi rapidi

### PowerShell

```powershell
# Scarica template
Invoke-WebRequest -Uri "http://localhost:8000/api/dpi/csv/template" -OutFile "template.csv"

# Upload CSV
$form = @{file = Get-Item -Path "catalogo.csv"}
Invoke-RestMethod -Uri "http://localhost:8000/api/dpi/csv/import-file" -Method Post -Form $form

# Visualizza report HTML
Start-Process "http://localhost:8000/api/dpi/csv/report.html"

# Export filtrato
Invoke-WebRequest -Uri "http://localhost:8000/api/dpi/csv/export?gruppo=ANTICADUTA&columns=listino" -OutFile "export.csv"
```

### curl

```bash
# Scarica template
curl -o template.csv http://localhost:8000/api/dpi/csv/template

# Upload CSV
curl -F "file=@catalogo.csv" http://localhost:8000/api/dpi/csv/import-file

# Visualizza metriche
curl http://localhost:8000/api/dpi/csv/metrics | jq

# Export filtrato
curl "http://localhost:8000/api/dpi/csv/export?gruppo=ANTICADUTA&columns=listino" -o export.csv
```

## Struttura dati

Il catalogo gestisce elementi DPI con i seguenti campi:

- **codice**: Codice identificativo univoco (es. IKAR-ABC123)
- **descrizione**: Descrizione dettagliata del DPI
- **prezzo**: Prezzo (formato numerico, con ',' o '.')
- **gruppo**: Categoria/gruppo DPI (es. ANTICADUTA, CASCO, GUANTI)

## Report HTML

Il report HTML (`/api/dpi/csv/report.html`) offre:

- Conteggio totale elementi
- Statistiche prezzi (con/senza)
- Distribuzione per gruppo
- Tabella interattiva con anteprima configurabile
- Filtri dinamici per gruppo e colonne

### Screenshot Report
> TODO: Aggiungere screenshot del report.html in produzione

## Note tecniche

- **Storage**: JSON persistente in `data/dpi_items.json`
- **Imports audit**: File CSV salvati in `data/cataloghi/imports/`
- **Validazione**: Soft validation con error/warning separati
- **Encoding**: Auto-detection multi-encoding per compatibilità Windows/Unix
- **Performance**: Limite configurabile per anteprima report (default 200, max 5000 righe)

## Link correlati

- [API Endpoints dettagliati](../http/catalogo_endpoints.md)
- [Go Live Checklist](checklist_go_live.md)
- [Frontend TODO (Flutter)](../frontend/catalogo_flutter_todo.md)
