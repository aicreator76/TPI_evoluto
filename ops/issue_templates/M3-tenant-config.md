## Contesto
Clienti enterprise possono richiedere specifiche sulla localizzazione dati e configurazioni per tenant.

## Obiettivo
Introdurre configurazione per tenant che permetta di gestire:
- impostazioni di base
- preferenze di data residency (almeno a livello logico per ora)

## Task
- [ ] Definire modello `TenantConfig` con campi:
  - data_residency (es. EU, IT)
  - impostazioni di sicurezza (place holder)
- [ ] Collegare `TenantConfig` a `tenant`
- [ ] Esporre API per lettura/modifica config (solo ruoli di alto livello)
- [ ] Documentare in `docs/enterprise/tenant_config.md` come funziona il modello

## Criteri di accettazione
- [ ] Ogni tenant ha una configurazione associata
- [ ] È possibile leggere/modificare la config tramite API protette
- [ ] La documentazione spiega chiaramente come estendere la parte Data Residency
