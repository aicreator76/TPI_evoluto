from datetime import datetime
import pandas as pd


def _scegli_colonna_scadenza(df: pd.DataFrame, config: dict) -> str:
    """
    Trova la colonna data scadenza:
    - prima prova config["date_column"]
    - se non esiste, sceglie la prima colonna che contiene "scadenza"
    """
    cfg_name = config.get("date_column")
    if cfg_name:
        name = cfg_name.strip().lower()
        if name in df.columns:
            return name

    candidates = [c for c in df.columns if "scadenza" in c]
    if not candidates:
        raise ValueError(
            f"Nessuna colonna di scadenza trovata. Colonne disponibili: {list(df.columns)}"
        )
    return candidates[0]


def classify_dpi(df: pd.DataFrame, config: dict):
    """
    Classifica i DPI in:
    - OK / WARNING / SCADUTO
    - ANOMALO      -> date valide ma con anno < 2000
    - ERRORE_DATA  -> date non interpretabili
    """

    date_col = _scegli_colonna_scadenza(df, config)

    # normalizzo la colonna in datetime (NaT se non interpretabile)
    date_series = pd.to_datetime(df[date_col], errors="coerce")

    today = datetime.now().date()
    warning_levels = config.get("days_warning", [60, 30, 15])
    max_warn = max(warning_levels) if warning_levels else 60

    giorni_rimanenti = []
    stati = []

    for v in date_series:
        # data non interpretabile
        if pd.isna(v):
            giorni_rimanenti.append(pd.NA)
            stati.append("ERRORE_DATA")
            continue

        try:
            d = v.date()
            year = d.year
        except Exception:
            giorni_rimanenti.append(pd.NA)
            stati.append("ERRORE_DATA")
            continue

        # ANOMALIA: data nel passato remoto (es. 1900)
        if year < 2000:
            giorni_rimanenti.append(pd.NA)
            stati.append("ANOMALO")
            continue

        # caso normale: calcolo giorni rimanenti
        diff = (d - today).days
        giorni_rimanenti.append(diff)

        if diff < 0:
            stati.append("SCADUTO")
        elif diff <= max_warn:
            stati.append("WARNING")
        else:
            stati.append("OK")

    df["giorni_rimanenti"] = giorni_rimanenti
    df["stato_scadenza"] = stati

    totale = int(len(df))
    ok = int((df["stato_scadenza"] == "OK").sum())
    warning = int((df["stato_scadenza"] == "WARNING").sum())
    scaduti = int((df["stato_scadenza"] == "SCADUTO").sum())
    anomali = int((df["stato_scadenza"] == "ANOMALO").sum())
    errore_data = int((df["stato_scadenza"] == "ERRORE_DATA").sum())
    righe_errore_data = anomali + errore_data

    summary = {
        "totale": totale,
        "totale_dpi": totale,
        "ok": ok,
        "warning": warning,
        "scaduti": scaduti,
        "anomali": anomali,
        "errore_data": errore_data,
        "righe_errore_data": righe_errore_data,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }

    return df, summary
