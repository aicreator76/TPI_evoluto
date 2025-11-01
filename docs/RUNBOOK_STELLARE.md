# RUNBOOK_STELLARE

Questa runbook copre operazioni **Enterprise-STELLARE**: deploy, rollback, rotazione segreti e gestione incident.

## Deploy (GHCR + compose)
1. Tagga una release: `git tag Snapshot-OK-YYYY-MM-DD && git push origin --tags`
2. GitHub Actions builderà e pubblicherà l'immagine su GHCR.
3. In produzione, aggiorna lo stack (esempio):
   ```bash
   docker login ghcr.io
   docker pull ghcr.io/<owner>/<repo>:Snapshot-OK-YYYY-MM-DD
   docker compose up -d
   ```

## Rollback
1. Se la nuova versione è degradata, torna al tag precedente:
   ```bash
   docker pull ghcr.io/<owner>/<repo>:<prev-tag>
   docker compose up -d
   ```

## Rotazione segreti
- Mantenere .env **fuori** dal repo.
- Ruotare periodicamente credenziali DB e token esterni.
- In GitHub Actions: preferire `${{ secrets.* }}` o `GITHUB_TOKEN` con permessi minimi.

## Incident response
- Abilitare Code Scanning → ingest di `trivy.sarif`.
- Allegare gli artifact (coverage, audit) ai ticket d'incidente.
- Annotare `correlation_id` nei log per ogni richiesta (middleware applicativo).

## Verifiche post-deploy
- Smoke test endpoint principali.
- Controllare metriche base (error rate, p95, throughput) e storage DB.
