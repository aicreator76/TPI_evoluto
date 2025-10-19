#!/usr/bin/env node

const https = require('https');
const http = require('http');

const discordWebhook = process.env.DISCORD_WEBHOOK;
const slackWebhook = process.env.SLACK_WEBHOOK;

console.log('🔧 Self-heal notification starting...');

async function sendNotification(message) {
  const payload = JSON.stringify({ 
    content: message, 
    text: message,
    username: 'Self-Heal Bot'
  });
  
  const webhooks = [discordWebhook, slackWebhook].filter(Boolean);
  
  if (webhooks.length === 0) {
    console.log('No webhooks configured, skipping notification');
    return;
  }
  
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
          },
          timeout: 10000
        }, (res) => {
          res.resume();
          if (res.statusCode >= 200 && res.statusCode < 300) {
            console.log(`✅ Notification sent to webhook`);
            resolve();
          } else {
            reject(new Error(`HTTP ${res.statusCode}`));
          }
        });
        
        req.on('error', reject);
        req.on('timeout', () => {
          req.destroy();
          reject(new Error('Request timeout'));
        });
        
        req.write(payload);
        req.end();
      });
    } catch (err) {
      console.error(`❌ Failed to send notification to ${webhook}:`, err.message);
    }
  }
}

async function main() {
  const message = `🚨 ROLLBACK TRIGGERED\n\nDeployment failed canary validation and has been rolled back.\nAction required: Review logs and investigate deployment issues.\n\nTimestamp: ${new Date().toISOString()}`;
  
  console.log(message);
  await sendNotification(message);
  console.log('Self-heal notification complete');
}

main().catch((err) => {
  console.error('Error in self-heal script:', err);
  process.exit(1);
});
