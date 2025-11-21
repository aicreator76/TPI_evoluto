# TPI_evoluto – README POWER

Questo documento descrive lo stato reale del progetto **TPI_evoluto**
e come funziona oggi la parte di **build DEMO TPI** gestita da CESARE.

---

## Cos'è TPI_evoluto

- Backend FastAPI per gestione DPI, anticaduta e flussi TPI.
- Pensato per girare dietro un reverse proxy (Nginx/Traefik) o in locale.
- Integrazione prevista con:
  - app Flutter / mobile,
  - automazioni CESARE (PowerShell),
  - sistemi di log e report (LIONEL / REPORT_DELTA).

---

## Componenti principali del Regno tecnico

- **Repo backend**: `E:\CLONAZIONE\tpi_evoluto`
- **Release locali**: `E:\CLONAZIONE\RELEASE_TPI\YYYY-MM-DD\`
- **Log release**: `E:\CLONAZIONE\LOG\RELEASE_TPI_YYYY-MM-DD.log`
- **Status giornaliero**: `E:\CLONAZIONE\RELEASE_TPI\STATUS_TPI_YYYY-MM-DD.json`
- **Agent CESARE**: script in `E:\CLONAZIONE\scripts\CESARE\`
- **Maestro LIONEL**: script in `E:\CLONAZIONE\MAESTRO_LIONEL\`

---

## Build TPI – stato attuale

Oggi il Regno ha due livelli di build per TPI:

1. **DEMO locale con CESARE**
2. **Build TPI (stub) su GitHub Actions**

Non esistono ancora **.exe** e **.apk** reali, firmati e pronti per i clienti.
Tutto ciò che segue è pensato per **testare il flusso**, non per consegnare prodotti finali.

### 1. CESARE_RELEASE_TPI_DEMO.ps1 (DEMO locale)

Script principale (lato Sovrano) per simulare una release giornaliera.

- Percorso script:
  `E:\CLONAZIONE\CESARE_COMANDI\scripts\CESARE_RELEASE_TPI_DEMO.ps1`
- Esempio di comando:

  ```powershell
  powershell -NoProfile -ExecutionPolicy Bypass `
    -File "E:\CLONAZIONE\CESARE_COMANDI\scripts\CESARE_RELEASE_TPI_DEMO.ps1" `
    -Version "vTEST-DEMO-002"
