# AGENTI DEL REGNO – OVERVIEW (MindStudio)

Questa pagina elenca gli **agenti digitali** a servizio della Regina e del Sovrano,
configurati su MindStudio per supportare il progetto **TPI_evoluto**.

---

## 1. Agente "COMPITI-REGINA"

- **Piattaforma:** MindStudio (piano Free)
- **Ruolo:** Assistente quotidiano della Regina
- **Cosa fa:**
  - Legge il **CRUSCOTTO_COMPITI_REGINA_*.md**
  - Legge gli **ORDINI_ORCHESTRA_PRIME_*.md**
  - Restituisce ogni giorno:
    - il **semaforo progetto**,
    - **3 TODO POWER** per il Sovrano,
    - avvisi se qualcosa è fermo da troppi giorni.
- **Limiti:**
  - Non crea né modifica file.
  - Non esegue comandi, fa solo lettura + sintesi.

File SPEC di riferimento:
- `docs/orchestrator/AGENTE_COMPITI_REGINA_SPEC.md`

---

## 2. Agente "ORCHESTRA-PRIME CHECKER"

- **Piattaforma:** MindStudio (piano Free)
- **Ruolo:** Verificatore stato ordini ORCHESTRA-PRIME
- **Cosa fa:**
  - Legge il file ordini del giorno:
    - `docs/ORDINI_ORCHESTRA_PRIME_YYYY-MM-DD.md`
  - Per ciascun compito:
    - valuta se è **eseguito (✅)**, **in corso (⚠️)** o **bloccato (🔴)**,
    - propone una **prossima azione sintetica** (1 riga).
- **Limiti:**
  - Non cambia gli ordini.
  - Non decide nuove priorità: si limita a **leggere e valutare**.

File SPEC di riferimento:
- `docs/orchestrator/AGENTE_ORCHESTRA_CHECK_SPEC.md`

---

## 3. Piano MindStudio e obiettivo

- **Piano usato:** MindStudio **Free**
  - Utilizziamo **2 agenti** principali:
    - `COMPITI-REGINA`
    - `ORCHESTRA-PRIME CHECKER`
- **Obiettivo:**
  - Supportare il lavoro reale su **TPI_evoluto** (cruscotti, ordini, stato progetto).
  - Nessun uso per marketing generico o demo vuote.

---

## 4. Nota finale per la Regina

> Questi sono i **primi 2 servitori digitali della Corona**.
>
> Se dimostrano di funzionare, saranno estesi, clonati e potenziati
> per seguire altri fronti del Regno (DPI, n8n, CESARE/CESARONI, ecc.).
