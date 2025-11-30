import os
import json
from datetime import datetime
import pandas as pd


def write_run_log(log_dir: str, summary: dict):
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "agente0.log")

    line = (
        f"{summary['timestamp']} | "
        f"TOT:{summary.get('totale', summary.get('totale_dpi', 0))} "
        f"OK:{summary.get('ok', 0)} "
        f"WARN:{summary.get('warning', 0)} "
        f"SCAD:{summary.get('scaduti', 0)} "
        f"ERR:{summary.get('errore_data', 0)} "
        f"ANOMALI:{summary.get('anomali', 0)} "
        f"RIGHE_ERR:{summary.get('righe_errore_data', 0)}"
        "\n"
    )

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)


def write_dashboard(dashboard_file: str, df: pd.DataFrame, summary: dict):
    """
    Scrive:
    - agente0_dashboard.json  -> conteggio + prime righe
    - agente0_cruscotto.json  -> solo conteggio
    """

    os.makedirs(os.path.dirname(dashboard_file), exist_ok=True)

    conteggio = {
        "totale_dpi": int(summary.get("totale_dpi", summary.get("totale", 0))),
        "ok": int(summary.get("ok", 0)),
        "warning": int(summary.get("warning", 0)),
        "scaduti": int(summary.get("scaduti", 0)),
        "anomali": int(summary.get("anomali", 0)),
        "righe_errore_data": int(
            summary.get("righe_errore_data", summary.get("errore_data", 0))
        ),
    }

    df_safe = df.copy().astype(str)
    now_iso = datetime.now().isoformat(timespec="seconds")

    data_dashboard = {
        "conteggio": conteggio,
        "rows": df_safe.head(100).to_dict(orient="records"),
        "updated_at": now_iso,
    }

    with open(dashboard_file, "w", encoding="utf-8") as f:
        json.dump(data_dashboard, f, ensure_ascii=False, indent=2)

    cruscotto_file = os.path.join(
        os.path.dirname(dashboard_file),
        "agente0_cruscotto.json",
    )

    data_cruscotto = {
        "conteggio": conteggio,
        "updated_at": now_iso,
    }

    with open(cruscotto_file, "w", encoding="utf-8") as f:
        json.dump(data_cruscotto, f, ensure_ascii=False, indent=2)
