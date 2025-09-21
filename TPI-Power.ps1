param(
  [string]$ProjectPath = "E:\TPI_evoluto",
  [string]$BindHost    = "127.0.0.1",
  [int]   $StartPort   = 8000,
  [switch]$OpenBrowser
)
if (-not $PSBoundParameters.ContainsKey("OpenBrowser")) { $OpenBrowser = $true }
$ErrorActionPreference = "Stop"

function Say($m,[ConsoleColor]$c="Cyan"){ Write-Host $m -ForegroundColor $c }
function Ensure-Dir($p){ if(-not(Test-Path $p)){ New-Item -ItemType Directory -Force -Path $p | Out-Null } }
function Ensure-File($path,$content){ if(-not(Test-Path $path)){ Set-Content -Path $path -Value $content -Encoding UTF8 } }
function Get-FreeTcpPort([int]$start,[int]$max=50,[string]$bindIp="127.0.0.1"){
  for($p=$start; $p -lt $start+$max; $p++){
    $l = New-Object System.Net.Sockets.TcpListener ([System.Net.IPAddress]::Parse($bindIp),$p)
    try{ $l.Start(); $l.Stop(); return $p }catch{}finally{ try{$l.Stop()}catch{} }
  }
  throw "Nessuna porta libera trovata a partire da $start"
}

# --- Struttura cartelle
@($ProjectPath,
  (Join-Path $ProjectPath "app"),
  (Join-Path $ProjectPath "app\routers"),
  (Join-Path $ProjectPath "app\config"),
  (Join-Path $ProjectPath "templates"),
  (Join-Path $ProjectPath "static"),
  (Join-Path $ProjectPath "logs"),
  (Join-Path $ProjectPath "data")
) | ForEach-Object { Ensure-Dir $_ }

# --- .gitignore (crea solo se assente)
$gitignore = @'
__pycache__/
*.pyc
.venv/
.env
logs/
data/uvicorn.pid
.vscode/
.idea/
