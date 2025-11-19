## Contesto
Attualmente TPI_evoluto lavora principalmente con CSV/Excel. Per andare verso un prodotto enterprise serve uno schema DB stabile (es. Postgres) con entità chiare e relazioni forti.

## Obiettivo
Definire lo schema dati minimo per gestire:
- aziende (tenant)
- utenti e ruoli
- DPI
- impianti anticaduta
- ispezioni
- allegati
- operatori, corsi e attestati (solo struttura base)

## Task
- [ ] Disegnare schema entità-relazioni (diagramma o README dedicato)
- [ ] Definire tabelle e chiavi primarie
- [ ] Definire relazioni fondamentali (FK) tra:
  - azienda → utenti / DPI / impianti / operatori
  - DPI → ispezioni / allegati
  - impianti → ispezioni / allegati
  - operatori → DPI assegnati / corsi / attestati
- [ ] Salvare schema in `docs/db/schema_TPI_v1.md` o immagine in `docs/db/`

## Criteri di accettazione
- [ ] Esiste un file di documentazione schema in `docs/db/`
- [ ] Tutte le entità critiche del dominio TPI sono rappresentate
- [ ] Le relazioni riflettono il flusso reale (azienda → impianto/DPI → operatore → ispezioni)
