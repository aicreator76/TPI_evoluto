\# Catalogo DPI – Modulo TPI\_evoluto



\## Obiettivo



Tenere allineati DPI, scadenze e sostituzioni usando un catalogo unico alimentato da CSV e API HTTP.



\## Percorsi file (default)



Se non imposti `CATALOGHI\_BASE\_DIR`, i dati del Catalogo vengono creati sotto:



\- `E:\\CLONAZIONE\\tpi\_evoluto\\data\\cataloghi\\inbox`

\- `E:\\CLONAZIONE\\tpi\_evoluto\\data\\cataloghi\\clean`

\- `E:\\CLONAZIONE\\tpi\_evoluto\\data\\cataloghi\\imports`

\- `E:\\CLONAZIONE\\tpi\_evoluto\\data\\cataloghi\\reports`

\- `E:\\CLONAZIONE\\tpi\_evoluto\\data\\cataloghi\\mapping`

\- `E:\\CLONAZIONE\\tpi\_evoluto\\data\\cataloghi\\.tmp`



In produzione puoi puntare ad un altro path impostando la variabile d’ambiente `CATALOGHI\_BASE\_DIR`.



\## Script di lavoro (CESARE)



Gli script PowerShell di supporto sono in `E:\\CLONAZIONE\\scripts\\CESARE`:



\- `setup\_dati\_cataloghi\_2025-11-20.ps1` → crea l’albero di cartelle `data\\cataloghi\\...`

\- `smoke\_catalogo\_DPI\_2025-11-20.ps1` → esegue uno smoke test end-to-end del Catalogo



\## Endpoint HTTP principali



\- `GET  /api/dpi/csv/template` → header CSV standard (`codice,descrizione,prezzo,gruppo`)

\- `POST /api/dpi/csv/save` → importa CSV grezzo (text/csv) e aggiorna il catalogo JSON

\- `POST /api/dpi/csv/import` → upload CSV (multipart/form-data)

\- `GET  /api/dpi/csv/catalogo` → restituisce il catalogo in JSON

\- `GET  /api/dpi/csv/export` → esporta il catalogo in CSV

\- `GET  /api/dpi/csv/metrics` → piccole metriche per monitoring

\- `GET  /api/dpi/csv/report.html` → mini report HTML (preview prime 50 righe)



\## Test rapidi (porta 8011)



Assumendo FastAPI avviata in locale con:



```bash

uvicorn app.main:app --reload --port 8011
