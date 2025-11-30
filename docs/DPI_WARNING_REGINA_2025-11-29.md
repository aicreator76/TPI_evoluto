# Stato DPI in warning – Relazione per la Regina
Data: 29/11/2025
Fonte tecnica: `E:\CLONAZIONE\tpi_evoluto\logs\agente0_dashboard.json`

---

## 1️⃣ Riepilogo numerico modulo DPI

Alla data dell’ultimo controllo automatico, il modulo DPI riporta:

- **Totale DPI monitorati:** 5
- **DPI in regola (OK):** 3
- **DPI in warning (≤ 30 giorni):** 2
- **DPI scaduti:** 0
- **Anomalie dati (date errate / non realistiche):** 0

Frase pronta per verbale / mail:

> «Alla data odierna il sistema DPI automatico riporta 5 dispositivi totali, di cui 3 in regola e 2 in stato di warning (scadenza entro 30 giorni). Non risultano DPI scaduti né anomalie nei dati.»

---

## 2️⃣ Dettaglio DPI in warning (da compilare)

I dati di dettaglio dei DPI in warning vanno presi dal file:
`E:\CLONAZIONE\tpi_evoluto\logs\agente0_dashboard.json`
(campi: `id_dpi`, `descrizione`, `data_scadenza`, `gg_alla_scad_verifica`, eventuale assegnatario).

Compilare la tabella qui sotto con i **2 DPI in warning**:

| ID DPI        | Descrizione / Modello        | Assegnato a        | Data scadenza utilizzo | Giorni alla scadenza | Azione suggerita                      |
|--------------|------------------------------|--------------------|------------------------|----------------------|----------------------------------------|
| **DA_COMPILARE** | **DA_COMPILARE**              | **DA_COMPILARE**   | **DA_COMPILARE**       | **DA_COMPILARE**     | Esempio: Ricontrollo entro 7 giorni    |
| **DA_COMPILARE** | **DA_COMPILARE**              | **DA_COMPILARE**   | **DA_COMPILARE**       | **DA_COMPILARE**     | Esempio: Programmare sostituzione DPI  |

Suggerimenti per la colonna “Azione suggerita”:
- **Ricontrollo entro X giorni** → se mancano ancora parecchi giorni ma il DPI è vicino alla scadenza.
- **Programmare sostituzione** → se la scadenza è molto ravvicinata (es. entro 7–10 giorni).
- **Verifica assegnazione** → se non è chiaro a chi è assegnato o se l’utilizzo reale è cambiato.

---

## 3️⃣ Note operative per Datore di Lavoro / RSPP

1. **Nessun DPI risulta scaduto:** il sistema non segnala, allo stato attuale, dispositivi oltre la data di scadenza.
2. **Due DPI in warning:** entrambi richiedono una decisione operativa (ricontrollo o sostituzione programmata).
3. **Tracciabilità:** ogni aggiornamento dei dati deve avvenire su:
   - `E:\CLONAZIONE\tpi_evoluto\data\dpi_input.xlsx`
   seguito da un nuovo lancio di:
   - `.\run_agente0.ps1` (eseguito dall’operatore tecnico).

Frase sintetica per la Regina:

> «I DPI risultano sotto controllo: nessun dispositivo scaduto, due in finestra di attenzione a 30 giorni. È consigliata una verifica mirata su questi due dispositivi per decidere se programmare sostituzione o semplice ricontrollo.»

---

## 4️⃣ Mini-checklist prima della riunione DPI

Questa sezione è per l’operatore tecnico (CESARE / Agente 0) prima del confronto con il Datore/RSPP.

1. **Rigenerare i dati DPI**
   - Posizionarsi nella cartella di lavoro:
     `E:\CLONAZIONE\tpi_evoluto`
   - Eseguire il controllo automatico DPI (Agente 0):
     - (Comando da lanciare in PowerShell, NON qui nel file)
       `.\run_agente0.ps1`

2. **Verificare il cruscotto numerico**
   - Aprire il file:
     `E:\CLONAZIONE\tpi_evoluto\logs\agente0_cruscotto.json`
   - Controllare che i numeri riportati corrispondano alla situazione che verrà presentata in riunione.

3. **Recuperare i dettagli dei 2 DPI in warning**
   - Aprire:
     `E:\CLONAZIONE\tpi_evoluto\logs\agente0_dashboard.json`
   - Cercare le righe con `stato_scadenza = "WARNING"`
   - Copiare per ciascuna riga:
     - id_dpi
     - descrizione
     - eventuale assegnatario
     - data_scadenza
     - gg_alla_scad_verifica

4. **Compilare la tabella della sezione 2️⃣**
   - Aggiornare le due righe della tabella con i dati reali.
   - Salvare questo file (`DPI_WARNING_REGINA_2025-11-29.md`) dopo le modifiche.

5. **Rilettura finale**
   - Verificare che:
     - i numeri in Sezione 1️⃣ coincidano con il cruscotto JSON,
     - i due DPI in warning siano presenti in tabella,
     - le azioni suggerite siano coerenti con la politica DPI aziendale (sostituzione / ricontrollo).

---

## 5️⃣ Messaggio finale per la Cronaca del Regno

> «In data 29/11/2025 il Modulo DPI del Regno ha registrato 5 dispositivi totali, con 3 DPI in piena regola e 2 in finestra di warning a 30 giorni. Nessun DPI risulta scaduto, nessuna anomalia sui dati. È stata predisposta una relazione specifica per i due dispositivi in warning, con proposta di azione mirata per evitare qualsiasi condizione di rischio.»
