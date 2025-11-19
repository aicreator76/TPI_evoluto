## Contesto
Per giocare in modalità enterprise è fondamentale che più aziende (tenant) possano convivere nello stesso sistema, senza condividere dati.

## Obiettivo
Introdurre il concetto di tenant in tutto il backend:
- ogni utente appartiene a un tenant
- ogni risorsa (DPI, impianti, operatori, ispezioni, ecc.) è sempre legata a un tenant
- tutte le query sono filtrate per `current_tenant`

## Task
- [ ] Aggiungere campo `tenant_id` alle tabelle principali
- [ ] Aggiungere relazione tra `tenant` e utenti/DPI/impianti/… nello schema
- [ ] Aggiornare repository/ORM per filtrare sempre per `tenant_id`
- [ ] Aggiornare endpoint esistenti per utilizzare `current_tenant` dalle info utente
- [ ] Aggiungere test che dimostrino che dati di tenant A non sono visibili da tenant B

## Criteri di accettazione
- [ ] Nessuna entità critica può essere creata/scritta senza contesto tenant
- [ ] Query cross-tenant non sono possibili via API (403 o nessun risultato)
- [ ] Test automatici a copertura del multi-tenant logico
