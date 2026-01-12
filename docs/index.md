# Catalogo DPI â€“ Release LYNX v1

Questa pagina documenta il **primo catalogo DPI reale** caricato in TPI_evoluto
a partire dal catalogo PDF (pagine 11â€“32).

## Contenuto della release

- **38 articoli DPI reali**:
  - Imbracature e cinture
  - Accessori e imbottiture
  - Dispositivi di salvataggio
  - Borse portattrezzi
  - Benne / contenitori di sollevamento
- Strutture generate da LYNX:
  - `catalogo_tpi.csv`  (per import backend)
  - `catalogo_tpi.json` (uso tecnico / AI)
  - `catalogo_tpi.md`   (consultazione rapida / doc)
  - `README_LYNX.txt`   (note di lavorazione)

Percorsi locali:

- CSV: `docs/catalogo/catalogo_tpi.csv`
- JSON: `docs/catalogo/catalogo_tpi.json`
- MD: `docs/catalogo/catalogo_tpi.md`
- README: `docs/catalogo/README_LYNX.txt`
- ZIP rilasciabile:
  `RELEASE_TPI/catalogo/catalogo_tpi_lynx_v1.zip`

## Import nel backend TPI

Endpoint utilizzato:

- `POST /api/dpi/csv/save`  â†’ import diretto del catalogo
- `GET  /api/dpi/csv/catalogo` â†’ verifica contenuto

Ultimo import valido:

- `rows_parsed: 38`
- `total_items: 43` (inclusi DPI demo)

Esempio risposta `/api/dpi/csv/catalogo` (ridotto):

```json
{
  "count": 43,
  "items": [
    {
      "codice": "7330326",
      "descrizione": "TripleA Gr. 1 - Imbracatura anticaduta/di posizionamento...",
      "prezzo": "",
      "gruppo": "imbracatura anticaduta"
    }
  ]
}

---

## ðŸ§© MOSSA 2 â€“ Aggiorna indice Catalogo

Sostituiamo `docs/catalogo/index.md` con una versione piÃ¹ completa.

```powershell
Set-Location "E:\CLONAZIONE\tpi_evoluto"

@'
# Catalogo DPI â€“ Panoramica

Questa sezione raccoglie **tutti i cataloghi DPI** gestiti da TPI_evoluto.

## Stato attuale

- Catalogo reale **LYNX v1** estratto dal PDF (pagg. 11â€“32)
- 38 articoli DPI caricati nel backend
- Import testato tramite `/api/dpi/csv/save`
- Consultazione via `/api/dpi/csv/catalogo`

## File principali

- `catalogo_tpi.csv`  â†’ import/export dati
- `catalogo_tpi.json` â†’ uso tecnico / AI
- `catalogo_tpi.md`   â†’ lettura umana rapida
- `README_LYNX.txt`   â†’ log della lavorazione

Percorsi locali (repo):

```text
docs/catalogo/catalogo_tpi.csv
docs/catalogo/catalogo_tpi.json
docs/catalogo/catalogo_tpi.md
docs/catalogo/README_LYNX.txt

---

## ðŸ§© MOSSA 3 â€“ Badge in homepage (index.md)

Aggiorniamo `docs/index.md` per mostrare che il Catalogo Ã¨ attivo.
(Questa Ã¨ una proposta semplice, non distrugge il resto: se hai giÃ  testo tuo, puoi integrare.)

```powershell
Set-Location "E:\CLONAZIONE\tpi_evoluto"

@'
# TPI_evoluto â€“ Backend & Orchestrator

Benvenuto nel backend ufficiale di **TPI_evoluto**.

## Stato rapido (dicembre 2025)

- âœ… Backend FastAPI + Alembic avviabile in dev (`TPI_SERVER_DEV`)
- âœ… Modulo DPI â€“ Agente 0 attivo (cruscotto + feed n8n)
- âœ… **Catalogo DPI reale LYNX v1 importato** (38 articoli)
- âœ… Documentazione tecnica base pronta per demo in ufficio

## Sezioni principali

- **Stato Backend** â†’ panoramica tecnica backend
- **Cruscotto CESARI/Agenti** â†’ vista operativa per Sovrano/Regina/tecnici
- **Stato TPI (generale)** â†’ sintesi stato progetto
- **Catalogo DPI** â†’ dati reali DPI (CSV/JSON/MD) e release LYNX v1
- **Database / Schema TPI v1** â†’ struttura tabelle

Usa il menu a sinistra per navigare tra le sezioni.- Agente0: [Step2](agente0_STEP2/index.md)
