import os
import json
import re
from datetime import datetime, date
from typing import Dict, Any

import pandas as pd

# Root del progetto (override possibile con env var TPI_ROOT)
ROOT = os.environ.get("TPI_ROOT", r"E:\CLONAZIONE\tpi_evoluto")

LOG_DIR = os.path.join(ROOT, "logs")
CRUSCOTTO_JSON = os.path.join(LOG_DIR, "agente0_dashboard.json")
CRUSCOTTO_HTML = os.path.join(LOG_DIR, "agente0_cruscotto.html")

DPI_CSV = os.path.join(ROOT, "data", "dpi.csv")

# Parametri di business
WARNING_DAYS = 30  # soglia warning in giorni
MIN_VALID_YEAR = 1910  # sotto questo anno la data è considerata anomala

# Regex per formati frequenti
_RE_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")  # 2025-12-22
_RE_ISO_DATE_SLASH = re.compile(r"^\d{4}/\d{2}/\d{2}$")  # 2025/12/22
_RE_IT_DATE_SLASH = re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$")  # 22/12/2025
_RE_IT_DATE_DASH = re.compile(r"^\d{1,2}-\d{1,2}-\d{4}$")  # 22-12-2025
_RE_STARTS_WITH_YEAR = re.compile(r"^\d{4}[-/]")


def carica_dpi_da_csv() -> pd.DataFrame:
    """Carica il file DPI; genera errore chiaro se manca."""
    if not os.path.exists(DPI_CSV):
        raise FileNotFoundError(f"File DPI non trovato: {DPI_CSV}")

    # dtype=str evita letture strane (es. scadenze numeriche) e conserva zeri iniziali
    df = pd.read_csv(DPI_CSV, dtype=str)

    if "scadenza" not in df.columns:
        raise KeyError(
            f"Colonna 'scadenza' non trovata in {DPI_CSV}. Colonne presenti: {list(df.columns)}"
        )

    return df


def calcola_semaforo(ok: int, warning: int, scaduti: int, anomalie: int) -> str:
    """
    Regole semaforo modulo DPI:
    - ROSSO: almeno 1 scaduto oppure anomalie > 0
    - GIALLO: nessun scaduto, ma almeno 1 warning
    - VERDE: tutto il resto (solo OK)
    """
    if scaduti > 0 or anomalie > 0:
        return "ROSSO"
    if warning > 0:
        return "GIALLO"
    return "VERDE"


def _parse_scadenza(raw_val: Any) -> date:
    """
    Parsing deterministico:
    - ISO: YYYY-MM-DD / YYYY/MM/DD  -> dayfirst False
    - IT:  DD/MM/YYYY / DD-MM-YYYY  -> dayfirst True
    - Fallback: dayfirst dipende da "inizia con anno?"
    """
    if raw_val is None or pd.isna(raw_val):
        raise ValueError("scadenza vuota")

    s = str(raw_val).strip()
    if not s:
        raise ValueError("scadenza vuota")

    # ISO secco (niente warning, formato esplicito)
    if _RE_ISO_DATE.match(s):
        return pd.to_datetime(s, format="%Y-%m-%d", errors="raise").date()
    if _RE_ISO_DATE_SLASH.match(s):
        return pd.to_datetime(s, format="%Y/%m/%d", errors="raise").date()

    # IT secco (formato esplicito)
    if _RE_IT_DATE_SLASH.match(s):
        return pd.to_datetime(s, format="%d/%m/%Y", errors="raise").date()
    if _RE_IT_DATE_DASH.match(s):
        return pd.to_datetime(s, format="%d-%m-%Y", errors="raise").date()

    # Fallback controllato (evita warning: se parte con anno -> dayfirst False)
    dayfirst = not bool(_RE_STARTS_WITH_YEAR.match(s))
    return pd.to_datetime(s, dayfirst=dayfirst, errors="raise").date()


def calcola_cruscotto(df: pd.DataFrame) -> Dict[str, Any]:
    """Calcola numeri DPI + contatore errori data + semaforo modulo."""
    totale = int(len(df))

    ok = 0
    warning = 0
    scaduti = 0
    anomalie = 0
    righe_errore_data = 0

    oggi: date = datetime.now().date()

    for _, riga in df.iterrows():
        raw_val = riga.get("scadenza", "")

        try:
            data_scad = _parse_scadenza(raw_val)
        except Exception:
            anomalie += 1
            righe_errore_data += 1
            continue

        # Date marce tipo 01/01/1900 ecc.
        if data_scad.year < MIN_VALID_YEAR:
            anomalie += 1
            righe_errore_data += 1
            continue

        diff = (data_scad - oggi).days

        if diff < 0:
            scaduti += 1
        elif diff <= WARNING_DAYS:
            warning += 1
        else:
            ok += 1

    semaforo = calcola_semaforo(ok=ok, warning=warning, scaduti=scaduti, anomalie=anomalie)

    return {
        "totale_dpi": totale,
        "ok": ok,
        "warning": warning,
        "scaduti": scaduti,
        "anomalie": anomalie,
        "righe_errore_data": righe_errore_data,
        "semaforo_modulo_dpi": semaforo,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }


def salva_cruscotto(cruscotto: Dict[str, Any]) -> None:
    """Scrive JSON + HTML del cruscotto DPI."""
    os.makedirs(LOG_DIR, exist_ok=True)

    # JSON
    with open(CRUSCOTTO_JSON, "w", encoding="utf-8") as f:
        json.dump(cruscotto, f, indent=2, ensure_ascii=False)

    # HTML semplice ma informativo
    html = f"""<html>
<head>
  <meta charset="UTF-8">
  <title>Cruscotto DPI</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 20px;
    }}
    .semaforo {{
      font-size: 1.4em;
      font-weight: bold;
    }}
  </style>
</head>
<body>
<h1>Cruscotto DPI</h1>

<p class="semaforo">Semaforo modulo DPI: {cruscotto["semaforo_modulo_dpi"]}</p>
<p><strong>Ultimo aggiornamento:</strong> {cruscotto["updated_at"]}</p>

<ul>
  <li>Totale DPI: {cruscotto["totale_dpi"]}</li>
  <li>OK: {cruscotto["ok"]}</li>
  <li>Warning (≤{WARNING_DAYS}gg): {cruscotto["warning"]}</li>
  <li>Scaduti: {cruscotto["scaduti"]}</li>
  <li>Anomalie: {cruscotto["anomalie"]}</li>
  <li>Righe con errore data: {cruscotto["righe_errore_data"]}</li>
</ul>
</body>
</html>
"""
    with open(CRUSCOTTO_HTML, "w", encoding="utf-8") as f:
        f.write(html)


def main() -> None:
    df = carica_dpi_da_csv()
    cruscotto = calcola_cruscotto(df)
    salva_cruscotto(cruscotto)
    print("[AGENTE0] Cruscotto rigenerato")
    print("[AGENTE0] JSON:", CRUSCOTTO_JSON)
    print("[AGENTE0] HTML:", CRUSCOTTO_HTML)


if __name__ == "__main__":
    main()
