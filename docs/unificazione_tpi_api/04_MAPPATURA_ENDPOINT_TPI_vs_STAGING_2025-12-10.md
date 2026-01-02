# 04 – MAPPATURA ENDPOINT TPI_evoluto vs TPI_api_staging (2025-12-10)

Questo file va COMPILATO a partire dai diff salvati:

- Struttura cartelle:
  - `11_diff_struttura_cartelle_2025-12-10.txt`
- Diff git:
  - `12_diff_git_tpi_evoluto_2025-12-10.txt`
  - `13_diff_git_tpi_api_staging_2025-12-10.txt`
- Elenco file .py:
  - `21_file_py_tpi_evoluto_2025-12-10.txt`
  - `22_file_py_tpi_api_staging_2025-12-10.txt`

## Tabella endpoint chiave

| # | Funzione business                 | TPI_evoluto – path/metodo         | TPI_api_staging – path/metodo     | Note / Azioni                        |
|---|-----------------------------------|------------------------------------|------------------------------------|--------------------------------------|
| 1 | Healthcheck API                   | /health (es.)                      | /healthz (es.)                     | Allineare nome/risposta              |
| 2 | Versione servizio                 | /version                           | /version                           | Verificare payload                   |
| 3 | Listino ACCESSORI (demo)         | /api/accessori/listino            | …                                  | Uniformare schema risposta           |
| 4 | Overview ACCESSORI (se esiste)    | /api/accessori/overview           | …                                  |                                      |
| 5 | Altro endpoint “vetrina”          | …                                  | …                                  |                                      |

> Compilazione manuale:
> - per ogni endpoint trovati nei due repo,
> - indicare path, metodo (GET/POST/…), payload,
> - segnare se TPI_api_staging deve adeguarsi a TPI_evoluto o viceversa.
