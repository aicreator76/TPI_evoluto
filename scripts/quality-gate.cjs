#!/usr/bin/env node
/**
 * Quality Gate Script
 * - Checks Node version (semver)
 * - Runs npm audit with tolerance
 * - Starts app on temporary port and verifies /health and /metrics
 * - Fails if endpoints not responding
 */

const { execSync, spawn } = require('child_process');
const http = require('http');
const semver = require('semver');

const REQUIRED_NODE_VERSION = '>=18.0.0';
const TEST_PORT = 9999;
const AUDIT_TOLERANCE = 'moderate'; // low, moderate, high, critical

function log(msg) {
  console.log(`[quality-gate] ${msg}`);
}

function error(msg) {
  console.error(`[quality-gate] ❌ ${msg}`);
}

function checkNodeVersion() {
  log('Checking Node.js version...');
  const currentVersion = process.version;
  
  if (!semver.satisfies(currentVersion, REQUIRED_NODE_VERSION)) {
    error(`Node.js version ${currentVersion} does not satisfy ${REQUIRED_NODE_VERSION}`);
    process.exit(1);
  }
  
  log(`✓ Node.js version ${currentVersion} OK`);
}

function runNpmAudit() {
  log('Running npm audit...');
  try {
    execSync(`npm audit --audit-level=${AUDIT_TOLERANCE}`, { 
      stdio: 'inherit',
      cwd: process.cwd()
    });
    log('✓ npm audit passed');
  } catch (err) {
    error('npm audit failed with vulnerabilities above tolerance level');
    process.exit(1);
  }
}

function httpGet(port, path) {
  return new Promise((resolve, reject) => {
    const req = http.get(`http://localhost:${port}${path}`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          resolve({ status: res.statusCode, data });
        } else {
          reject(new Error(`HTTP ${res.statusCode}`));
        }
      });
    });
    
    req.on('error', reject);
    req.setTimeout(5000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
  });
}

async function verifyEndpoints() {
  log(`Starting app on port ${TEST_PORT} for verification...`);
  
  const appProcess = spawn('node', ['main.js'], {
    env: { ...process.env, PORT: TEST_PORT },
    stdio: 'pipe'
  });
  
  let appOutput = '';
  appProcess.stdout.on('data', data => appOutput += data.toString());
  appProcess.stderr.on('data', data => appOutput += data.toString());
  
  // Wait for app to start
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  try {
    // Check /health endpoint
    log('Checking /health endpoint...');
    const healthRes = await httpGet(TEST_PORT, '/health');
    log(`✓ /health responded: ${healthRes.data.substring(0, 100)}`);
    
    // Check /metrics endpoint
    log('Checking /metrics endpoint...');
    const metricsRes = await httpGet(TEST_PORT, '/metrics');
    log(`✓ /metrics responded: ${metricsRes.data.substring(0, 100)}`);
    
    log('✓ All endpoints verified successfully');
  } catch (err) {
    error(`Endpoint verification failed: ${err.message}`);
    log('App output:\n' + appOutput);
    appProcess.kill();
    process.exit(1);
  }
  
  appProcess.kill();
  log('✓ Quality gate passed!');
}

async function main() {
  log('Starting quality gate checks...');
  
  checkNodeVersion();
  
  // Only run npm audit if node_modules exists
  try {
    const fs = require('fs');
    if (fs.existsSync('node_modules')) {
      runNpmAudit();
    } else {
      log('⚠️  node_modules not found, skipping npm audit');
    }
  } catch (err) {
    log('⚠️  Skipping npm audit');
  }
  
  await verifyEndpoints();
  
  log('🎉 All quality gate checks passed!');
}

main().catch(err => {
  error(`Quality gate failed: ${err.message}`);
  process.exit(1);
});
