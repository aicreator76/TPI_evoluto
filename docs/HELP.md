# Help rapido

## Test webhook (dry-run)
Vedi `README_AELIS_QuickStart.md` per curl, ENV, workflow n8n.

## Errori comuni
- 404 webhook: workflow n8n non attivo o path errato.
- 401/403: manca Authorization tra FastAPI â†” n8n.
- Output non JSON: imposta `response_format: { "type":"json_object" }`.

## Validazione modello
Usa `schemas/aelis_model.schema.json` in Postman (tv4) o nel nodo n8n â€œParse + Validateâ€.
