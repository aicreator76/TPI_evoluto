# [M2] Agente 0 – n8n notifiche DPI

## Obiettivo
Inviare notifiche automatiche quando:
- un DPI è già scaduto
- un DPI scade entro X giorni (es. 30 / 15 / 1)

## Input minimo
- Endpoint API TPI: /api/dpi/scadenze (mock iniziale)
- Campo chiave: codice_dpi, data_scadenza, stato, email_destinatario

## Primo workflow n8n (Fase 1)
1. Nodo HTTP GET ? chiama /api/dpi/scadenze
2. Nodo IF        ? filtra DPI con scadenza entro X giorni
3. Nodo NOTIFICA  ? per ora LOG su file in E:\CLONAZIONE\n8n_logs\notifiche_test.log

## Requisiti per dire "Fase 1 OK"
- Workflow salvato in n8n con nome: "AGENTE0_DPI_scadenze_F1"
- Screenshot del workflow allegato all'Issue #61
- Log di esempio con almeno 1 DPI in notifica
