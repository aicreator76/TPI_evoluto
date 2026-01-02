param(
  [string]$Root = "https://aicreator76.github.io/TPI_evoluto/",
  [string]$Rel  = "demo_grafica_tpi_2025-12-10"
)

$urls = @(
  $Root,
  ($Root + "$Rel/dashboard_wow_dpi.html"),
  ($Root + "$Rel/wow_anim.css"),
  ($Root + "$Rel/wow_data_demo.js"),
  ($Root + "$Rel/config.js")
)

"=== PAGES SMOKE TEST ==="
foreach($u in $urls){
  try{
    $r = Invoke-WebRequest $u -UseBasicParsing -TimeoutSec 15
    "{0}  {1}" -f $r.StatusCode, $u
  } catch {
    "ERR  {0}" -f $u
  }
}
