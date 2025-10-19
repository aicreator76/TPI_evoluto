#!/usr/bin/env node

const https = require('https');
const http = require('http');

// Parse environment variables
const targets = (process.env.TARGETS || '').split(',').map(t => t.trim()).filter(Boolean);
const errorRateThreshold = parseFloat(process.env.ERROR_RATE_THRESHOLD || '0.01');
const latencyP95Ms = parseInt(process.env.LATENCY_P95_MS || '800', 10);
const durationSec = parseInt(process.env.DURATION_SEC || '300', 10);
const intervalMs = parseInt(process.env.INTERVAL_MS || '5000', 10);
const discordWebhook = process.env.DISCORD_WEBHOOK;
const slackWebhook = process.env.SLACK_WEBHOOK;

console.log('🔍 Canary Health Monitor starting...');
console.log(`Targets: ${targets.join(', ')}`);
console.log(`Duration: ${durationSec}s, Interval: ${intervalMs}ms`);
console.log(`Thresholds: Error Rate < ${errorRateThreshold * 100}%, P95 < ${latencyP95Ms}ms`);

const results = {
  requests: 0,
  errors: 0,
  latencies: []
};

async function checkEndpoint(url) {
  return new Promise((resolve) => {
    const startTime = Date.now();
    const client = url.startsWith('https') ? https : http;
    
    const req = client.get(url, { timeout: 10000 }, (res) => {
      const latency = Date.now() - startTime;
      const success = res.statusCode >= 200 && res.statusCode < 400;
      
      res.resume(); // Consume response
      resolve({ success, latency });
    });
    
    req.on('error', () => {
      const latency = Date.now() - startTime;
      resolve({ success: false, latency });
    });
    
    req.on('timeout', () => {
      req.destroy();
      const latency = Date.now() - startTime;
      resolve({ success: false, latency });
    });
  });
}

async function runCheck() {
  for (const target of targets) {
    const result = await checkEndpoint(target);
    results.requests++;
    results.latencies.push(result.latency);
    
    if (!result.success) {
      results.errors++;
      console.log(`❌ ${target} failed (${result.latency}ms)`);
    } else {
      console.log(`✅ ${target} ok (${result.latency}ms)`);
    }
  }
}

function calculateP95() {
  if (results.latencies.length === 0) return 0;
  const sorted = [...results.latencies].sort((a, b) => a - b);
  const index = Math.ceil(sorted.length * 0.95) - 1;
  return sorted[index];
}

async function sendNotification(message) {
  const payload = JSON.stringify({ content: message, text: message });
  
  const webhooks = [discordWebhook, slackWebhook].filter(Boolean);
  
  for (const webhook of webhooks) {
    try {
      const url = new URL(webhook);
      const client = url.protocol === 'https:' ? https : http;
      
      await new Promise((resolve, reject) => {
        const req = client.request(webhook, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(payload)
          }
        }, (res) => {
          res.resume();
          resolve();
        });
        
        req.on('error', reject);
        req.write(payload);
        req.end();
      });
    } catch (err) {
      console.error(`Failed to send notification to ${webhook}:`, err.message);
    }
  }
}

async function main() {
  const endTime = Date.now() + (durationSec * 1000);
  
  while (Date.now() < endTime) {
    await runCheck();
    await new Promise(resolve => setTimeout(resolve, intervalMs));
  }
  
  const errorRate = results.requests > 0 ? results.errors / results.requests : 0;
  const p95 = calculateP95();
  
  console.log('\n📊 Final Results:');
  console.log(`Total Requests: ${results.requests}`);
  console.log(`Total Errors: ${results.errors}`);
  console.log(`Error Rate: ${(errorRate * 100).toFixed(2)}%`);
  console.log(`P95 Latency: ${p95}ms`);
  
  const failed = errorRate > errorRateThreshold || p95 > latencyP95Ms;
  
  if (failed) {
    const message = `🚨 Canary validation FAILED!\nError Rate: ${(errorRate * 100).toFixed(2)}% (threshold: ${errorRateThreshold * 100}%)\nP95 Latency: ${p95}ms (threshold: ${latencyP95Ms}ms)`;
    console.error(`\n${message}`);
    await sendNotification(message);
    process.exit(1);
  } else {
    const message = `✅ Canary validation PASSED\nError Rate: ${(errorRate * 100).toFixed(2)}%\nP95 Latency: ${p95}ms`;
    console.log(`\n${message}`);
    await sendNotification(message);
    process.exit(0);
  }
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
