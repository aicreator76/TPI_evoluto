$ErrorActionPreference="Stop"
$port = 8011
Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | %{
  try { taskkill /F /PID $_.OwningProcess 2>$null } catch {}
}
Write-Host "Terminati eventuali processi su $port."
