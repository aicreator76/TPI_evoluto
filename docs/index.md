# Catalogo DPI – Release LYNX v1

Questa pagina documenta il **primo catalogo DPI reale** caricato in TPI_evoluto
a partire dal catalogo PDF (pagine 11–32).

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

- `POST /api/dpi/csv/save`  → import diretto del catalogo
- `GET  /api/dpi/csv/catalogo` → verifica contenuto

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

## 🧩 MOSSA 2 – Aggiorna indice Catalogo

Sostituiamo `docs/catalogo/index.md` con una versione più completa.

```powershell
Set-Location "E:\CLONAZIONE\tpi_evoluto"

@'
# Catalogo DPI – Panoramica

Questa sezione raccoglie **tutti i cataloghi DPI** gestiti da TPI_evoluto.

## Stato attuale

- Catalogo reale **LYNX v1** estratto dal PDF (pagg. 11–32)
- 38 articoli DPI caricati nel backend
- Import testato tramite `/api/dpi/csv/save`
- Consultazione via `/api/dpi/csv/catalogo`

## File principali

- `catalogo_tpi.csv`  → import/export dati
- `catalogo_tpi.json` → uso tecnico / AI
- `catalogo_tpi.md`   → lettura umana rapida
- `README_LYNX.txt`   → log della lavorazione

Percorsi locali (repo):

```text
docs/catalogo/catalogo_tpi.csv
docs/catalogo/catalogo_tpi.json
docs/catalogo/catalogo_tpi.md
docs/catalogo/README_LYNX.txt

---

## 🧩 MOSSA 3 – Badge in homepage (index.md)

Aggiorniamo `docs/index.md` per mostrare che il Catalogo è attivo.
(Questa è una proposta semplice, non distrugge il resto: se hai già testo tuo, puoi integrare.)

```powershell
Set-Location "E:\CLONAZIONE\tpi_evoluto"

@'
# TPI_evoluto – Backend & Orchestrator

Benvenuto nel backend ufficiale di **TPI_evoluto**.

## Stato rapido (dicembre 2025)

- ✅ Backend FastAPI + Alembic avviabile in dev (`TPI_SERVER_DEV`)
- ✅ Modulo DPI – Agente 0 attivo (cruscotto + feed n8n)
- ✅ **Catalogo DPI reale LYNX v1 importato** (38 articoli)
- ✅ Documentazione tecnica base pronta per demo in ufficio

## Sezioni principali

- **Stato Backend** → panoramica tecnica backend
- **Cruscotto CESARI/Agenti** → vista operativa per Sovrano/Regina/tecnici
- **Stato TPI (generale)** → sintesi stato progetto
- **Catalogo DPI** → dati reali DPI (CSV/JSON/MD) e release LYNX v1
- **Database / Schema TPI v1** → struttura tabelle

Usa il menu a sinistra per navigare tra le sezioni.
