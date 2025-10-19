/* Health monitor: misura p95 e error rate, pubblica su Slack/Discord e fallisce se oltre soglia */
const http = require('http'); const https = require('https'); const { URL } = require('url');

const TARGETS = (process.env.TARGETS || '').split(',').map(s => s.trim()).filter(Boolean);
const DURATION_SEC = +process.env.DURATION_SEC || 300;
const INTERVAL_MS = +process.env.INTERVAL_MS || 5000;
const ERROR_RATE_THRESHOLD = parseFloat(process.env.ERROR_RATE_THRESHOLD || '0.01');
const LATENCY_P95_MS = parseFloat(process.env.LATENCY_P95_MS || '800');

if (!TARGETS.length) { console.error('No TARGETS provided'); process.exit(2); }

const sleep = ms => new Promise(r => setTimeout(r, ms));
const fetchUrl = (u) => new Promise((res) => {
  const url = new URL(u);
  const lib = url.protocol === 'https:' ? https : http;
  const t0 = Date.now();
  const req = lib.get(url, { timeout: 4000 }, r => {
    r.resume();
    res({ status: r.statusCode, ms: Date.now() - t0 });
  });
  req.on('error', () => res({ status: 599, ms: Date.now() - t0 }));
  req.on('timeout', () => { req.destroy(); res({ status: 598, ms: Date.now() - t0 }); });
});

const results = Object.fromEntries(TARGETS.map(t => [t, []]));
(async () => {
  const end = Date.now() + DURATION_SEC * 1000;
  while (Date.now() < end) {
    await Promise.all(TARGETS.map(async t => results[t].push(await fetchUrl(t))));
    await sleep(INTERVAL_MS);
  }
  // Valutazione
  let fail = false;
  for (const t of TARGETS) {
    const arr = results[t];
    const codes = arr.map(x => x.status);
    const errs = codes.filter(c => c >= 500 || c === 598 || c === 599).length;
    const errRate = errs / arr.length;
    const lat = arr.map(x => x.ms).sort((a,b)=>a-b);
    const p95 = lat[Math.floor(lat.length * 0.95)] || 0;
    console.log(`[${t}] samples=${arr.length} errorRate=${(errRate*100).toFixed(2)}% p95=${p95}ms`);
    if (errRate > ERROR_RATE_THRESHOLD || p95 > LATENCY_P95_MS) fail = true;
  }
  const msg = fail ? '❌ Canary FAILED' : '✅ Canary PASSED';
  console.log(msg);

  const webhook = process.env.DISCORD_WEBHOOK || process.env.SLACK_WEBHOOK;
  if (webhook) {
    const payload = JSON.stringify({ content: `${msg} – thresholds: err>${ERROR_RATE_THRESHOLD*100}% or p95>${LATENCY_P95_MS}ms` });
    const { hostname, pathname, protocol } = new URL(webhook);
    const lib = protocol === 'https:' ? https : http;
    const req = lib.request({ hostname, path: pathname, method: 'POST', headers: { 'Content-Type': 'application/json' } });
    req.on('error', ()=>{});
    req.write(payload); req.end();
  }
  process.exit(fail ? 1 : 0);
})();
