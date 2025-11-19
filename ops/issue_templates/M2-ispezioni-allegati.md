## Contesto
Il cuore del valore sta nel registrare ispezioni tracciabili, con domande, esito e allegati (foto, pdf, ecc.).

## Obiettivo
Aggiungere la gestione completa delle ispezioni per:
- DPI
- impianti anticaduta

## Task
- [ ] Definire modello `Ispezione` con:
  - riferimento a DPI o impianto
  - data
  - esito
  - note
  - utente che ha eseguito
- [ ] Definire modello `Allegato` con:
  - tipo (foto, pdf, altro)
  - path/storage ref
  - collegamento a DPI/impianto/ispezione
- [ ] Implementare API:
  - [ ] creare ispezione
  - [ ] allegare file (anche solo stub iniziale, es. path locale)
  - [ ] elencare storico ispezioni per DPI/impianto
- [ ] Collegare esito ispezione al cambio stato DPI/impianto

## Criteri di accettazione
- [ ] È possibile creare un’ispezione per un DPI o impianto e vederla nello storico
- [ ] È possibile associare almeno un allegato (anche se storage iniziale è semplice)
- [ ] Lo stato DPI/impianto viene aggiornato in base all’esito (es. NO = riparazione/scarto)
