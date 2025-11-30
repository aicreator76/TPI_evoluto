# Endpoint mock scadenze DPI

## GET /api/dpi/scadenze

Scopo:
- Fornire ad Agente 0 (n8n) una lista DPI con scadenza e email destinatario.

Risposta mock (Fase 1):

[
  {
    ""codice_dpi"": ""IMBRACATURA-001"",
    ""data_scadenza"": ""2026-01-31"",
    ""stato"": ""IN_SCADENZA"",
    ""email_destinatario"": ""operatore@example.com""
  }
]

Note:
- In Fase 1 basta che l'endpoint esista e risponda con un JSON fisso.
- In Fase 2 leggerà dal DB TPI_evoluto.
