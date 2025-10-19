#!/usr/bin/env node
/**
 * Policy Check Script
 * - Fails if REQUIRE_OPA=1 and policy is absent
 * - Otherwise warns only
 */

const fs = require('fs');
const path = require('path');

function log(msg) {
  console.log(`[policy-check] ${msg}`);
}

function warn(msg) {
  console.warn(`[policy-check] ⚠️  ${msg}`);
}

function error(msg) {
  console.error(`[policy-check] ❌ ${msg}`);
}

function main() {
  log('Checking OPA policy...');
  
  const requireOpa = process.env.REQUIRE_OPA === '1' || process.env.REQUIRE_OPA === 'true';
  const policyPath = path.join(process.cwd(), 'policies', 'policy.rego');
  
  const policyExists = fs.existsSync(policyPath);
  
  if (!policyExists) {
    if (requireOpa) {
      error('OPA policy required (REQUIRE_OPA=1) but policy file not found');
      error(`Expected policy at: ${policyPath}`);
      process.exit(1);
    } else {
      warn('OPA policy file not found (this is optional)');
      warn(`Expected policy at: ${policyPath}`);
      log('Set REQUIRE_OPA=1 to make this check mandatory');
    }
  } else {
    log(`✓ OPA policy found at ${policyPath}`);
    
    // Basic validation - check if file is not empty
    const stats = fs.statSync(policyPath);
    if (stats.size === 0) {
      if (requireOpa) {
        error('OPA policy file is empty');
        process.exit(1);
      } else {
        warn('OPA policy file is empty');
      }
    } else {
      log(`✓ Policy file size: ${stats.size} bytes`);
    }
  }
  
  log('Policy check complete');
}

main();
