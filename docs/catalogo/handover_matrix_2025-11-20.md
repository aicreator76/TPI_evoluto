# Handover Catalogo DPI – Matrix SPEC vs TEST (2025-11-20)

| # | Requisito Handover                               | Stato   | Test / file                              |
|---|--------------------------------------------------|---------|------------------------------------------|
| 1 | SHA256 / idempotenza file pulito                | TODO | test_app/test_import_sha256.py           |
| 2 | Dedup globale (codice DPI / matricola / seriale) | PARTIAL | test_app/test_dedup_dpi.py               |
| 3 | Rifiuto .xlsm con MACRO_DETECTED (422)          | TODO | test_app/test_import_block_xlsm.py       |
| 4 | Limite ZIP (≤50 file, ≤200MB, ≤5MB per file)    | TODO | test_app/test_import_zip_limits.py       |
| 5 | Osservabilità JSONL + X-Correlation-ID          | PARTIAL | test_app/test_logging_correlation_id.py  |
| 6 | Export short/extended del catalogo              | PARTIAL | test_app/test_export_catalogo.py         |
| 7 | Report HTML DPI catalogo                        | PARTIAL | test_app/test_report_html.py             |
| 8 | Endpoint /api/dpi/csv/metrics                   | TODO | test_app/test_dpi_metrics.py             |
| 9 | Template CSV versione 1 con header stabile      | PARTIAL | test_app/test_template_versioning.py     |

> NOTE:
> - Stato: DONE / PARTIAL / TODO
> - Aggiornare il campo "Test / file" quando il caso di test esiste davvero nel repo.
