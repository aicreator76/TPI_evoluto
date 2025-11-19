## Contesto
Una delle differenze chiave rispetto ai concorrenti è la presenza forte del mondo impianti anticaduta.

## Obiettivo
Aggiungere entità e API per gestire impianti anticaduta:
- linee vita
- punti di ancoraggio
- scale fisse, parapetti, ecc. (almeno struttura generica)

## Task
- [ ] Definire modello `ImpiantoAnticaduta` con campi:
  - tipo impianto
  - ubicazione (testo + eventuali coordinate)
  - azienda/tenant
  - stato (attivo/out of service)
- [ ] Implementare API CRUD per impianti
- [ ] Collegare impianti alle ispezioni
- [ ] Documentare le API nel README/docs

## Criteri di accettazione
- [ ] È possibile creare e gestire impianti anticaduta per ogni azienda
- [ ] Gli impianti compaiono nelle relazioni con ispezioni e DPI
- [ ] Tutto è filtrato per tenant in modo consistente
