## Sicurezza & Deploy

[![Security CI](https://github.com/aicreator76/TPI_evoluto/actions/workflows/security.yml/badge.svg)](https://github.com/aicreator76/TPI_evoluto/actions/workflows/security.yml)
[![Pages](https://github.com/aicreator76/TPI_evoluto/actions/workflows/pages.yml/badge.svg)](https://github.com/aicreator76/TPI_evoluto/actions/workflows/pages.yml)

### ENV (sample)
Copia `.env.example` in `.env` e personalizza:
- `ENV=prod` in produzione
- `CORS_ALLOW_ORIGINS=https://tuo.dominio`
- `ALLOWED_HOSTS=tuo.dominio,*.azienda.it`

### Quick test
```powershell
$env:APP_VERSION = "v4.1"
$env:GIT_SHA    = (git rev-parse --short HEAD)
$env:BUILD_TIME = ((Get-Date).ToUniversalTime()).ToString("s") + "Z"
uvicorn app.main:app --reload

### F) Commit & push (hook devono restare **Passed**)
```powershell
pre-commit run -a
git add app/middleware_security.py app/main.py .github/workflows/security.yml .env.example README.md
git commit -m "sec: headers+correlation-id+CORS hardening; ci: pip-audit+bandit; env example"
git push
# CODEOWNERS + PR template (facilitano review e checklist)
mkdir .github -Force | Out-Null
@'* @aicreator76'@ | Set-Content .\.github\CODEOWNERS -Encoding UTF8
@'
## Ready to merge checklist
- [ ] CORS/Hosts configurati per PROD
- [ ] Nessun dato sensibile nei log
- [ ] Test http aggiornati (import/export/health/version)
- [ ] Security CI green (pip-audit/bandit)
