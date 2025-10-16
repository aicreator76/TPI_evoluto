# Guida al Deploy - TPI Dashboard

## 🚀 Deploy su GitHub Pages (Automatico)

La dashboard è configurata per il deploy automatico su GitHub Pages.

### Configurazione iniziale (una tantum)

1. Vai su GitHub → Repository Settings
2. Nella sezione "Pages":
   - **Source**: GitHub Actions
   - Salva le modifiche

3. Il deploy avverrà automaticamente al prossimo push su `main`

### URL della dashboard

Una volta attivato GitHub Pages, la dashboard sarà disponibile su:
```
https://aicreator76.github.io/TPI_evoluto/
```

## 🔄 Deploy automatico

Il workflow `.github/workflows/pages.yml` si attiva automaticamente:
- ✅ Ad ogni push sul branch `main`
- ✅ Manualmente da GitHub Actions → "Deploy to GitHub Pages" → Run workflow

## 💻 Test in locale

### Opzione 1: Python HTTP Server
```bash
cd /path/to/TPI_evoluto
python3 -m http.server 8080
```
Apri http://localhost:8080

### Opzione 2: Node.js HTTP Server
```bash
cd /path/to/TPI_evoluto
npx http-server -p 8080
```
Apri http://localhost:8080

### Opzione 3: Live Server (VS Code)
1. Installa l'estensione "Live Server"
2. Apri `index.html`
3. Click destro → "Open with Live Server"

## 🔍 Verifica deploy

1. Vai su GitHub → Actions
2. Controlla lo stato del workflow "Deploy to GitHub Pages"
3. Se verde ✅, la dashboard è live!

## 🛠️ Troubleshooting

### Il deploy fallisce
- Verifica che GitHub Pages sia attivo nelle Settings
- Controlla che il branch sia `main`
- Verifica i permessi del workflow (Settings → Actions → General)

### La dashboard non si carica
- Controlla la console del browser (F12)
- Verifica che i path delle risorse siano corretti
- Assicurati che i file CSS e JS siano stati inclusi nel commit

### Modifiche non visibili
- GitHub Pages può impiegare 1-2 minuti per aggiornare
- Prova a fare un hard refresh (Ctrl+Shift+R o Cmd+Shift+R)
- Svuota la cache del browser

## 📋 Checklist pre-deploy

- [ ] Tutti i file sono committati
- [ ] Il branch è `main` (o merge della PR su main)
- [ ] GitHub Pages è attivo nelle Settings
- [ ] Il workflow è attivo (.github/workflows/pages.yml)
- [ ] Test locale superato

## 🔐 Sicurezza

- Non committare mai API key o credenziali nel codice
- Le variabili sensibili vanno in GitHub Secrets
- Verifica che `.gitignore` escluda file sensibili

## 📚 Risorse utili

- [GitHub Pages Documentation](https://docs.github.com/pages)
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Deploy pages action](https://github.com/actions/deploy-pages)
