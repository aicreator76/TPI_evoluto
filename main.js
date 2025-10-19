import express from 'express';
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Safe-mode loading snippet
let config = { port: 8080, safeMode: false };
let SAFE_MODE = false;

try {
  const configPath = join(__dirname, 'configs', 'config.json');
  const configData = readFileSync(configPath, 'utf8');
  config = JSON.parse(configData);
  SAFE_MODE = config.safeMode || process.env.AELIS_SAFE_MODE === 'true' || process.env.AELIS_SAFE_MODE === '1';
} catch (err) {
  console.warn('⚠️  Could not load config.json, using defaults:', err.message);
}

const app = express();
const PORT = process.env.PORT || config.port || 8080;

// Middleware
app.use(express.json());
app.use(express.static('public'));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', safeMode: SAFE_MODE, timestamp: new Date().toISOString() });
});

// Metrics endpoint
app.get('/metrics', (req, res) => {
  res.set('Content-Type', 'text/plain');
  res.send(`# HELP app_info Application information
# TYPE app_info gauge
app_info{version="1.0.0",safe_mode="${SAFE_MODE}"} 1
# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds counter
app_uptime_seconds ${process.uptime()}
`);
});

// Observability routes aliases
app.get('/observability/metrics', (req, res) => {
  res.redirect('/metrics');
});

// Mode endpoint
app.get('/mode', (req, res) => {
  res.json({ 
    safeMode: SAFE_MODE,
    config: config,
    env: process.env.AELIS_SAFE_MODE
  });
});

// Plugin loader with SAFE_MODE check
async function loadPlugins() {
  if (SAFE_MODE) {
    console.log('🔒 SAFE_MODE enabled - skipping plugin loading');
    return;
  }
  
  try {
    console.log('🔌 Loading plugins...');
    // Plugin loading logic would go here
    // For now, just a placeholder
  } catch (err) {
    console.error('❌ Error loading plugins:', err.message);
  }
}

// Start server
async function startServer() {
  await loadPlugins();
  
  app.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
    console.log(`🔒 Safe mode: ${SAFE_MODE}`);
    console.log(`📊 Metrics available at http://localhost:${PORT}/metrics`);
    console.log(`💚 Health check at http://localhost:${PORT}/health`);
  });
}

startServer().catch(err => {
  console.error('❌ Failed to start server:', err);
  process.exit(1);
});
