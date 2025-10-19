# Observability – Aelis

## Endpoint
- `/health` → 200 OK con heartbeat.
- `/metrics` → Prometheus exposition (stessa porta 8080).
- `/observability/metrics` → alias JSON (compat), opzionale array con snapshot metriche principali.

## Prometheus scrape
```yaml
scrape_configs:
  - job_name: 'aelis'
    static_configs:
      - targets: ['host.docker.internal:8080']  # dev
```

## Dashboard (Grafana)

Pannelli suggeriti:

- `rate(http_requests_total[5m])` per rotta

- `p95 latency` (histogram quantile se disponibile) o quantile approssimato client-side

- `error rate 5xx`

Alert:

- `5xx_rate > 1%` per 5m

- `p95_latency > 800ms` per 5m


> Nota: hai già l'alias `/observability/metrics → /metrics` nel server; lascia `/metrics` come sorgente unica per Prometheus.
