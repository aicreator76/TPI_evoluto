#!/usr/bin/env node
/**
 * Database Snapshot Script
 * - Creates backup using better-sqlite3 backup or VACUUM INTO fallback
 */

const fs = require('fs');
const path = require('path');

function log(msg) {
  console.log(`[snapshot] ${msg}`);
}

function error(msg) {
  console.error(`[snapshot] ❌ ${msg}`);
}

async function createSnapshot() {
  const dbPath = process.env.DB_PATH || path.join(process.cwd(), 'data', 'app.db');
  const backupDir = process.env.BACKUP_DIR || path.join(process.cwd(), 'backups');
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const backupPath = path.join(backupDir, `snapshot-${timestamp}.db`);
  
  log(`Creating snapshot of ${dbPath}...`);
  
  // Check if database exists
  if (!fs.existsSync(dbPath)) {
    log('⚠️  Database not found, skipping snapshot');
    return;
  }
  
  // Create backup directory if it doesn't exist
  if (!fs.existsSync(backupDir)) {
    fs.mkdirSync(backupDir, { recursive: true });
    log(`Created backup directory: ${backupDir}`);
  }
  
  try {
    // Try using better-sqlite3 if available
    const Database = require('better-sqlite3');
    const db = new Database(dbPath, { readonly: true });
    
    log('Using better-sqlite3 backup method...');
    db.backup(backupPath)
      .then(() => {
        db.close();
        log(`✓ Snapshot created: ${backupPath}`);
        
        const stats = fs.statSync(backupPath);
        log(`Backup size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
      })
      .catch(err => {
        db.close();
        throw err;
      });
  } catch (err) {
    // Fallback to VACUUM INTO method
    log('better-sqlite3 not available, using VACUUM INTO fallback...');
    
    try {
      const sqlite3 = require('sqlite3');
      const db = new sqlite3.Database(dbPath);
      
      db.exec(`VACUUM INTO '${backupPath}'`, (err) => {
        db.close();
        
        if (err) {
          throw err;
        }
        
        log(`✓ Snapshot created: ${backupPath}`);
        const stats = fs.statSync(backupPath);
        log(`Backup size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
      });
    } catch (err2) {
      // Last fallback - simple file copy
      log('SQLite modules not available, using file copy...');
      fs.copyFileSync(dbPath, backupPath);
      log(`✓ Snapshot created: ${backupPath}`);
      
      const stats = fs.statSync(backupPath);
      log(`Backup size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
    }
  }
}

async function main() {
  log('Starting database snapshot...');
  
  try {
    await createSnapshot();
    log('✓ Snapshot completed');
  } catch (err) {
    error(`Snapshot failed: ${err.message}`);
    process.exit(1);
  }
}

main();
