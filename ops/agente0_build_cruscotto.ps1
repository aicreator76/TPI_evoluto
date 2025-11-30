param()

Write-Host "=== AGENTE0 - CRUSCOTTO + FEED n8n + CRONACA ==="

# -----------------------------
# CONFIG PERCORSI
# -----------------------------
$RepoRoot      = "E:\CLONAZIONE\tpi_evoluto"
$LogsPath      = Join-Path $RepoRoot "logs"
$DashboardPath = Join-Path $LogsPath "agente0_dashboard.json"
$CruscottoJson = Join-Path $LogsPath "agente0_cruscotto.json"
$FeedPath      = Join-Path $LogsPath "agente0_feed_notifiche.json"
$CruscottoHtml = Join-Path $LogsPath "agente0_cruscotto.html"

$CronacheRoot  = "E:\CLONAZIONE\CRONACHE_CAMELOT"

# -----------------------------
# LETTURA DASHBOARD
# -----------------------------
if (-not (Test-Path $DashboardPath)) {
    Write-Error "File dashboard non trovato: $DashboardPath"
    exit 1
}

$dashboardJson = Get-Content -Path $DashboardPath -Raw
$dashboard     = $dashboardJson | ConvertFrom-Json

$rows      = $dashboard.rows
$updatedAt = $dashboard.updated_at

if (-not $rows) {
    Write-Warning "Nessuna riga DPI trovata in agente0_dashboard.json."
    $rows = @()
}

$oggi    = Get-Date
$culture = [System.Globalization.CultureInfo]::InvariantCulture

# -----------------------------
# CLASSIFICAZIONE RIGHE (MUTUAMENTE ESCLUSIVE)
# -----------------------------
$okList        = @()
$warningList   = @()
$scadutiReali  = @()
$anomali       = @()

foreach ($row in $rows) {

    $scadenzaStr  = $row.scadenza
    $scadenzaDate = $null
    $isAnomalo    = $false

    # --- analisi scadenza "vita DPI" ---
    if (-not [string]::IsNullOrWhiteSpace($scadenzaStr)) {
        try {
            $scadenzaDate = [datetime]::Parse($scadenzaStr, $culture)
            if ($scadenzaDate.Year -lt 2000) {
                # es: 1900/1909 -> anomalia
                $isAnomalo = $true
            }
        } catch {
            $isAnomalo = $true
        }
    } else {
        $isAnomalo = $true
    }

    if ($isAnomalo) {
        $anomali += $row
        continue
    }

    # --- gg alla scadenza verifica (per warning 30gg) ---
    $giorniAllaScad = $null
    if ($row.gg_alla_scad_verifica -ne $null -and $row.gg_alla_scad_verifica -ne "") {
        [double]::TryParse([string]$row.gg_alla_scad_verifica, [ref]$giorniAllaScad) | Out-Null
    }

    # ORDINE DI PRIORITA':
    # 1) SCADUTO (vita DPI finita)
    # 2) WARNING (30 gg verifica)
    # 3) OK
    if ($scadenzaDate -lt $oggi) {
        $scadutiReali += $row
        continue
    }

    if ($giorniAllaScad -ne $null -and $giorniAllaScad -ge 0 -and $giorniAllaScad -le 30) {
        $warningList += $row
        continue
    }

    $okList += $row
}

$totaleDpi     = $rows.Count
$warningPuliti = $warningList.Count
$scadutiPuliti = $scadutiReali.Count
$ok            = $okList.Count
$anomaliCount  = $anomali.Count

Write-Host "Dashboard letta e ricalcolata:"
Write-Host "  Totale DPI:             $totaleDpi"
Write-Host "  In regola (OK):         $ok"
Write-Host "  Warning 30gg:           $warningPuliti"
Write-Host "  Scaduti REALI:          $scadutiPuliti"
Write-Host "  Anomali da verificare:  $anomaliCount"

# -----------------------------
# 1) CRUSCOTTO JSON "REGINA"
# -----------------------------
$now    = Get-Date
$nowIso = $now.ToString("s")

$cruscottoObj = [ordered]@{
    meta = [ordered]@{
        fonte              = "agente0_dashboard.json"
        versione_cruscotto = 1
        generato_il        = $nowIso
    }
    conteggio = [ordered]@{
        totale_dpi        = $totaleDpi
        ok                = $ok
        warning           = $warningPuliti
        scaduti           = $scadutiPuliti
        righe_errore_data = $anomaliCount
    }
}

$cruscottoJsonText = $cruscottoObj | ConvertTo-Json -Depth 5
Set-Content -Path $CruscottoJson -Value $cruscottoJsonText -Encoding UTF8
Write-Host "Cruscotto Regina JSON scritto in: $CruscottoJson"
Get-Content -Path $CruscottoJson

# -----------------------------
# 2) FEED n8n (solo warning + scaduti REALI)
# -----------------------------
$feedObj = [ordered]@{
    generated_at = $nowIso
    dpi_warning  = $warningList
    dpi_scaduti  = $scadutiReali
}

$feedJsonText = $feedObj | ConvertTo-Json -Depth 8
Set-Content -Path $FeedPath -Value $feedJsonText -Encoding UTF8
Write-Host "Feed n8n scritto in: $FeedPath"

# -----------------------------
# 3) MINI-CRUSCOTTO HTML
# -----------------------------
$aggiornatoIl = if ($updatedAt) { $updatedAt } else { $nowIso }

$html = @"
<h2>Cruscotto DPI - Teufelberger</h2>
<p>Totale DPI: <strong>$totaleDpi</strong></p>
<ul>
  <li>In regola: $ok</li>
  <li>In allerta 30 gg: $warningPuliti</li>
  <li>Scaduti reali: $scadutiPuliti</li>
  <li>Anomali da verificare: $anomaliCount</li>
</ul>
<small>Aggiornato il: $aggiornatoIl</small>
"@

Set-Content -Path $CruscottoHtml -Value $html -Encoding UTF8
Write-Host "Cruscotto HTML scritto in: $CruscottoHtml"

# -----------------------------
# 4) CRONACA CAMELOT (Markdown)
# -----------------------------
if (-not (Test-Path $CronacheRoot)) {
    New-Item -ItemType Directory -Path $CronacheRoot | Out-Null
}

# data cronaca = data updated_at se presente, altrimenti oggi
if ($updatedAt) {
    try {
        $dtCronaca = [datetime]::Parse($updatedAt, $culture)
    } catch {
        $dtCronaca = $oggi
    }
} else {
    $dtCronaca = $oggi
}

$giornoStr   = $dtCronaca.ToString("yyyy-MM-dd")
$cronacaPath = Join-Path $CronacheRoot ("CRONACA_CAMELOT_{0}.md" -f $giornoStr)

if (-not (Test-Path $cronacaPath)) {
    $header = "# Cronaca di Camelot - $giornoStr`r`n"
    Set-Content -Path $cronacaPath -Value $header -Encoding UTF8
}

$cronacaBlocco = @"
## Agente 0 - DPI Teufelberger

- Totale DPI: **$totaleDpi**
- In regola: **$ok**
- In allerta 30 gg: **$warningPuliti**
- Scaduti reali (dopo pulizia anomalie): **$scadutiPuliti**
- Anomali da verificare (es. scadenze anno < 2000): **$anomaliCount**

File di riferimento:
- `logs\agente0_dashboard.json`
- `logs\agente0_cruscotto.json`
- `logs\agente0_cruscotto.html`
- `logs\agente0_feed_notifiche.json`

Note:
- Gli "anomali" sono DPI con date di scadenza storiche (es. 1900/1909) considerate errori di compilazione ed escluse dal conteggio ufficiale dei DPI scaduti.
- Il feed per n8n è pronto ma **non ancora collegato** a nessun flusso di notifica.
"@

Add-Content -Path $cronacaPath -Value $cronacaBlocco -Encoding UTF8
Write-Host "Cronaca aggiornata in: $cronacaPath"

Write-Host "=== AGENTE0 - OPERAZIONE COMPLETATA ==="
