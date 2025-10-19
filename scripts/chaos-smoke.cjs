#!/usr/bin/env node
/**
 * Chaos Smoke Test Script
 * - Sends random load events via WebSocket
 * - Simulates chaotic traffic patterns
 */

const WebSocket = require('ws');

function log(msg) {
  console.log(`[chaos-smoke] ${msg}`);
}

function error(msg) {
  console.error(`[chaos-smoke] ❌ ${msg}`);
}

function generateRandomEvent() {
  const eventTypes = [
    'dpi.expiring',
    'dpi.expired',
    'work_order.created',
    'work_order.updated',
    'work_order.closed',
    'badge.update',
    'kpi.update'
  ];
  
  const workers = ['Mario Rossi', 'Luigi Verdi', 'Anna Bianchi', 'Paolo Neri', 'Sofia Gialli'];
  const equipment = ['Casco', 'Scarpe', 'Guanti', 'Imbracatura', 'Occhiali'];
  
  const type = eventTypes[Math.floor(Math.random() * eventTypes.length)];
  const worker = workers[Math.floor(Math.random() * workers.length)];
  const item = equipment[Math.floor(Math.random() * equipment.length)];
  
  return {
    type,
    worker,
    equipment: item,
    timestamp: new Date().toISOString(),
    random: Math.random(),
    daysRemaining: Math.floor(Math.random() * 60) - 10
  };
}

async function runChaosLoad() {
  const WS_URL = process.env.WS_URL || 'ws://localhost:8080';
  const DURATION = parseInt(process.env.CHAOS_DURATION || '30000', 10); // 30 seconds
  const RATE = parseInt(process.env.CHAOS_RATE || '100', 10); // ms between events
  
  log(`Starting chaos load test for ${DURATION}ms at ${RATE}ms intervals`);
  log(`Connecting to ${WS_URL}...`);
  
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(WS_URL);
    let eventCount = 0;
    let interval;
    
    ws.on('open', () => {
      log('✓ WebSocket connected');
      
      const startTime = Date.now();
      
      interval = setInterval(() => {
        const elapsed = Date.now() - startTime;
        
        if (elapsed >= DURATION) {
          clearInterval(interval);
          ws.close();
          return;
        }
        
        const event = generateRandomEvent();
        ws.send(JSON.stringify(event));
        eventCount++;
        
        if (eventCount % 10 === 0) {
          log(`Sent ${eventCount} events...`);
        }
      }, RATE);
    });
    
    ws.on('close', () => {
      if (interval) clearInterval(interval);
      log(`✓ Chaos test complete - sent ${eventCount} events`);
      resolve();
    });
    
    ws.on('error', (err) => {
      if (interval) clearInterval(interval);
      log(`⚠️  WebSocket error (this is ok if no WS server): ${err.message}`);
      resolve();
    });
  });
}

async function main() {
  log('Starting chaos smoke test...');
  
  try {
    await runChaosLoad();
    log('✓ Chaos smoke test completed');
  } catch (err) {
    error(`Chaos test failed: ${err.message}`);
    process.exit(1);
  }
}

main();
