"""
notifier_n8n.py – BLOCCO B (versione POWER, compatibile con invia_notifiche)

- Legge config.yaml (percorsi + notifiche)
- Legge agente0_dashboard.json
- Costruisce agente0_feed_notifiche.json con soli DPI WARNING/SCADUTO
- Se notifiche.enabled == true e DPI_allarme >= min_dpi_allarme,
  invia il feed al webhook n8n con timeout configurabile.

Compatibilità:
- Espone la funzione invia_notifiche(), così agente0_main.py può
  continuare a fare: from notifier_n8n import invia_notifiche
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import yaml

# Fallback, nel caso non riuscissimo a risalire dal __file__
ROOT_FALLBACK = Path(r"E:\CLONAZIONE\tpi_evoluto")


def get_repo_root() -> Path:
    """
    Ritorna la root della repo:
    ...\tpi_evoluto\agents\agente0_orchestratore\notifier_n8n.py
    -> genitore di livello 2 = cartella progetto.
    """
    here = Path(__file__).resolve()
    try:
        candidate = here.parents[2]
        if candidate.exists():
            return candidate
    except Exception:  # noqa: BLE001
        pass
    return ROOT_FALLBACK


def load_config(repo_root: Path) -> dict[str, Any]:
    cfg_path = repo_root / "config.yaml"
    if not cfg_path.exists():
        print(f"[NOTIFIER] config.yaml non trovato: {cfg_path}")
        return {}

    try:
        raw = cfg_path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw) or {}
        return data
    except Exception as exc:  # noqa: BLE001
        print(f"[NOTIFIER] ERRORE lettura config.yaml: {exc}")
        return {}


def get_paths(repo_root: Path, cfg: dict[str, Any]) -> dict[str, Path]:
    """
    Deriva i percorsi da:
    - blocco 'percorsi' (root, logs_dir)
    - blocco 'agente0' (dashboard_json, feed_notifiche_json)
    - fallback su valori storici.
    """
    percorsi = cfg.get("percorsi", {}) or {}
    agente0_cfg = cfg.get("agente0", {}) or {}

    root = Path(percorsi.get("root", repo_root))
    logs_dir = Path(percorsi.get("logs_dir", root / "logs"))

    # dashboard: prima da agente0.dashboard_json, poi da dashboard_file
    dashboard_default = root / (
        cfg.get("dashboard_file") or "logs/agente0_dashboard.json"
    )
    dashboard_path = Path(agente0_cfg.get("dashboard_json", dashboard_default))

    feed_default = logs_dir / "agente0_feed_notifiche.json"
    feed_path = Path(agente0_cfg.get("feed_notifiche_json", feed_default))

    return {
        "root": root,
        "logs_dir": logs_dir,
        "dashboard_json": dashboard_path,
        "feed_notifiche_json": feed_path,
    }


def load_dashboard(dashboard_path: Path) -> dict[str, Any]:
    if not dashboard_path.exists():
        raise FileNotFoundError(f"Dashboard agente0 non trovata: {dashboard_path}")

    raw = dashboard_path.read_text(encoding="utf-8")
    data = json.loads(raw) or {}
    return data


def build_feed_from_dashboard(
    dashboard: dict[str, Any], out_path: Path
) -> dict[str, Any]:
    """
    Prende agente0_dashboard.json e costruisce un feed con:
    - dpi_warning: righe WARNING
    - dpi_scaduti: righe SCADUTO
    """
    conteggio = dashboard.get("conteggio", {}) or {}
    rows = dashboard.get("rows", []) or []

    dpi_warning: list[dict[str, Any]] = []
    dpi_scaduti: list[dict[str, Any]] = []

    for r in rows:
        stato = str(r.get("stato_scadenza", "")).upper()
        if stato == "WARNING":
            dpi_warning.append(r)
        elif stato == "SCADUTO":
            dpi_scaduti.append(r)

    tot_alert = len(dpi_warning) + len(dpi_scaduti)

    feed: dict[str, Any] = {
        "conteggio": conteggio,
        "totale_dpi_allarme": tot_alert,
        "dpi_warning": dpi_warning,
        "dpi_scaduti": dpi_scaduti,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "meta": {
            "fonte": "agente0_dashboard.json",
            "note": "Solo WARNING/SCADUTO estratti per notifiche",
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(feed, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"[NOTIFIER] Scritto feed notifiche: {out_path}")
    print(
        f"[NOTIFIER] DPI in allarme: WARNING={len(dpi_warning)}, "
        f"SCADUTI={len(dpi_scaduti)}, TOT={tot_alert}"
    )

    return feed


def get_notifiche_cfg(cfg: dict[str, Any]) -> dict[str, Any]:
    blocco = cfg.get("notifiche", {}) or {}

    enabled = bool(blocco.get("enabled", False))
    url = (blocco.get("n8n_webhook_url") or "").strip()
    timeout_sec = int(blocco.get("timeout_sec", 10))
    min_dpi_allarme = int(blocco.get("min_dpi_allarme", 1))

    return {
        "enabled": enabled,
        "url": url,
        "timeout_sec": timeout_sec,
        "min_dpi_allarme": min_dpi_allarme,
    }


def send_to_n8n(feed: dict[str, Any], notif_cfg: dict[str, Any]) -> None:
    enabled = notif_cfg["enabled"]
    url = notif_cfg["url"]
    timeout_sec = notif_cfg["timeout_sec"]
    min_dpi_allarme = notif_cfg["min_dpi_allarme"]

    if not enabled:
        print("[NOTIFIER] Notifiche DISABILITATE in config.yaml → nessun invio.")
        return

    if not url or "TUO-N8N-HOST" in url:
        print(
            "[NOTIFIER] URL webhook n8n non configurato o placeholder → nessun invio."
        )
        return

    tot_alert = int(feed.get("totale_dpi_allarme", 0))
    if tot_alert < min_dpi_allarme:
        print(
            f"[NOTIFIER] DPI in allarme = {tot_alert} (< soglia {min_dpi_allarme}) "
            "→ nessuna chiamata a n8n."
        )
        return

    try:
        print(
            f"[NOTIFIER] Invio feed a n8n: {url} "
            f"(DPI in allarme: {tot_alert}, timeout={timeout_sec}s)"
        )
        resp = requests.post(url, json=feed, timeout=timeout_sec)
        resp.raise_for_status()
        print(f"[NOTIFIER] Risposta n8n: HTTP {resp.status_code}")
    except Exception as exc:  # noqa: BLE001
        print(f"[NOTIFIER] ERRORE invio a n8n: {exc}")


def main() -> None:
    """
    Entry point sia per esecuzione diretta che per wrapper invia_notifiche().
    NON lancia eccezioni verso l'alto: logga e ritorna.
    """
    try:
        repo_root = get_repo_root()
        cfg = load_config(repo_root)
        if not cfg:
            print("[NOTIFIER] Config vuota o non trovata. Esco.")
            return

        paths = get_paths(repo_root, cfg)
        dashboard = load_dashboard(paths["dashboard_json"])
        feed = build_feed_from_dashboard(dashboard, paths["feed_notifiche_json"])

        notif_cfg = get_notifiche_cfg(cfg)
        send_to_n8n(feed, notif_cfg)

        print("[NOTIFIER] BLOCCO B completato.")
    except Exception as exc:  # noqa: BLE001
        print(f"[NOTIFIER] ERRORE BLOCCO B: {exc}")


def invia_notifiche() -> None:
    """
    Wrapper compatibile con la vecchia versione di Agente 0.
    agente0_main.py può continuare a fare:
        from notifier_n8n import invia_notifiche
        invia_notifiche()
    """
    main()


if __name__ == "__main__":
    main()
