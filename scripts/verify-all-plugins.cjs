#!/usr/bin/env node
/**
 * Plugin Verification Script
 * - Verifies plugin signatures using ed25519
 * - Uses SHA-256 digest
 * - Tolerant to missing modules directory or public key
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

function log(msg) {
  console.log(`[verify-plugins] ${msg}`);
}

function warn(msg) {
  console.warn(`[verify-plugins] ⚠️  ${msg}`);
}

function error(msg) {
  console.error(`[verify-plugins] ❌ ${msg}`);
}

function verifyPluginSignature(pluginPath, publicKeyPath) {
  try {
    // Read plugin file
    const pluginData = fs.readFileSync(pluginPath);
    
    // Read signature file
    const signaturePath = pluginPath + '.sig';
    if (!fs.existsSync(signaturePath)) {
      warn(`No signature file found for ${path.basename(pluginPath)}`);
      return false;
    }
    
    const signature = fs.readFileSync(signaturePath);
    
    // Read public key
    if (!fs.existsSync(publicKeyPath)) {
      warn(`Public key not found at ${publicKeyPath}`);
      return false;
    }
    
    const publicKey = fs.readFileSync(publicKeyPath, 'utf8');
    
    // Calculate SHA-256 digest
    const hash = crypto.createHash('sha256').update(pluginData).digest();
    
    // Verify signature using ed25519
    const verify = crypto.createVerify('SHA256');
    verify.update(hash);
    verify.end();
    
    const isValid = verify.verify(publicKey, signature);
    
    if (isValid) {
      log(`✓ ${path.basename(pluginPath)} signature valid`);
      return true;
    } else {
      error(`Invalid signature for ${path.basename(pluginPath)}`);
      return false;
    }
  } catch (err) {
    error(`Error verifying ${path.basename(pluginPath)}: ${err.message}`);
    return false;
  }
}

function main() {
  log('Starting plugin verification...');
  
  const modulesDir = path.join(process.cwd(), 'modules');
  const publicKeyPath = path.join(process.cwd(), 'keys', 'plugin-public.pem');
  
  // Check if modules directory exists
  if (!fs.existsSync(modulesDir)) {
    warn('Modules directory not found, skipping verification');
    return;
  }
  
  // Check if public key exists
  if (!fs.existsSync(publicKeyPath)) {
    warn('Public key not found, skipping signature verification');
    return;
  }
  
  // Find all plugin files
  const files = fs.readdirSync(modulesDir);
  const pluginFiles = files.filter(f => f.endsWith('.js') && !f.endsWith('.sig'));
  
  if (pluginFiles.length === 0) {
    log('No plugin files found to verify');
    return;
  }
  
  log(`Found ${pluginFiles.length} plugin(s) to verify`);
  
  let allValid = true;
  for (const file of pluginFiles) {
    const pluginPath = path.join(modulesDir, file);
    const isValid = verifyPluginSignature(pluginPath, publicKeyPath);
    if (!isValid) {
      allValid = false;
    }
  }
  
  if (allValid) {
    log('✓ All plugins verified successfully');
  } else {
    error('Some plugins failed verification');
    process.exit(1);
  }
}

main();
