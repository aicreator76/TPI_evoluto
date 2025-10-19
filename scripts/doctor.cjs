#!/usr/bin/env node
/* scripts/doctor.cjs
   Auto-diagnostica rapida per Aelis: avvia il server in SAFE MODE,
   verifica /health e /metrics su PORT (default 8080) e ritorna exit code.
*/
const { spawn } = require('child_process');
const http = require('http');

const PORT = process.env.PORT ? +process.env.PORT : 8080;
const SAFE = '1'; // forza safe mode di default
const NODE_REQ = 20;

function nodeMajor(v){ return +v.replace(/^v/,'').split('.')[0]; }
if (nodeMajor(process.version) < NODE_REQ) {
  console.error(`❌ Node ${process.version} < ${NODE_REQ}.x — aggiorna Node.`);
  process.exit(1);
}

const get = (path='/health') => new Promise((resolve) => {
  const req = http.get({ hostname: '127.0.0.1', port: PORT, path, timeout: 2000 }, res => {
    res.resume(); resolve(res.statusCode);
  });
  req.on('error', () => resolve(0));
  req.on('timeout', () => { req.destroy(); resolve(0); });
});

(async () => {
  // 1) C’è già qualcuno su PORT?
  let status = await get('/health');
  if (status) {
    console.log(`ℹ️  Qualcosa risponde già su :${PORT} /health => ${status}`);
    const m = await get('/metrics');
    console.log(`ℹ️  /metrics => ${m || 'no response'}`);
    process.exit(status === 200 && m === 200 ? 0 : 2);
  }

  // 2) Avvia Aelis in SAFE MODE su PORT
  console.log('▶ Avvio Aelis in SAFE MODE su :%d…', PORT);
  const child = spawn(process.execPath, ['main.js'], {
    env: { ...process.env, PORT: String(PORT), AELIS_SAFE_MODE: SAFE, NODE_ENV: 'production' },
    stdio: ['ignore', 'pipe', 'pipe']
  });

  let bootLog = '';
  child.stdout.on('data', d => { bootLog += d.toString(); process.stdout.write(d); });
  child.stderr.on('data', d => { bootLog += d.toString(); process.stderr.write(d); });

  // 3) Poll /health e /metrics fino a 15s
  const deadline = Date.now() + 15000;
  let okH = false, okM = false;
  while (Date.now() < deadline) {
    okH = (await get('/health')) === 200;
    okM = (await get('/metrics')) === 200;
    if (okH && okM) break;
    await new Promise(r => setTimeout(r, 600));
  }

  if (!okH || !okM) {
    console.error(`❌ Doctor: health=${okH} metrics=${okM}. Probabile crash o porta non in ascolto.`);
    console.error('Suggerimenti:');
    console.error('- Verifica dipendenze: npm ci');
    console.error('- Forza 0.0.0.0 in app.listen(PORT, "0.0.0.0")');
    console.error('- SAFE MODE attivo: se crasha comunque, guarda lo stack qui sopra');
    child.kill('SIGTERM');
    process.exit(1);
  } else {
    console.log('✅ Doctor: /health & /metrics OK su :%d', PORT);
    console.log('ℹ️  Arresto processo di test…');
    child.kill('SIGTERM');
    process.exit(0);
  }
})();
