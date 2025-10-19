/* Self-heal: log, suggerimenti e hook integration; non forza rollback se i token/mapping mancano */
const https = require('https'); const http = require('http');

function notify(text){
  const wh = process.env.DISCORD_WEBHOOK || process.env.SLACK_WEBHOOK;
  if (!wh) return;
  const u = new URL(wh); const lib = u.protocol==='https:'?https:http;
  const req = lib.request({hostname:u.hostname, path:u.pathname, method:'POST', headers:{'Content-Type':'application/json'}});
  req.on('error', ()=>{}); req.end(JSON.stringify({ content: text }));
}

(async()=>{
  notify('🩹 Self-heal triggered: evaluating rollback & mitigations…');
  const hints = [
    'Fly rollback: `flyctl releases` e `flyctl deploy --rollback <version>`',
    'Worker rollback: definire PREV_WORKER_VERSION e ridistribuire quella',
    'Abilita SAFE MODE: `AELIS_SAFE_MODE=1` per isolare i plugin',
    'Riduci peso edge: imposta TTL cache su risorse calde',
  ];
  console.log('Self-heal hints:\n- ' + hints.join('\n- '));
  notify('🧭 Self-heal hints delivered. Manual confirmation may be required.');
})();
