## Contesto
Al momento le API sono di fatto "nude". Per esporre TPI_evoluto oltre il perimetro interno servono autenticazione e ruoli minimi.

## Obiettivo
Implementare autenticazione basata su JWT con ruoli base:
- RSPP
- HSE
- Datore
- Operatore
- Revisore DPI

## Task
- [ ] Definire modello `User` con riferimento a `tenant` e `role`
- [ ] Implementare registrazione/creazione utenti (anche solo via script/admin)
- [ ] Implementare login con rilascio JWT (access + optional refresh)
- [ ] Implementare dipendenza FastAPI che:
  - valida il token
  - carica utente e ruolo
  - rende disponibili `current_user` e `current_tenant`
- [ ] Limitare accesso a una prima API di prova in base al ruolo

## Criteri di accettazione
- [ ] Un utente può autenticarsi e ottenere un JWT valido
- [ ] Chiamate senza JWT ricevono 401/403
- [ ] Almeno un endpoint dimostra differenza di permessi fra ruoli (es. Datore = sola lettura, RSPP = scrittura)
