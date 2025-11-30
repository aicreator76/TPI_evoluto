## Contesto
Serve un "Agente 0" reale che inizi ad agire come orchestratore delle scadenze, base per notifiche e automazioni.

## Obiettivo
Implementare un job di orchestrazione che:
- legge DPI e impianti
- calcola scadenze (30/15/1 giorni)
- genera una coda di eventi in tabella o queue

## Task
- [ ] Definire tabella `OrchestratorEvent` (tipo evento, riferimento, tenant, data evento, stato)
- [ ] Implementare job (es. comando CLI o task schedulato) che:
  - [ ] legge scadenze DPI
  - [ ] legge scadenze impianti
  - [ ] crea eventi per soglie 30/15/1 giorni
- [ ] Aggiungere endpoint per leggere eventi in coda per un tenant
- [ ] Documentare come lanciare il job

## Criteri di accettazione
- [ ] Eseguendo il job su un DB di test vengono creati eventi coerenti con le scadenze
- [ ] Gli eventi sono filtrabili per tenant e tipo
- [ ] Esiste documentazione minima su come collegare questi eventi a n8n/CESARE in futuro
