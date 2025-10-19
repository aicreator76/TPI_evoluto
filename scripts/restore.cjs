#!/usr/bin/env node
/**
 * Database Restore Script
 * - Restores database from provided backup
 * - Creates pre-restore backup
 * - Removes WAL/SHM files
 */

const fs = require('fs');
const path = require('path');

function log(msg) {
  console.log(`[restore] ${msg}`);
}

function error(msg) {
  console.error(`[restore] ❌ ${msg}`);
}

async function restoreDatabase() {
  const backupPath = process.argv[2];
  
  if (!backupPath) {
    error('Usage: node restore.cjs <backup-file-path>');
    process.exit(1);
  }
  
  if (!fs.existsSync(backupPath)) {
    error(`Backup file not found: ${backupPath}`);
    process.exit(1);
  }
  
  const dbPath = process.env.DB_PATH || path.join(process.cwd(), 'data', 'app.db');
  const dbDir = path.dirname(dbPath);
  
  log(`Restoring from ${backupPath} to ${dbPath}...`);
  
  // Create data directory if it doesn't exist
  if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
    log(`Created data directory: ${dbDir}`);
  }
  
  // Create pre-restore backup if database exists
  if (fs.existsSync(dbPath)) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const preRestoreBackup = path.join(dbDir, `pre-restore-${timestamp}.db`);
    
    log('Creating pre-restore backup...');
    fs.copyFileSync(dbPath, preRestoreBackup);
    log(`✓ Pre-restore backup created: ${preRestoreBackup}`);
    
    // Remove WAL and SHM files
    const walPath = dbPath + '-wal';
    const shmPath = dbPath + '-shm';
    
    if (fs.existsSync(walPath)) {
      fs.unlinkSync(walPath);
      log('✓ Removed WAL file');
    }
    
    if (fs.existsSync(shmPath)) {
      fs.unlinkSync(shmPath);
      log('✓ Removed SHM file');
    }
  }
  
  // Restore from backup
  log('Restoring database...');
  fs.copyFileSync(backupPath, dbPath);
  
  const stats = fs.statSync(dbPath);
  log(`✓ Database restored: ${dbPath}`);
  log(`Database size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
  
  // Verify database integrity (if sqlite3 is available)
  try {
    const Database = require('better-sqlite3');
    const db = new Database(dbPath, { readonly: true });
    
    const result = db.pragma('integrity_check');
    db.close();
    
    if (result[0].integrity_check === 'ok') {
      log('✓ Database integrity check passed');
    } else {
      error('Database integrity check failed');
      log(result);
    }
  } catch (err) {
    log('⚠️  Could not verify database integrity (better-sqlite3 not available)');
  }
}

async function main() {
  log('Starting database restore...');
  
  try {
    await restoreDatabase();
    log('✓ Restore completed');
  } catch (err) {
    error(`Restore failed: ${err.message}`);
    process.exit(1);
  }
}

main();
