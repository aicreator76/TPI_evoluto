# 05 – TODO UNIFICAZIONE ENTRO LA DEMO (LUNEDÌ)

## Fase 1 – Allineamento rapido per demo

- [ ] Confermare percorso locale repo STAGING:
      `E:\CLONAZIONE\TPI_api_staging`
- [ ] Aprire e leggere:
      - `11_diff_struttura_cartelle_2025-12-10.txt`
      - `21_file_py_tpi_evoluto_2025-12-10.txt`
      - `22_file_py_tpi_api_staging_2025-12-10.txt`
- [ ] Individuare in entrambi i progetti:
      - main FastAPI (es. `app/main.py` vs `app.py` o similare)
      - cartelle `app/api/` o equivalenti in STAGING
- [ ] Compilare la tabella in:
      `04_MAPPATURA_ENDPOINT_TPI_vs_STAGING_2025-12-10.md`
      per almeno:
      - healthcheck
      - version
      - 1–2 endpoint di listino (es. ACCESSORI)

## Fase 2 – Codice da toccare per l’unificazione minima

- [ ] In `TPI_evoluto`:
      - [ ] Verificare che gli endpoint “vetrina” abbiano:
            - nomi chiari
            - risposte stabili
            - test associati (pytest)
- [ ] In `TPI_api_staging`:
      - [ ] Allineare path e payload degli endpoint scelti
      - [ ] Aggiornare (se serve) il file principale FastAPI
      - [ ] Aggiornare o creare test minimi per gli endpoint demo

## Fase 3 – Storytelling tecnico per lunedì

- [ ] Preparare breve narrazione:
      - “TPI_evoluto = motore”
      - “TPI_api_staging = vetrina staging su Render”
- [ ] Evidenziare:
      - 2–3 endpoint chiave già funzionanti in staging
      - come vengono alimentati dal motore TPI_evoluto
- [ ] Annotare eventuali limiti noti:
      - endpoint ancora solo nel motore
      - parti non ancora esposte in staging

Questo TODO è la checklist ufficiale per arrivare alla demo
con un’unificazione **credibile, reale e presentabile**.
