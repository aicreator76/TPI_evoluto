# TPI — pacchetto portabile (versione migliorata)

Questa versione aggiornata della dashboard offline TPI include diverse migliorie di accessibilità, l’integrazione di una *checklist* DPI digitalizzata e una sezione dedicata alle sovvenzioni. Di seguito trovi le istruzioni per utilizzarla e personalizzarla.

## Come avviare la dashboard

1. **Estrai** lo ZIP del progetto in una cartella qualsiasi del tuo computer.
2. Apri il file `index.html` con un browser moderno (Chromium, Firefox, Edge, Safari). Non occorre installare software; tutti i file sono locali.
3. Dalla barra di navigazione potrai accedere alle varie sezioni, compresa la nuova **Checklist DPI** e la pagina **Sovvenzioni**.

## Novità principali

- **Navigazione accessibile:** la barra di navigazione è stata ristrutturata con un elenco ordinato di link e utilizza l’attributo `aria‑label` per supportare gli screen reader. Tutti gli elementi cliccabili sono contrassegnati con `role="button"` per facilitare la navigazione tramite tastiera.
- **Migliore codifica:** sono stati corretti caratteri errati (es. `�`) sostituendoli con il giusto simbolo (trattino, apostrofi tipografici, ecc.).
- **Checklist digitalizzata:** la sezione *Checklist DPI* espone una tabella generata dinamicamente a partire dal file Excel di verifica DPI. I dati sono incorporati nel file sotto forma di array JavaScript (`dpiData`). Per aggiornare la checklist è sufficiente esportare nuovamente l’Excel in JSON e sostituire l’array nel file `index.html`.
- **Sezione sovvenzioni:** una nuova pagina riassume i programmi di finanziamento rilevanti (es. INAIL ISI, OT23 2026, Transizione 5.0, SIMEST 394, Voucher Digitali I4.0 e Nuova Sabatini). Ogni card descrive requisiti, percentuale di contributo e prossimi passi.
- **Stile responsive:** la tabella ha un wrapper con `overflow‑x:auto` che permette lo scroll orizzontale su schermi piccoli. I colori e i contrasti seguono le linee guida WCAG (contrast ratio ≥ 4.5:1)【265202959969271†L0-L8】.
- **Pagina di login multilingue:** l’accesso alla dashboard avviene attraverso una schermata di login ispirata all’interfaccia TPI. Supporta italiano, inglese, francese e tedesco: un menu a tendina consente di selezionare la lingua e tutte le etichette (titolo, campi, pulsante, credenziali demo) si adattano automaticamente. I dati di login sono memorizzati in `sessionStorage`, consentendo alla dashboard di riconoscere l’utente e di mostrarne l’e‑mail e il ruolo in alto a destra. È presente un pulsante **Esci** per terminare la sessione.

## Come aggiornare la checklist

1. Apri l’Excel `Checklist_Conformita_DPI_Anticaduta_2025-10-08.xlsx` in un programma compatibile.
2. Esporta i dati in formato JSON (ad esempio con Python/pandas) in modo che i campi corrispondano a quelli presenti nel file esistente (ID, Categoria, Norma EN, Marca/Modello, Data primo uso, Scadenza).
3. Sostituisci l’array `dpiData` in fondo al file `index.html` con i nuovi dati JSON.
4. Salva il file e ricarica la pagina nel browser per vedere la checklist aggiornata.

## Personalizzazione

- **Aggiungere nuove sezioni:** puoi creare altre sezioni seguendo la struttura HTML dei capitoli automatici. Assicurati di aggiornare la barra di navigazione con nuovi link e di mantenere la semantica (`<section id="nuova-sezione">`).
- **Aggiornare le sovvenzioni:** modifica il contenuto delle card nella sezione *Sovvenzioni* per riflettere le novità normative o nuovi bandi. Ogni card è un semplice elemento `<a>` con titolo e descrizione.
- **Stile:** per modificare i colori o i font, intervieni nelle variabili CSS dichiarate nella sezione `<style>` dell’`index.html`. Sono presenti variabili per sfondo, carte, testo, accenti, ecc.

## Backup e note operative

- **Backup:** ti consigliamo di copiare l’intera cartella su un supporto esterno (es. `E:\CLONAZIONE\TPI_Progetto_2025-10-08`) come indicato nel memo originale【566994465160441†L18-L18】.
- **Accessibilità:** verifica periodicamente la compatibilità con screen reader e strumenti di navigazione via tastiera. Per elementi interattivi complessi considera l’aggiunta di attributi ARIA (ad esempio `aria‑label`, `aria‑expanded`).

Se hai bisogno di assistenza per l’esportazione del JSON o per la manutenzione del codice, sentiti libero di contattare il team di sviluppo.

## Gestione utenti e accesso

La dashboard offline utilizza una schermata di autenticazione che consente di selezionare la lingua e inserire le credenziali. Se l’accesso va a buon fine, la dashboard visualizza in alto a destra l’e‑mail dell’utente e il suo ruolo e memorizza queste informazioni nel `sessionStorage`. È inoltre presente un pulsante **Esci** per terminare la sessione e tornare alla pagina di login.

### Credenziali demo

| Ruolo | E‑mail | Password |
|------|----------------|-----------|
| RSPP | `rspp@demo.tpi` | `Passw0rd!23` |
| HSE | `hse@demo.tpi` | `Passw0rd!23` |
| Datore | `datore@demo.tpi` | `Passw0rd!23` |

Questi account dimostrativi sono utili per testare il sistema. Il mapping tra e‑mail e ruolo è definito nello script di `index.html` e può essere esteso modificando l’oggetto `roleMap`.

### Selezione della lingua

La schermata di login dispone di un menu per la scelta della lingua (italiano, inglese, francese, tedesco). La lingua selezionata viene salvata e riutilizzata per tradurre automaticamente le etichette e i testi dell’interfaccia.

### Logout

Il pulsante **Esci**, posizionato nella barra superiore, cancella la sessione e reindirizza l’utente al modulo di login. Per personalizzare l’etichetta in altre lingue, modifica la chiave `logoutButton` nell’oggetto `translations` di `index.html`.
