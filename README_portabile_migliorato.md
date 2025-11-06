# TPI â€” pacchetto portabile (versione migliorata)

Questa versione aggiornata della dashboard offline TPI include diverse migliorie di accessibilitÃ , lâ€™integrazione di una *checklist* DPI digitalizzata e una sezione dedicata alle sovvenzioni. Di seguito trovi le istruzioni per utilizzarla e personalizzarla.

## Come avviare la dashboard

1. **Estrai** lo ZIP del progetto in una cartella qualsiasi del tuo computer.
2. Apri il file `index.html` con un browser moderno (Chromium, Firefox, Edge, Safari). Non occorre installare software; tutti i file sono locali.
3. Dalla barra di navigazione potrai accedere alle varie sezioni, compresa la nuova **Checklist DPI** e la pagina **Sovvenzioni**.

## NovitÃ  principali

- **Navigazione accessibile:** la barra di navigazione Ã¨ stata ristrutturata con un elenco ordinato di link e utilizza lâ€™attributo `ariaâ€‘label` per supportare gli screen reader. Tutti gli elementi cliccabili sono contrassegnati con `role="button"` per facilitare la navigazione tramite tastiera.
- **Migliore codifica:** sono stati corretti caratteri errati (es. `ï¿½`) sostituendoli con il giusto simbolo (trattino, apostrofi tipografici, ecc.).
- **Checklist digitalizzata:** la sezione *Checklist DPI* espone una tabella generata dinamicamente a partire dal file Excel di verifica DPI. I dati sono incorporati nel file sotto forma di array JavaScript (`dpiData`). Per aggiornare la checklist Ã¨ sufficiente esportare nuovamente lâ€™Excel in JSON e sostituire lâ€™array nel file `index.html`.
- **Sezione sovvenzioni:** una nuova pagina riassume i programmi di finanziamento rilevanti (es. INAIL ISI, OT23Â 2026, TransizioneÂ 5.0, SIMESTÂ 394, Voucher DigitaliÂ I4.0 e Nuova Sabatini). Ogni card descrive requisiti, percentuale di contributo e prossimi passi.
- **Stile responsive:** la tabella ha un wrapper con `overflowâ€‘x:auto` che permette lo scroll orizzontale su schermi piccoli. I colori e i contrasti seguono le linee guida WCAG (contrast ratio â‰¥Â 4.5:1)ã€265202959969271â€ L0-L8ã€‘.
- **Pagina di login multilingue:** lâ€™accesso alla dashboard avviene attraverso una schermata di login ispirata allâ€™interfaccia TPI. Supporta italiano, inglese, francese e tedesco: un menu a tendina consente di selezionare la lingua e tutte le etichette (titolo, campi, pulsante, credenziali demo) si adattano automaticamente. I dati di login sono memorizzati in `sessionStorage`, consentendo alla dashboard di riconoscere lâ€™utente e di mostrarne lâ€™eâ€‘mail e il ruolo in alto a destra. Ãˆ presente un pulsante **Esci** per terminare la sessione.

## Come aggiornare la checklist

1. Apri lâ€™Excel `Checklist_Conformita_DPI_Anticaduta_2025-10-08.xlsx` in un programma compatibile.
2. Esporta i dati in formato JSON (ad esempio con Python/pandas) in modo che i campi corrispondano a quelli presenti nel file esistente (ID, Categoria, Norma EN, Marca/Modello, Data primo uso, Scadenza).
3. Sostituisci lâ€™array `dpiData` in fondo al file `index.html` con i nuovi dati JSON.
4. Salva il file e ricarica la pagina nel browser per vedere la checklist aggiornata.

## Personalizzazione

- **Aggiungere nuove sezioni:** puoi creare altre sezioni seguendo la struttura HTML dei capitoli automatici. Assicurati di aggiornare la barra di navigazione con nuovi link e di mantenere la semantica (`<section id="nuova-sezione">`).
- **Aggiornare le sovvenzioni:** modifica il contenuto delle card nella sezione *Sovvenzioni* per riflettere le novitÃ  normative o nuovi bandi. Ogni card Ã¨ un semplice elemento `<a>` con titolo e descrizione.
- **Stile:** per modificare i colori o i font, intervieni nelle variabili CSS dichiarate nella sezione `<style>` dellâ€™`index.html`. Sono presenti variabili per sfondo, carte, testo, accenti, ecc.

## Backup e note operative

- **Backup:** ti consigliamo di copiare lâ€™intera cartella su un supporto esterno (es. `E:\CLONAZIONE\TPI_Progetto_2025-10-08`) come indicato nel memo originaleã€566994465160441â€ L18-L18ã€‘.
- **AccessibilitÃ :** verifica periodicamente la compatibilitÃ  con screen reader e strumenti di navigazione via tastiera. Per elementi interattivi complessi considera lâ€™aggiunta di attributi ARIA (ad esempio `ariaâ€‘label`, `ariaâ€‘expanded`).

Se hai bisogno di assistenza per lâ€™esportazione del JSON o per la manutenzione del codice, sentiti libero di contattare il team di sviluppo.

## Gestione utenti e accesso

La dashboard offline utilizza una schermata di autenticazione che consente di selezionare la lingua e inserire le credenziali. Se lâ€™accesso va a buon fine, la dashboard visualizza in alto a destra lâ€™eâ€‘mail dellâ€™utente e il suo ruolo e memorizza queste informazioni nel `sessionStorage`. Ãˆ inoltre presente un pulsante **Esci** per terminare la sessione e tornare alla pagina di login.

### Credenziali demo

| Ruolo | Eâ€‘mail | Password |
|------|----------------|-----------|
| RSPP | `rspp@demo.tpi` | `Passw0rd!23` |
| HSE | `hse@demo.tpi` | `Passw0rd!23` |
| Datore | `datore@demo.tpi` | `Passw0rd!23` |

Questi account dimostrativi sono utili per testare il sistema. Il mapping tra eâ€‘mail e ruolo Ã¨ definito nello script di `index.html` e puÃ² essere esteso modificando lâ€™oggetto `roleMap`.

### Selezione della lingua

La schermata di login dispone di un menu per la scelta della lingua (italiano, inglese, francese, tedesco). La lingua selezionata viene salvata e riutilizzata per tradurre automaticamente le etichette e i testi dellâ€™interfaccia.

### Logout

Il pulsante **Esci**, posizionato nella barra superiore, cancella la sessione e reindirizza lâ€™utente al modulo di login. Per personalizzare lâ€™etichetta in altre lingue, modifica la chiave `logoutButton` nellâ€™oggetto `translations` di `index.html`.
