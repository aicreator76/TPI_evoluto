## Contesto
Per convincere clienti enterprise e tutelare legalmente, serve un audit trail completo delle azioni su DPI/impianti/ispezioni.

## Obiettivo
Introdurre un audit log centrale e la possibilità di generare un report "legale" esportabile.

## Task
- [ ] Definire tabella `AuditLog` (utente, ruolo, tenant, azione, risorsa, timestamp, metadati)
- [ ] Integrare audit logging nelle operazioni critiche:
  - creazione/modifica/cancellazione DPI
  - creazione/modifica ispezioni
  - cambio stato impianti
- [ ] Implementare endpoint per estrarre audit log filtrato per:
  - intervallo di date
  - tenant
  - tipo risorsa
- [ ] Aggiungere generazione report (anche solo CSV/Excel, PDF in step successivo)

## Criteri di accettazione
- [ ] Ogni azione critica genera una riga in `AuditLog`
- [ ] È possibile estrarre un report di audit per un periodo
- [ ] Almeno un test end-to-end verifica la catena: azione → log → export
