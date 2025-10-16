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

## Dashboard pubblicata

🚀 **La dashboard è LIVE su GitHub Pages:**
- **URL**: https://aicreator76.github.io/TPI_evoluto/
- **Deploy automatico**: ogni push su `main` attiva GitHub Actions
- **Status**: ✅ Operativo

### Test locali
```bash
# Con Python
python3 -m http.server 8080

# Oppure con Node.js
npx http-server -p 8080
```
Poi apri `http://localhost:8080` nel browser.

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

## Licenza
Vedi `LICENSE` (MIT).