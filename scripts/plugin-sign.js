#!/usr/bin/env node
/**
 * Plugin Signing Script
 * - Signs a plugin file using ed25519
 * - Creates .sig signature file
 */

import crypto from 'crypto';
import { readFileSync, writeFileSync } from 'fs';

function log(msg) {
  console.log(`[plugin-sign] ${msg}`);
}

function error(msg) {
  console.error(`[plugin-sign] ❌ ${msg}`);
}

async function signPlugin() {
  const pluginPath = process.argv[2];
  const privateKeyPath = process.argv[3];
  
  if (!pluginPath || !privateKeyPath) {
    error('Usage: node plugin-sign.js <plugin-file> <private-key-file>');
    process.exit(1);
  }
  
  log(`Signing plugin: ${pluginPath}`);
  
  try {
    // Read plugin file
    const pluginData = readFileSync(pluginPath);
    
    // Read private key
    const privateKey = readFileSync(privateKeyPath, 'utf8');
    
    // Calculate SHA-256 digest
    const hash = crypto.createHash('sha256').update(pluginData).digest();
    
    // Sign using ed25519
    const sign = crypto.createSign('SHA256');
    sign.update(hash);
    sign.end();
    
    const signature = sign.sign(privateKey);
    
    // Write signature file
    const signaturePath = pluginPath + '.sig';
    writeFileSync(signaturePath, signature);
    
    log(`✓ Signature created: ${signaturePath}`);
    log(`Signature size: ${signature.length} bytes`);
  } catch (err) {
    error(`Signing failed: ${err.message}`);
    process.exit(1);
  }
}

signPlugin();
