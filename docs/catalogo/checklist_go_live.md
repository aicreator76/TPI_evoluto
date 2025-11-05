# Checklist Go Live – Catalogo Online

## Backend (API)
- [x] Endpoint `/api/dpi/csv/template` disponibile
- [x] Endpoint `/api/dpi/csv/save` implementato con validazioni soft
- [x] Endpoint `/api/dpi/csv/import-file` per upload multipart
- [x] Endpoint `/api/dpi/csv/catalogo` per lettura JSON
- [x] Endpoint `/api/dpi/csv/export` con filtri (gruppo, colonne)
- [x] Endpoint `/api/dpi/csv/metrics` per statistiche
- [x] Endpoint `/api/dpi/csv/report.html` dashboard HTML
- [x] Validazione soft (errors/warnings separati)
- [x] Merge intelligente (update esistenti, insert nuovi)
- [x] Audit trail (salvataggio file importati con timestamp)

## Documentazione
- [x] Overview catalogo (`docs/catalogo/index.md`)
- [x] API Endpoints (`docs/http/catalogo_endpoints.md`)
- [x] Go Live Checklist (`docs/catalogo/checklist_go_live.md`)
- [x] README catalogo (`docs/catalogo/README.md`)
- [x] Frontend TODO (`docs/frontend/catalogo_flutter_todo.md`)
- [x] MkDocs navigation configurata
- [x] GitHub Pages deployment workflow

## CI/CD
- [ ] Security CI workflow (pip-audit high/critical)
- [ ] Python CI workflow (lint, typecheck, tests)
- [ ] Pre-commit hooks configurati e verdi
- [ ] Deploy Pages workflow verde
- [ ] Badge README aggiornati

## Testing
- [ ] Smoke tests per endpoint principali
- [ ] Test import CSV con encoding misti
- [ ] Test validazioni (errors/warnings)
- [ ] Test export filtrato
- [ ] Test metriche aggregate

## Frontend (Flutter) - TODO
- [ ] Pagina Lista DPI con ricerca/filtri
- [ ] Pagina Dettaglio DPI
- [ ] Pulsante Export CSV + Share
- [ ] Visualizzazione metriche (cards)
- [ ] Upload CSV da mobile
- [ ] Integrazione NFC (opzionale)

## Deployment
- [ ] Environment variables configurate
- [ ] Database/storage path verificato
- [ ] Backup automatico JSON configurato
- [ ] Monitoraggio endpoint attivo
- [ ] Rate limiting configurato
- [ ] CORS policy definita

## Performance
- [ ] Report HTML con limite righe (default 200, max 5000)
- [ ] Cache pip configurata in CI
- [ ] Build MkDocs ottimizzato
- [ ] Compressione response abilitata

## Security
- [ ] Nessun high/critical vulnerability aperto
- [ ] Input validation attiva
- [ ] File upload limite dimensione
- [ ] SARIF reports uploadati
- [ ] Secrets baseline aggiornata

## Accessibilità
- [ ] Report HTML accessibile (semantic HTML)
- [ ] Contrast ratio verificato
- [ ] Keyboard navigation testata
- [ ] Screen reader compatibility

---

**Note**: Questa checklist viene aggiornata progressivamente durante lo sviluppo.
