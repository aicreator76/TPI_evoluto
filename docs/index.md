# TPI – Tecnologia • Prevenzione • Innovazione

> **Suite enterprise** per DPI, impianti anticaduta e INOX.  
> Progettata per Datore di lavoro, RSPP, HSE, Operatori e Revisori.

[Scarica Demo Windows](download.md){ .md-button } [Scarica APK Android](download.md){ .md-button }

## Perché TPI è enterprise
- Ruoli avanzati, tracciamento eventi, audit log
- Export **PDF/Excel** e backup cifrati
- Flussi **NFC** (solo HSE) e foto/video pre-uso con **geotag**
- AI assistita con livelli di riservatezza selezionabili
- Multilingua (IT, DE/AT, DE, EN, ES, FR)

!!! tip "Obiettivo del mese"
    Rilascio **TPI v4.1 – IKAR–TECI** con roadmap visibile e KPI settimanali.

## Catalogo DPI – Go Live

🚀 **Nuovo!** Sistema di gestione catalogo DPI ora disponibile con API REST complete.

### Funzionalità principali
- **Import CSV**: caricamento e validazione soft con merge intelligente
- **Export filtrato**: esportazione per gruppo e colonne personalizzabili
- **Report HTML**: dashboard interattiva con metriche e anteprima
- **API REST**: endpoint completi per integrazione con app esterne

### Link rapidi
- [📖 Overview Catalogo](catalogo/index.md) – Guida completa
- [🔌 API Endpoints](http/catalogo_endpoints.md) – Documentazione endpoint REST
- [✅ Go Live Checklist](catalogo/checklist_go_live.md) – Lista verifiche pre-produzione
- [📱 Frontend TODO](frontend/catalogo_flutter_todo.md) – Roadmap app mobile

### Prova rapida

**PowerShell**:
```powershell
# Visualizza report HTML
Start-Process "http://localhost:8000/api/dpi/csv/report.html"

# Scarica metriche
Invoke-RestMethod -Uri "http://localhost:8000/api/dpi/csv/metrics"
```

**curl**:
```bash
# Visualizza metriche
curl http://localhost:8000/api/dpi/csv/metrics | jq

# Esporta catalogo
curl "http://localhost:8000/api/dpi/csv/export?gruppo=ANTICADUTA" -o export.csv
```

---

## Moduli principali
- **DPI** – Scadenze semaforo, notifiche 30/15/1, revisione con evidenze
- **Impianti anticaduta** – Wizard indirizzo → satellite → Q&A
- **INOX/Kanban** – Schema ordini aperti per grandi clienti
- **IKAR** – Inserimento catalogo e lead tracking

---
[**Sostieni Camelot 🚀**](fondi.md) · [Privacy](legal/privacy.md) · [Cookie](legal/cookie.md)
