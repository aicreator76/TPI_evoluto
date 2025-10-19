export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.pathname === '/api/health') {
      try {
        const r = await fetch(`${env.FLY_ORIGIN}/health`, { cf: { cacheTtl: 0 }, method: 'GET' });
        return new Response(JSON.stringify({ ok: r.ok }), { status: r.ok ? 200 : 503, headers: { 'content-type': 'application/json' } });
      } catch {
        return new Response(JSON.stringify({ ok: false }), { status: 503, headers: { 'content-type': 'application/json' } });
      }
    }

    // Cache solo per GET idempotenti e risposte 200
    if (request.method === 'GET') {
      const cache = caches.default;
      const key = new Request(request.url, request);
      let res = await cache.match(key);
      if (!res) {
        res = await fetch(`${env.FLY_ORIGIN}${url.pathname}${url.search}`, request);
        const cc = res.headers.get('cache-control');
        const cacheable = res.ok && (!cc || !/no-store|no-cache/.test(cc));
        if (cacheable) {
          res = new Response(res.body, res);
          res.headers.set('cache-control', 's-maxage=30, stale-while-revalidate=30');
          ctx.waitUntil(cache.put(key, res.clone()));
        }
      }
      return res;
    }

    return fetch(`${env.FLY_ORIGIN}${url.pathname}${url.search}`, request);
  }
}
