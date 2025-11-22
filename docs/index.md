# TPI_evoluto Docs

Benvenuto nella documentazione del progetto **TPI_evoluto**
(pipeline DPI/Funi: ingest, validazione, report e notifiche intelligenti).

- **Repo:** [aicreator76/TPI_evoluto](https://github.com/aicreator76/TPI_evoluto)
- **Site Pages:** <https://aicreator76.github.io/TPI_evoluto/>

---

## Per iniziare in 2 minuti

1. Vai a **Catalogo DPI → Go Live**
   per vedere cosa fa oggi il router CSV e come lanciare lo smoke test.
2. Controlla la sezione **API → OpenAPI**
   per l’elenco completo degli endpoint disponibili.
3. Usa `/health` per verificare che il servizio sia vivo.

---

## Moduli principali

- **Backend FastAPI**: cartella `app/`
  - probes: `/health`, `/version`
  - router CSV DPI: `/api/dpi/csv/*`
- **Catalogo DPI**:
  - template CSV sicuro per Excel
  - import/export da file
  - metriche e report HTML

---

## Per sviluppatori

- Clona il repo:

  ```bash
  git clone https://github.com/aicreator76/TPI_evoluto.git
  cd TPI_evoluto
