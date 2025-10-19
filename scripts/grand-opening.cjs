#!/usr/bin/env node
/**
 * Grand Opening Script
 * - Runs quality gate
 * - Optional docker compose up
 * - Starts server
 * - Runs seed-demo
 * - Prints banner
 */

const { execSync, spawn } = require('child_process');
const path = require('path');

function log(msg) {
  console.log(`[grand-opening] ${msg}`);
}

function error(msg) {
  console.error(`[grand-opening] ❌ ${msg}`);
}

function printBanner() {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🎉  TPI/AELIS GRAND OPENING  🎉                        ║
║                                                           ║
║   Dashboard & Agents are now running!                    ║
║                                                           ║
║   📊 Metrics:  http://localhost:8080/metrics             ║
║   💚 Health:   http://localhost:8080/health              ║
║   🔒 Mode:     http://localhost:8080/mode                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
  `);
}

async function runQualityGate() {
  log('Running quality gate...');
  try {
    execSync('node scripts/quality-gate.cjs', { 
      stdio: 'inherit',
      cwd: process.cwd()
    });
    log('✓ Quality gate passed');
  } catch (err) {
    error('Quality gate failed');
    process.exit(1);
  }
}

async function dockerComposeUp() {
  const runDocker = process.env.DOCKER_COMPOSE === '1' || process.env.DOCKER_COMPOSE === 'true';
  
  if (!runDocker) {
    log('Skipping docker compose (set DOCKER_COMPOSE=1 to enable)');
    return;
  }
  
  log('Starting docker compose...');
  try {
    execSync('docker compose up -d', { 
      stdio: 'inherit',
      cwd: process.cwd()
    });
    log('✓ Docker compose started');
  } catch (err) {
    log('⚠️  Docker compose failed (continuing anyway)');
  }
}

async function startServer() {
  log('Starting server...');
  
  const serverProcess = spawn('node', ['main.js'], {
    env: { ...process.env },
    stdio: 'inherit',
    detached: true
  });
  
  serverProcess.unref();
  
  // Wait for server to start
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  log('✓ Server started');
}

async function runSeedDemo() {
  const runSeed = process.env.SKIP_SEED !== '1';
  
  if (!runSeed) {
    log('Skipping seed demo (SKIP_SEED=1)');
    return;
  }
  
  log('Running seed demo...');
  try {
    execSync('node scripts/seed-demo.cjs', { 
      stdio: 'inherit',
      cwd: process.cwd(),
      timeout: 10000
    });
    log('✓ Seed demo completed');
  } catch (err) {
    log('⚠️  Seed demo failed (continuing anyway)');
  }
}

async function main() {
  log('🚀 Starting grand opening sequence...');
  
  await runQualityGate();
  await dockerComposeUp();
  await startServer();
  await runSeedDemo();
  
  printBanner();
  
  log('✅ Grand opening complete!');
}

main().catch(err => {
  error(`Grand opening failed: ${err.message}`);
  process.exit(1);
});
