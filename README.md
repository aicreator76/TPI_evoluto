# TPI / AELIS – Dashboard & Agenti (#7 Operativo, #8 Ordini DPI)

Questo repository ospita la dashboard TPI e l’integrazione con gli agenti AELIS:
- **Agente #7 – Operativo Dashboard:** notifica scadenze DPI, badge, KPI.
- **Agente #8 – Ordini DPI:** crea/chiude ordini di sostituzione DPI (work orders).

## Tecnologie
- **n8n** (webhook + orchestrazione, HTTP-only verso OpenAI)
- **FastAPI** (+ Firestore) per esecuzione azioni reali (opzionale)
- **Postman/Newman** per test end-to-end
- **GitHub Actions** per CI (collection Postman)
- Frontend: HTML/CSS/JS (o React, se presente)

## Installazione (locale)
1. Node 18+, (opzionale) Python 3.11+, n8n in esecuzione.
2. Variabili n8n → Settings → Variables:
   - `OPENAI_API_KEY`, `FASTAPI_BASE_URL`, `FASTAPI_JWT`, `TZ=Europe/Amsterdam`
3. Importa i workflow n8n da `n8n/Agente7_ReturnModel.json` e `n8n/Agente8_WorkOrders.json`.

## Avvio rapido
- **Test via curl**: vedi `README_AELIS_QuickStart.md` / sezione Quick Start.
- **CI Postman**: GitHub → Actions → “AELIS Agents – Postman CI” → Run workflow.

## Flusso utente (esempio)
1. Agente #7 riceve DPI in scadenza → **notify** + badge rosso/giallo.
2. Agente #8 riceve l’evento → **plan**: crea ordine “sostituzione DPI”.
3. Tecnico sostituisce e verifica → **update**: se tutti authorized=true → chiusura ordine.
4. Dashboard aggiorna badge e KPI.

## Qualità & Accessibilità
- **WLL badge fix**: evita “NaN giorni” per date mancanti o non ISO.
- **Grafici & trend**: card KPI con andamento e alert personalizzati (critico/attenzione/ok).
- **Accessibilità**: contrasto ≥ 4.5:1, focus visibile, ARIA per componenti interattivi, supporto keyboard/screen reader.
- Dettagli in `docs/ACCESSIBILITY.md`.

## Scripts operativi
- `npm start` - Avvia il server (porta 8080)
- `npm run prod` - Avvia in modalità produzione
- `npm run grand` - Grand opening (quality gate + seed + server)
- `npm run quality-gate` - Check di qualità (Node version, npm audit, endpoints)
- `npm run verify-plugins` - Verifica firme plugin con ed25519
- `npm run policy-check` - Controlla policy OPA
- `npm run seed:demo` - Invia eventi demo via WebSocket
- `npm run chaos:smoke` - Test di carico chaos via WebSocket
- `npm run snapshot` - Backup database
- `npm run restore` - Ripristina database da backup
- `npm run sign-plugin` - Firma un plugin

## Endpoints disponibili
- `GET /health` - Health check con stato safe mode
- `GET /metrics` - Metriche formato Prometheus
- `GET /mode` - Modalità corrente (safe mode, config, env)
- `GET /observability/metrics` - Redirect a /metrics

## Deployment
- **Fly.io**: Configurato con `fly.toml` (Dockerfile, HTTPS, autoscaling, metrics)
- **Cloudflare Workers**: API stub in `server/workers/api.js` con `wrangler.toml`
- **Safe mode**: Impostare `AELIS_SAFE_MODE=true` per disabilitare caricamento plugin

## Licenza
Vedi `LICENSE` (MIT).