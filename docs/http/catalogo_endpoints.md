# API Endpoints – Catalogo DPI

Documentazione completa degli endpoint REST per la gestione del catalogo DPI.

## Base URL

```
http://localhost:8000/api/dpi/csv
```

In produzione: sostituire con l'URL del server.

---

## Endpoints

### 1. GET `/template`

Scarica un template CSV vuoto con intestazione standard.

**Response**: `text/csv`

**Headers**:
```
Content-Type: text/csv; charset=utf-8
```

**Esempio CSV**:
```csv
codice,descrizione,prezzo,gruppo
```

#### Esempi

**curl**:
```bash
curl -o template.csv http://localhost:8000/api/dpi/csv/template
```

**PowerShell**:
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/dpi/csv/template" -OutFile "template.csv"
```

---

### 2. POST `/save`

Importa CSV in formato raw (text/csv) con validazioni soft e merge persistente.

**Content-Type**: `text/csv`

**Body**: CSV raw bytes

**Response**: JSON
```json
{
  "status": "ok",
  "saved": true,
  "csv_path": "data/cataloghi/imports/catalogo_20241105_121530.csv",
  "rows_parsed": 15,
  "updated_existing": 3,
  "accepted": 14,
  "rejected": 1,
  "errors": [...],
  "warnings": [...],
  "total_items": 42
}
```

#### Esempi

**curl**:
```bash
curl -X POST -H "Content-Type: text/csv" --data-binary @catalogo.csv http://localhost:8000/api/dpi/csv/save
```

**PowerShell**:
```powershell
$csv = Get-Content -Path "catalogo.csv" -Raw -Encoding UTF8
Invoke-RestMethod -Uri "http://localhost:8000/api/dpi/csv/save" -Method Post -Body $csv -ContentType "text/csv"
```

---

### 3. POST `/import-file`

Importa CSV tramite multipart/form-data (upload file).

**Content-Type**: `multipart/form-data`

**Form field**: `file` (CSV file)

**Response**: JSON (simile a `/save`)

#### Esempi

**curl**:
```bash
curl -F "file=@catalogo.csv" http://localhost:8000/api/dpi/csv/import-file
```

**PowerShell**:
```powershell
$form = @{file = Get-Item -Path "catalogo.csv"}
Invoke-RestMethod -Uri "http://localhost:8000/api/dpi/csv/import-file" -Method Post -Form $form
```

---

### 4. GET `/catalogo`

Ritorna il catalogo DPI corrente in formato JSON.

**Response**: JSON
```json
{
  "count": 42,
  "items": [
    {
      "codice": "IKAR-ABC123",
      "descrizione": "Imbracatura anticaduta professionale",
      "prezzo": "89.90",
      "gruppo": "ANTICADUTA"
    },
    ...
  ]
}
```

#### Esempi

**curl**:
```bash
curl http://localhost:8000/api/dpi/csv/catalogo | jq
```

**PowerShell**:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/dpi/csv/catalogo" | ConvertTo-Json
```

---

### 5. GET `/export`

Esporta il catalogo in formato CSV con filtri e selezione colonne.

**Query Parameters**:
- `gruppo` (optional): Filtra per gruppo (es. ANTICADUTA)
- `columns` (optional): Alias o lista colonne
  - Alias: `short`, `listino`, `full`, `id`
  - Lista: es. `codice,prezzo`

**Response**: `text/csv`

#### Esempi

**Export completo**:
```bash
curl "http://localhost:8000/api/dpi/csv/export" -o catalogo_full.csv
```

**Export filtrato per gruppo**:
```bash
curl "http://localhost:8000/api/dpi/csv/export?gruppo=ANTICADUTA" -o anticaduta.csv
```

**Export con colonne personalizzate**:
```bash
curl "http://localhost:8000/api/dpi/csv/export?columns=listino" -o listino.csv
```

**PowerShell**:
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/dpi/csv/export?gruppo=ANTICADUTA&columns=listino" -OutFile "export.csv"
```

---

### 6. GET `/metrics`

Ritorna metriche aggregate del catalogo.

**Response**: JSON
```json
{
  "total_items": 42,
  "by_group": {
    "ANTICADUTA": 15,
    "CASCO": 10,
    "GUANTI": 12,
    "_vuoto_": 5
  },
  "price_filled": 38,
  "price_missing": 4
}
```

#### Esempi

**curl**:
```bash
curl http://localhost:8000/api/dpi/csv/metrics | jq
```

**PowerShell**:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/dpi/csv/metrics"
```

---

### 7. GET `/report.html`

Dashboard HTML interattiva con metriche e tabella del catalogo.

**Query Parameters**:
- `gruppo` (optional): Filtra per gruppo
- `columns` (optional): Alias o lista colonne (default: `listino`)
- `limit` (optional): Limite righe tabella (default: 200, max: 5000)

**Response**: `text/html`

#### Esempi

**Apri in browser**:
```bash
# Linux/macOS
xdg-open "http://localhost:8000/api/dpi/csv/report.html"

# Windows PowerShell
Start-Process "http://localhost:8000/api/dpi/csv/report.html"
```

**Report filtrato**:
```
http://localhost:8000/api/dpi/csv/report.html?gruppo=ANTICADUTA&limit=50
```

---

## Endpoint Meta (root level)

Oltre agli endpoint CSV, l'applicazione espone:

### GET `/healthz`

Health check endpoint.

**Response**: JSON
```json
{"status": "ok"}
```

### GET `/version`

Informazioni versione applicazione.

**Response**: JSON
```json
{
  "name": "tpi_evoluto",
  "version": "0.1.0",
  "git": "abc1234"
}
```

### GET `/metrics`

Metriche aggregate (include metriche CSV).

**Response**: JSON
```json
{
  "csv": {
    "total_items": 42,
    "by_group": {...},
    "price_filled": 38,
    "price_missing": 4
  }
}
```

---

## Validazioni

### Campi richiesti
- **codice**: obbligatorio (error se mancante)

### Campi opzionali con warning
- **descrizione**: warning se mancante
- **prezzo**: warning se non numerico

### Formato prezzo
Accettati: `19.90`, `19,90`, `19`  
Non accettati: `€19.90`, `19.90€`, `19,90 EUR`

---

## Codici errore/warning

### Errori (righe rifiutate)
- `ERR_MISSING_CODE`: campo 'codice' mancante

### Warning (righe accettate con avvisi)
- `WARN_DESC_MISSING`: campo 'descrizione' mancante
- `WARN_PRICE_NON_NUMERIC`: campo 'prezzo' non numerico

---

## Note tecniche

- **Encoding**: Auto-detection (UTF-8-sig, UTF-8, CP1252, Latin-1)
- **Separatore CSV**: virgola (`,`)
- **Line endings**: supporta CRLF, LF, mixed
- **BOM**: gestito automaticamente (UTF-8-sig)
- **Limite upload**: Configurabile in FastAPI (valore default specifico dipende dalla configurazione del server)
- **Performance**: report.html limitato a 5000 righe max

---

## Testing rapido

File di test disponibili in `docs/http/`:
- `api-tests.http`: Collezione HTTP per VS Code REST Client
- `api-scenari.http`: Scenari d'uso completi

---

## Link correlati

- [Catalogo Overview](../catalogo/index.md)
- [Go Live Checklist](../catalogo/checklist_go_live.md)
- [Frontend TODO](../frontend/catalogo_flutter_todo.md)
