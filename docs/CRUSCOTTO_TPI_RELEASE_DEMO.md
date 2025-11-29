# \# Cruscotto TPI – Catena Release DEMO

#

# \## 1. CESARE\_RELEASE\_TPI\_DEMO.ps1

#

# \- Script: `E:\\CLONAZIONE\\CESARE\_COMANDI\\scripts\\CESARE\_RELEASE\_TPI\_DEMO.ps1`

# \- Effetto:

# &nbsp; - crea `E:\\CLONAZIONE\\BACKUP\_EMERGENZA\\`

# &nbsp; - crea cartella `E:\\CLONAZIONE\\RELEASE\_TPI\\YYYY-MM-DD\\`

# &nbsp; - genera `STATUS\_TPI\_YYYY-MM-DD.json`

# \- Log: `E:\\CLONAZIONE\\LOG\\RELEASE\_TPI\_YYYY-MM-DD.log`

#

# \## 2. CESARE\_TPI\_CI\_BRIDGE.ps1

#

# \- Script: `E:\\CLONAZIONE\\scripts\\CESARE\\CESARE\_TPI\_CI\_BRIDGE.ps1`

# \- Effetto:

# &nbsp; - crea tag `tpi-v\*` (es. `tpi-vTEST-CI-BRIDGE-001`)

# &nbsp; - accende il workflow GitHub \*\*Build TPI (stub)\*\*

# \- Risultato: artifact stub (WIN/APK) per quella versione in GitHub Actions

#

# \## 3. Workflow GitHub “Build TPI (stub)”

#

# \- File: `.github/workflows/build-tpi.yml`

# \- Effetto:

# &nbsp; - genera artefatti STUB (non EXE/APK reali)

# &nbsp; - verifica CI e collegamento con CESARE

#

# \## 4. CESARE\_CRONACA\_OK.ps1

#

# \- Script: `E:\\CLONAZIONE\\scripts\\CESARE\\CESARE\_CRONACA\_OK.ps1`

# \- Effetto:

# &nbsp; - aggiorna `STATUS\_TPI\_YYYY-MM-DD.json` con:

# &nbsp;   - `cronaca='saved'`

# &nbsp;   - `cronaca\_file`

# &nbsp;   - `cronaca\_updated\_at`

# &nbsp;   - `semaforo\_tecnico`

# &nbsp;   - `note\_critiche`

# &nbsp;   - `regina\_note`

# &nbsp; - logga riga `CRONACA YYYY-MM-DD : SALVATA` nel log `RELEASE\_TPI\_YYYY-MM-DD.log`

#

# \## 5. Cronache Regina

#

# \- File: `E:\\CLONAZIONE\\Cronache\_Regina\\Cronache\_Regina\_YYYY-MM.md`

# \- Effetto:

# &nbsp; - riassume la giornata con:

# &nbsp;   - semafori `001–BLD / 002–GIT / 003–LMB`

# &nbsp;   - riferimenti a `STATUS\_TPI\_YYYY-MM-DD.json` e ai log `RELEASE\_TPI\_YYYY-MM-DD.log`

#

# \## 6. Agente 0 – Cruscotto DPI DEMO

#

# \- Script orchestratore: `E:\\CLONAZIONE\\tpi\_evoluto\\run\_agente0.ps1`

# \- Effetto:

# &nbsp; - BLOCCO A: legge `E:\\CLONAZIONE\\tpi\_evoluto\\data\\dpi.csv`

# &nbsp;   - calcola: `totale\_dpi`, `ok`, `warning`, `scaduti`, `anomalie`

# &nbsp;   - aggiorna:

# &nbsp;     - `E:\\CLONAZIONE\\tpi\_evoluto\\logs\\agente0\_dashboard.json`

# &nbsp;     - `E:\\CLONAZIONE\\tpi\_evoluto\\logs\\agente0\_cruscotto.html`

# &nbsp; - BLOCCO B: genera feed notifiche DPI per n8n (senza invio se config disabilitata)

# &nbsp;   - file: `E:\\CLONAZIONE\\tpi\_evoluto\\logs\\agente0\_feed\_notifiche.json`

# \- Note:

# &nbsp; - le anomalie (date 1900/1909 ecc.) sono conteggiate in `anomalie`, non come scaduti

# &nbsp; - le chiamate reali a n8n sono controllate da `notifiche.enabled` in `E:\\CLONAZIONE\\tpi\_evoluto\\config.yaml`
