# Cruscotto COMPITI-REGINA – TPI_evoluto

## Semaforo progetto (da STATO-REGNO)

- **Progetto TPI_evoluto**   : 🟡 avanzamento stabile, M1/M2 ancora aperte ma sotto controllo
- **Agente 0 / n8n**         : 🟡 SPEC in preparazione, nodo n8n ancora da accendere
- **Cruscotto vista Regina** : 🟡 prima versione attiva, da portare in routine quotidiana

### Regole semaforo (promemoria rapido)

- 🟢 tutto in pista, servizi chiave attivi, nessun blocco critico
- 🟡 si procede, ma c’è almeno un punto bloccante o da decidere
- 🔴 bloccato qualcosa di visibile alla Regina (servizi giù / task critico fermo)

---

## Obiettivi finestra 10 giorni (Agente 0 / n8n)

- [ ] Accendere n8n sul nodo di lavoro e salvare una config di base.
- [ ] Completare Fase 1 workflow Agente 0 (SPEC n8n + primo log di prova).
- [ ] Avere un report giornaliero minimo: `STATO-REGNO` + 3 TODO concreti.

---

## Ordini di lavoro ORCHESTRA-PRIME

Ordini validi per ORCHESTRA-PRIME (giornata 2025-11-22) →
vedi **`docs/ORDINI_ORCHESTRA_PRIME_2025-11-22.md`**.

---

## Cosa fare domani (3 punti POWER)

1. **n8n**
   Decidere e fissare per iscritto *come* verrà installato n8n
   (nodo, percorso es. `E:\CLONAZIONE\n8n`, log `E:\CLONAZIONE\n8n_logs`, utente che lo gestisce).

2. **Backend / Agente 0**
   Creare endpoint mock `GET /api/dpi/scadenze` in TPI_evoluto
   per permettere ad Agente 0 e a n8n di testare le notifiche DPI.

3. **Cronache della Regina**
   Aggiornare `docs/Cronache_Regina_YYYY-MM.md` con una riga sintetica:
   stato n8n (acceso/spento), cosa è stato fatto oggi su Agente 0, semaforo giornata (🟢🟡🔴).

---

_Versione cruscotto: 2025-11-22 – finestra 10 giorni Agente 0 / n8n._
