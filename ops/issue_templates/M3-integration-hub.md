## Contesto
Per integrarsi con ERP/HR/n8n serve un punto unico dove configurare e spedire eventi standard.

## Obiettivo
Creare un modulo di integrazione che:
- espone webhook/eventi per sistemi esterni
- consente di configurare "destinazioni" per tenant

## Task
- [ ] Definire tabella `IntegrationEndpoint` (tenant, url, tipo evento, stato)
- [ ] Implementare API per CRUD degli endpoint di integrazione (solo ruoli alti)
- [ ] Sopra l'orchestratore, aggiungere invio eventi a endpoint attivi:
  - DPI in scadenza
  - impianti in scadenza
  - corsi/attestati in scadenza (anche stub)
- [ ] Documentare formato degli eventi (JSON) in `docs/integration/events.md`

## Criteri di accettazione
- [ ] È possibile configurare almeno un endpoint di integrazione per tenant
- [ ] Un evento orchestratore genera una chiamata HTTP verso l'endpoint configurato
- [ ] La documentazione definisce chiaramente struttura e significato degli eventi
