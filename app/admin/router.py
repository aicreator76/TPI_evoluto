from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router: APIRouter = APIRouter(tags=["admin"])

_HTML = r"""
<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>TPI_evoluto – Admin</title>
  <style>
    body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:16px;max-width:1100px}
    .row{display:flex;gap:12px;flex-wrap:wrap}
    .card{border:1px solid #ddd;border-radius:10px;padding:12px;flex:1;min-width:320px}
    label{display:block;font-size:12px;color:#333;margin-top:8px}
    input,select,textarea{width:100%;padding:8px;border:1px solid #ccc;border-radius:8px}
    textarea{min-height:130px;font-family:ui-monospace,Consolas,monospace}
    button{padding:10px 12px;border:0;border-radius:10px;cursor:pointer}
    .btn{background:#111;color:#fff}
    .btn2{background:#eee}
    .ok{color:green}
    .bad{color:#b00020}
    pre{background:#f6f6f6;padding:10px;border-radius:10px;overflow:auto}
    table{width:100%;border-collapse:collapse}
    th,td{border-bottom:1px solid #eee;padding:8px;text-align:left;font-size:13px}
    .muted{color:#666;font-size:12px}
  </style>
</head>
<body>
  <h2>TPI_evoluto – Admin</h2>
  <div class="muted">UI integrata: lock / run / events / ack. Nessuna dipendenza extra.</div>

  <div class="row">
    <div class="card">
      <h3>Connessione</h3>
      <label>Base URL (lascia vuoto = stesso host)</label>
      <input id="base" placeholder="es: http://127.0.0.1:8000" />

      <label>X-API-Key (opzionale)</label>
      <input id="apikey" placeholder="se ORCH_API_KEY è attivo" />

      <div style="margin-top:10px" class="row">
        <button class="btn2" onclick="health()">Healthz</button>
        <button class="btn2" onclick="lockStatus()">Lock status</button>
      </div>

      <div id="conn_out" style="margin-top:10px"></div>
    </div>

    <div class="card">
      <h3>Lock</h3>
      <label>Lock name</label>
      <input id="lock_name" value="orchestrator0"/>

      <label>Owner</label>
      <input id="lock_owner" value="ADMIN-UI"/>

      <label>TTL seconds</label>
      <input id="lock_ttl" type="number" value="120"/>

      <div style="margin-top:10px" class="row">
        <button class="btn" onclick="lockAcquire()">Acquire</button>
        <button class="btn2" onclick="lockRelease()">Release</button>
      </div>

      <label>Token (auto da acquire)</label>
      <input id="lock_token" placeholder="token..." />
      <div id="lock_out" style="margin-top:10px"></div>
    </div>
  </div>

  <div class="row" style="margin-top:12px">
    <div class="card">
      <h3>Run Orchestrator</h3>
      <div class="muted">POST /api/orchestrator/run (usa lock interno)</div>

      <label>Body JSON</label>
      <textarea id="run_body"></textarea>

      <div style="margin-top:10px" class="row">
        <button class="btn" onclick="runOrchestrator()">Run</button>
        <button class="btn2" onclick="fillSample()">Carica sample</button>
      </div>

      <div id="run_out" style="margin-top:10px"></div>
    </div>

    <div class="card">
      <h3>Events</h3>
      <label>Tenant</label>
      <input id="tenant" value="ACME"/>

      <label>Status</label>
      <input id="status" value="pending"/>

      <label>Limit</label>
      <input id="limit" type="number" value="200"/>

      <div style="margin-top:10px" class="row">
        <button class="btn2" onclick="loadEvents()">Refresh</button>
      </div>

      <div id="events_out" style="margin-top:10px"></div>
    </div>
  </div>

<script>
function baseUrl() {
  const b = document.getElementById("base").value.trim();
  return b ? b.replace(/\/+$/,'') : "";
}
function headersJson() {
  const h = {"Content-Type":"application/json"};
  const k = document.getElementById("apikey").value.trim();
  if (k) h["X-API-Key"] = k;
  return h;
}
function out(id, ok, obj) {
  const el = document.getElementById(id);
  const cls = ok ? "ok" : "bad";
  el.innerHTML = `<div class="${cls}">${ok ? "OK" : "ERR"}</div><pre>${escapeHtml(JSON.stringify(obj, null, 2))}</pre>`;
}
function escapeHtml(s){return (s||"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;");}

async function health(){
  try{
    const r = await fetch(baseUrl()+"/healthz");
    const j = await r.json();
    out("conn_out", r.ok, j);
  }catch(e){ out("conn_out", false, {error:String(e)}); }
}
async function lockStatus(){
  const name = document.getElementById("lock_name").value.trim();
  try{
    const r = await fetch(baseUrl()+`/api/orchestrator/lock?name=${encodeURIComponent(name)}`);
    const j = await r.json();
    out("lock_out", r.ok, j);
  }catch(e){ out("lock_out", false, {error:String(e)}); }
}
async function lockAcquire(){
  const name = document.getElementById("lock_name").value.trim();
  const owner = document.getElementById("lock_owner").value.trim();
  const ttl = parseInt(document.getElementById("lock_ttl").value,10) || 120;
  try{
    const r = await fetch(baseUrl()+"/api/orchestrator/lock/acquire", {
      method:"POST", headers: headersJson(),
      body: JSON.stringify({name:name, ttl_seconds: ttl, owner: owner})
    });
    const j = await r.json();
    if (r.ok && j.lock && j.lock.token) document.getElementById("lock_token").value = j.lock.token;
    out("lock_out", r.ok, j);
  }catch(e){ out("lock_out", false, {error:String(e)}); }
}
async function lockRelease(){
  const name = document.getElementById("lock_name").value.trim();
  const token = document.getElementById("lock_token").value.trim();
  try{
    const r = await fetch(baseUrl()+"/api/orchestrator/lock/release", {
      method:"POST", headers: headersJson(),
      body: JSON.stringify({name:name, token: token})
    });
    const j = await r.json();
    out("lock_out", r.ok, j);
  }catch(e){ out("lock_out", false, {error:String(e)}); }
}
function fillSample(){
  const root = "E:\\\\CLONAZIONE\\\\tpi_evoluto";
  const sample = {
    dpi_csv: root + "\\\\data\\\\dpi_sample.csv",
    horizon_days: 60,
    backfill_days: 2,
    thresholds: [30,15,1],
    dry_run: false,
    init_db: false,
    lock_name: "orchestrator0",
    lock_ttl_seconds: 120,
    owner: "ADMIN-UI"
  };
  document.getElementById("run_body").value = JSON.stringify(sample, null, 2);
}
async function runOrchestrator(){
  try{
    const body = JSON.parse(document.getElementById("run_body").value || "{}");
    const r = await fetch(baseUrl()+"/api/orchestrator/run", {
      method:"POST", headers: headersJson(), body: JSON.stringify(body)
    });
    const j = await r.json();
    out("run_out", r.ok, j);
  }catch(e){ out("run_out", false, {error:String(e)}); }
}
async function loadEvents(){
  const tenant = document.getElementById("tenant").value.trim();
  const status = document.getElementById("status").value.trim();
  const limit = parseInt(document.getElementById("limit").value,10) || 200;
  try{
    const r = await fetch(baseUrl()+`/api/orchestrator/events?tenant=${encodeURIComponent(tenant)}&status=${encodeURIComponent(status)}&limit=${limit}`);
    const j = await r.json();
    renderEvents(j);
  }catch(e){ document.getElementById("events_out").innerHTML = `<div class="bad">ERR</div><pre>${escapeHtml(String(e))}</pre>`; }
}
function renderEvents(items){
  if (!Array.isArray(items)) {
    out("events_out", false, items);
    return;
  }
  let html = `<table><thead><tr><th>ID</th><th>ref</th><th>threshold</th><th>event_date</th><th>status</th><th>ACK</th></tr></thead><tbody>`;
  for (const ev of items){
    html += `<tr>
      <td>${ev.id}</td>
      <td>${escapeHtml((ev.ref_type||"")+" / "+(ev.ref_id||""))}</td>
      <td>${ev.threshold_days}</td>
      <td>${escapeHtml(ev.event_date||"")}</td>
      <td>${escapeHtml(ev.status||"")}</td>
      <td><button class="btn2" onclick="ackEvent(${ev.id}, 'ack')">ack</button></td>
    </tr>`;
  }
  html += `</tbody></table>`;
  document.getElementById("events_out").innerHTML = html;
}
async function ackEvent(id, status){
  try{
    const r = await fetch(baseUrl()+`/api/orchestrator/events/${id}/ack`, {
      method:"POST", headers: headersJson(), body: JSON.stringify({status: status})
    });
    const j = await r.json();
    if (!r.ok) { out("events_out", false, j); return; }
    loadEvents();
  }catch(e){ out("events_out", false, {error:String(e)}); }
}
fillSample();
</script>
</body>
</html>
"""


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def admin_ui() -> HTMLResponse:
    return HTMLResponse(_HTML)
