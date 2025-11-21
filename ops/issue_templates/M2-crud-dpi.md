## Contesto
Per usare TPI in produzione serve una gestione DPI completa, con stati che riflettano la realtà operativa.

## Obiettivo
Implementare CRUD DPI con questi stati minimi:
- attivo
- in magazzino
- in riparazione
- scartato
- non trovato (solo come stato risultante da ispezione)

## Task
- [ ] Definire modello DPI in DB con attributi principali (codice, seriale, modello, categoria, ecc.)
- [ ] Implementare API:
  - [ ] create DPI
  - [ ] read (singolo e lista con filtri)
  - [ ] update
  - [ ] soft delete / dismissione
- [ ] Implementare gestione cambio stato con regole base (es. da attivo → riparazione solo tramite ispezione)
- [ ] Documentare le API DPI in OpenAPI/README

## Criteri di accettazione
- [ ] È possibile creare, leggere, aggiornare, cambiare stato e dismettere un DPI via API
- [ ] Gli stati sono allineati al dominio sicurezza DPI
- [ ] I DPI sono sempre filtrati per tenant e accessibili solo a ruoli autorizzati
