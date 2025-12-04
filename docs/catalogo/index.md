### Export DPI in CSV

Endpoint: `GET /api/dpi/csv/export`

Parametri:

- `gruppo` (opzionale) – filtra per gruppo DPI.
- `stato` (opzionale) – `ok` / `warning` / `scaduto`.
- `azienda_id` (opzionale) – multi-tenant.

Esempi:

- Tutti i DPI:
  `GET /api/dpi/csv/export`
- Solo warning 30 giorni:
  `GET /api/dpi/csv/export?stato=warning`
- Solo scaduti per azienda 2:
  `GET /api/dpi/csv/export?stato=scaduto&azienda_id=2`
