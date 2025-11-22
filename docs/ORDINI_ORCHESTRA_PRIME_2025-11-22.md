# ORDINI DI LAVORO – ORCHESTRA-PRIME
Data: 2025-11-22
Fronte scelto: **003–LMB / Documentazione & Cruscotti**
Supporto: mini-task per **002–GIT**
Stato **001–BLD**: solo sorveglianza (niente build pesanti oggi)

---

## 🔵 Compito 1 – Congelare il REGALO (docs/theme-refresh) – 002–GIT + Orchestratrice

**Obiettivo:** mettere al sicuro il nuovo tema docs senza toccare `main`.

### Passi eseguiti

```powershell
cd E:\CLONAZIONE\tpi_evoluto
git checkout docs/theme-refresh
git status
git add mkdocs.yml docs\index.md
git commit -m "Refresh tema docs Material + homepage TPI_evoluto"
git push -u origin docs/theme-refresh
