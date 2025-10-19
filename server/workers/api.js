/**
 * Cloudflare Worker API Stub
 * - Responds to /api/health
 * - Proxies other requests to FLY_ORIGIN
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Handle health check
    if (url.pathname === '/api/health') {
      return new Response(JSON.stringify({
        status: 'ok',
        worker: 'cloudflare',
        timestamp: new Date().toISOString()
      }), {
        status: 200,
        headers: {
          'Content-Type': 'application/json'
        }
      });
    }
    
    // Proxy to FLY_ORIGIN
    const flyOrigin = env.FLY_ORIGIN || 'https://tpi-evoluto.fly.dev';
    const proxyUrl = new URL(url.pathname + url.search, flyOrigin);
    
    // Forward request to Fly.io
    const proxyRequest = new Request(proxyUrl, {
      method: request.method,
      headers: request.headers,
      body: request.body
    });
    
    try {
      const response = await fetch(proxyRequest);
      return response;
    } catch (err) {
      return new Response(JSON.stringify({
        error: 'Proxy error',
        message: err.message
      }), {
        status: 502,
        headers: {
          'Content-Type': 'application/json'
        }
      });
    }
  }
};
