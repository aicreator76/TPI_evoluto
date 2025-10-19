#!/usr/bin/env node
/**
 * Seed Demo Script
 * - Sends demo events via WebSocket
 */

const WebSocket = require('ws');

function log(msg) {
  console.log(`[seed-demo] ${msg}`);
}

function error(msg) {
  console.error(`[seed-demo] ❌ ${msg}`);
}

const demoEvents = [
  {
    type: 'dpi.expiring',
    worker: 'Mario Rossi',
    equipment: 'Casco protettivo',
    daysRemaining: 15,
    priority: 'medium'
  },
  {
    type: 'dpi.expired',
    worker: 'Luigi Verdi',
    equipment: 'Scarpe antinfortunistiche',
    daysRemaining: -5,
    priority: 'high'
  },
  {
    type: 'work_order.created',
    orderId: 'WO-2025-001',
    worker: 'Luigi Verdi',
    equipment: 'Scarpe antinfortunistiche',
    status: 'pending'
  }
];

async function sendDemoEvents() {
  const WS_URL = process.env.WS_URL || 'ws://localhost:8080';
  
  log(`Connecting to ${WS_URL}...`);
  
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(WS_URL);
    let eventIndex = 0;
    
    ws.on('open', () => {
      log('✓ WebSocket connected');
      
      // Send events with delay
      const interval = setInterval(() => {
        if (eventIndex >= demoEvents.length) {
          clearInterval(interval);
          ws.close();
          return;
        }
        
        const event = demoEvents[eventIndex];
        log(`Sending event ${eventIndex + 1}/${demoEvents.length}: ${event.type}`);
        ws.send(JSON.stringify(event));
        eventIndex++;
      }, 500);
    });
    
    ws.on('message', (data) => {
      log(`Received: ${data}`);
    });
    
    ws.on('close', () => {
      log('✓ WebSocket closed');
      resolve();
    });
    
    ws.on('error', (err) => {
      // If connection fails, it's likely because there's no WebSocket server
      // This is ok for demo purposes
      log(`⚠️  WebSocket error (this is ok if no WS server): ${err.message}`);
      resolve();
    });
    
    // Timeout after 10 seconds
    setTimeout(() => {
      ws.close();
      resolve();
    }, 10000);
  });
}

async function main() {
  log('Starting demo seed...');
  
  try {
    await sendDemoEvents();
    log('✓ Demo seed completed');
  } catch (err) {
    error(`Seed failed: ${err.message}`);
    process.exit(1);
  }
}

main();
