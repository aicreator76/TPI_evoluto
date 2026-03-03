[CmdletBinding()]
param(
  [string]$EnvFile = "$PSScriptRoot\radar_mail.env",
  [string]$ReportsDir,
  [string]$ReportPattern,
  [switch]$DryRun,
  [switch]$NoAttach,
  [int]$MaxAttachMB,
  [string]$SubjectPrefix
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Load-DotEnv([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) { return }
  Get-Content -LiteralPath $Path | ForEach-Object {
    $line = $_.Trim()
    if ($line -eq "" -or $line.StartsWith("#") -or $line.StartsWith(";")) { return }
    $idx = $line.IndexOf("=")
    if ($idx -lt 1) { return }
    $key = $line.Substring(0, $idx).Trim()
    $val = $line.Substring($idx + 1).Trim()

    if (($val.StartsWith('"') -and $val.EndsWith('"')) -or ($val.StartsWith("'") -and $val.EndsWith("'"))) {
      if ($val.Length -ge 2) { $val = $val.Substring(1, $val.Length - 2) }
    }

    if (-not [string]::IsNullOrWhiteSpace($key)) {
      Set-Item -Path ("Env:{0}" -f $key) -Value $val
    }
  }
}

function Get-Cfg([string]$Key, [string]$Default = $null, [switch]$Required) {
  $item = Get-Item -Path ("Env:{0}" -f $Key) -ErrorAction SilentlyContinue
  $v = $null
  if ($null -ne $item) { $v = $item.Value }
  if ([string]::IsNullOrWhiteSpace($v)) { $v = $Default }
  if ($Required -and [string]::IsNullOrWhiteSpace($v)) { throw "Missing required config: $Key" }
  return $v
}

function Split-EmailList([string]$List) {
  if ([string]::IsNullOrWhiteSpace($List)) { return @() }
  return ($List -split '[,;]') | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
}

function Ensure-Dir([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
  }
}

$mailMessage = $null
$smtpClient  = $null
$attachment  = $null

try {
  Load-DotEnv -Path $EnvFile

  $smtpHost = Get-Cfg "RADAR_SMTP_HOST" "127.0.0.1"
  $smtpPort = [int](Get-Cfg "RADAR_SMTP_PORT" "1025")
  $smtpUser = Get-Cfg "RADAR_SMTP_USER" $null -Required
  $smtpPass = Get-Cfg "RADAR_SMTP_APP_PASSWORD" $null -Required

  $mailFrom = Get-Cfg "RADAR_MAIL_FROM" $smtpUser
  $mailTo   = Split-EmailList (Get-Cfg "RADAR_MAIL_TO" $null -Required)
  $mailCc   = Split-EmailList (Get-Cfg "RADAR_MAIL_CC" "")
  $mailBcc  = Split-EmailList (Get-Cfg "RADAR_MAIL_BCC" "")

  if (-not $PSBoundParameters.ContainsKey("SubjectPrefix")) { $SubjectPrefix = Get-Cfg "RADAR_SUBJECT_PREFIX" "[DPI radar]" }
  if (-not $PSBoundParameters.ContainsKey("MaxAttachMB"))   { $MaxAttachMB   = [int](Get-Cfg "RADAR_MAX_ATTACH_MB" "5") }
  if (-not $PSBoundParameters.ContainsKey("ReportPattern") -or [string]::IsNullOrWhiteSpace($ReportPattern)) {
    $ReportPattern = Get-Cfg "RADAR_REPORT_PATTERN" "radar_*.csv"
  }

  if ([string]::IsNullOrWhiteSpace($ReportsDir)) {
    $ReportsDir = Get-Cfg "RADAR_REPORTS_DIR" $null
    if ([string]::IsNullOrWhiteSpace($ReportsDir)) {
      $dataDir = Get-Cfg "RADAR_DPI_DATA_DIR" $null -Required
      $ReportsDir = Join-Path $dataDir "reports"
    }
  }
  if (-not (Test-Path -LiteralPath $ReportsDir)) { throw "Directory report non trovata: $ReportsDir" }

  $logDir = Get-Cfg "RADAR_LOG_DIR" $null
  if ([string]::IsNullOrWhiteSpace($logDir)) {
    $maybeDataDir = Get-Cfg "RADAR_DPI_DATA_DIR" $null
    if (-not [string]::IsNullOrWhiteSpace($maybeDataDir)) { $logDir = Join-Path $maybeDataDir "logs" }
    else { $logDir = Join-Path $PSScriptRoot "logs" }
  }
  Ensure-Dir -Path $logDir
  $logFile = Join-Path $logDir ("radar_send_mail_{0}.log" -f (Get-Date -Format "yyyy-MM-dd"))

  function Log([string]$Msg) {
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[{0}] {1}" -f $ts, $Msg
    Write-Host $line
    Add-Content -LiteralPath $logFile -Value $line
  }

  $report = Get-ChildItem -LiteralPath $ReportsDir -File -Filter $ReportPattern |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

  if (-not $report) { throw "Nessun report trovato in '$ReportsDir' con pattern '$ReportPattern'" }

  $rowCount = 0
  try { $rowCount = (Import-Csv -LiteralPath $report.FullName | Measure-Object).Count } catch { $rowCount = 0 }

  $now = Get-Date
  $subject = "{0} {1} - {2}" -f $SubjectPrefix, $now.ToString("yyyy-MM-dd HH:mm"), $report.Name

  $body = @"
Ciao,

in allegato il report giornaliero generato da Radar DPI.

Report: $($report.Name)
Percorso: $($report.FullName)
Ultima modifica: $($report.LastWriteTime)
Righe (stima): $rowCount

-- TPI_evoluto / Radar DPI
"@

  $mailMessage = New-Object System.Net.Mail.MailMessage
  $mailMessage.From = $mailFrom
  foreach ($addr in $mailTo)  { [void]$mailMessage.To.Add($addr) }
  foreach ($addr in $mailCc)  { [void]$mailMessage.CC.Add($addr) }
  foreach ($addr in $mailBcc) { [void]$mailMessage.Bcc.Add($addr) }

  $mailMessage.Subject = $subject
  $mailMessage.Body = $body
  $mailMessage.IsBodyHtml = $false

  $attached = $false
  if (-not $NoAttach) {
    $sizeMB = [math]::Round(($report.Length / 1MB), 2)
    if ($sizeMB -le $MaxAttachMB) {
      $attachment = New-Object System.Net.Mail.Attachment($report.FullName)
      [void]$mailMessage.Attachments.Add($attachment)
      $attached = $true
    } else {
      $mailMessage.Body += ("`r`nNOTA: report {0} MB > limite {1} MB, non allegato." -f $sizeMB, $MaxAttachMB)
      $attached = $false
    }
  }

  if ($DryRun) {
    Log ("DRY RUN: pronto a inviare via {0}:{1} come {2}" -f $smtpHost, $smtpPort, $smtpUser)
    Log ("Da: {0}" -f $mailFrom)
    Log ("A: {0}" -f ($mailTo -join "; "))
    if (@($mailCc).Count -gt 0)  { Log ("CC: {0}" -f ($mailCc -join "; ")) }
    if (@($mailBcc).Count -gt 0) { Log ("BCC: {0}" -f ($mailBcc -join "; ")) }
    Log ("Oggetto: {0}" -f $subject)
    Log ("Report selezionato: {0}" -f $report.FullName)
    Log ("Allegato: {0}" -f ($(if ($attached) { "SI" } else { "NO" })))
    exit 0
  }

  $smtpClient = New-Object System.Net.Mail.SmtpClient($smtpHost, $smtpPort)

  # TLS solo se NON e' localhost (con MailHog/Papercut spesso NO TLS)
  $smtpClient.EnableSsl = ($smtpHost -notin @("127.0.0.1","localhost"))

  $smtpClient.UseDefaultCredentials = $false
  $smtpClient.DeliveryMethod = [System.Net.Mail.SmtpDeliveryMethod]::Network
  $smtpClient.Credentials = New-Object System.Net.NetworkCredential($smtpUser, $smtpPass)

  Log ("INVIO: {0}:{1} user={2} report={3}" -f $smtpHost, $smtpPort, $smtpUser, $report.Name)
  $smtpClient.Send($mailMessage)
  Log "OK: mail inviata."
  exit 0
}
catch {
  Write-Error $_
  try {
    $msg = $_.Exception.Message
    if (-not [string]::IsNullOrWhiteSpace($msg)) { Write-Host ("ERRORE: {0}" -f $msg) }
  } catch { }
  exit 1
}
finally {
  if ($attachment)  { $attachment.Dispose() }
  if ($mailMessage) { $mailMessage.Dispose() }
  if ($smtpClient)  { $smtpClient.Dispose() }
}
