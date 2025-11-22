## ORDINI ORCHESTRA-PRIME – PROSSIMA SESSIONE (POWER)

### 1️⃣ PULIZIA & COMMIT REGINA

**Obiettivo:** portare in Git, in modo pulito, cruscotto, ordini e SPEC agenti MindStudio.

**Passi operativi (branch `orchestra/build-tpi-stub`):**

1. Normalizzare i 5 file (TrimEnd + newline finale):

   - docs/CRUSCOTTO_COMPITI_REGINA_2025-11-22.md
   - docs/ORDINI_ORCHESTRA_PRIME_2025-11-22.md
   - docs/AGENTI_DEL_REGNO_OVERVIEW.md
   - docs/orchestrator/AGENTE_COMPITI_REGINA_SPEC.md
   - docs/orchestrator/AGENTE_ORCHESTRA_CHECK_SPEC.md

2. Eseguire i hook di pre-commit solo su questi file:

   ```powershell
   cd E:\CLONAZIONE\tpi_evoluto
   pre-commit run --files `
     docs/CRUSCOTTO_COMPITI_REGINA_2025-11-22.md `
     docs/ORDINI_ORCHESTRA_PRIME_2025-11-22.md `
     docs/AGENTI_DEL_REGNO_OVERVIEW.md `
     docs/orchestrator/AGENTE_COMPITI_REGINA_SPEC.md `
     docs/orchestrator/AGENTE_ORCHESTRA_CHECK_SPEC.md
