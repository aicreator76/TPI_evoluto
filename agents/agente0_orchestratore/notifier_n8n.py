"""
notifier_n8n.py – BLOCCO B (POWER, compatibile con invia_notifiche)

- Legge config.yaml
- Legge agente0_dashboard.json
- Costruisce agente0_feed_notifiche.json con soli DPI WARNING/SCADUTO
- Se notifiche.enabled == true e DPI_allarme >= min_dpi_allarme,
  invia il feed al webhook n8n con timeout configurabile.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import yaml

log = logging.getLogger(__name__)
ROOT_FALLBACK = Path(r"E:\CLONAZIONE\tpi_evoluto")


@dataclass(frozen=True)
class NotificheCfg:
    enabled: bool
    url: str
    timeout_sec: int
    min_dpi_allarme: int


def get_repo_root() -> Path:
    """Ritorna la root repo (fallback se path “strano”)."""
    here = Path(__file__).resolve()
    try:
        candidate = here.parents[2]
        return candidate if candidate.exists() else ROOT_FALLBACK
    except Exception as exc:  # noqa: BLE001
        log.debug("get_repo_root fallback: %s", exc)
        return ROOT_FALLBACK


def load_config(repo_root: Path) -> dict[str, Any]:
    cfg_path = repo_root / "config.yaml"
    if not cfg_path.exists():
        log.warning("[NOTIFIER] config.yaml non trovato: %s", cfg_path)
        return {}
    try:
        return yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001
        log.exception("[NOTIFIER] ERRORE lettura config.yaml: %s", exc)
        return {}


def get_paths(repo_root: Path, cfg: dict[str, Any]) -> dict[str, Path]:
    percorsi = cfg.get("percorsi", {}) or {}
    agente0_cfg = cfg.get("agente0", {}) or {}

    root = Path(percorsi.get("root", repo_root))
    logs_dir = Path(percorsi.get("logs_dir", root / "logs"))

    dashboard_default = root / (cfg.get("dashboard_file") or "logs/agente0_dashboard.json")
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
    try:
        return json.loads(dashboard_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"ERRORE parsing JSON dashboard: {exc}") from exc


def build_feed_from_dashboard(dashboard: dict[str, Any], out_path: Path) -> dict[str, Any]:
    conteggio: dict[str, Any] = dashboard.get("conteggio", {}) or {}
    rows = dashboard.get("rows", []) or []

    dpi_warning: list[dict[str, Any]] = []
    dpi_scaduti: list[dict[str, Any]] = []

    for r in rows:
        stato = str(r.get("stato_scadenza", "")).upper()
        if stato == "WARNING":
            dpi_warning.append(r)
        elif stato == "SCADUTO":
            dpi_scaduti.append(r)

    derived_tot = len(rows)
    derived_warn = len(dpi_warning)
    derived_scad = len(dpi_scaduti)

    merged_conteggio: dict[str, Any] = {
        "totale_dpi": conteggio.get("totale_dpi", derived_tot) or derived_tot,
        "warning": conteggio.get("warning", derived_warn) or derived_warn,
        "scaduti": conteggio.get("scaduti", derived_scad) or derived_scad,
    }

    tot_alert = int(merged_conteggio["warning"]) + int(merged_conteggio["scaduti"])

    feed: dict[str, Any] = {
        "conteggio": merged_conteggio,
        "totale_dpi_allarme": tot_alert,
        "dpi_warning": dpi_warning,
        "dpi_scaduti": dpi_scaduti,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "meta": {"fonte": "agente0_dashboard.json", "note": "Solo WARNING/SCADUTO per notifiche"},
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(feed, ensure_ascii=False, indent=2), encoding="utf-8")

    log.info("[NOTIFIER] Feed scritto: %s", out_path)
    log.info(
        "[NOTIFIER] DPI allarme: WARNING=%s SCADUTI=%s TOT=%s",
        merged_conteggio["warning"],
        merged_conteggio["scaduti"],
        tot_alert,
    )
    return feed


def get_notifiche_cfg(cfg: dict[str, Any]) -> NotificheCfg:
    blocco = cfg.get("notifiche", {}) or {}
    enabled = bool(blocco.get("enabled", False))
    url = (blocco.get("n8n_webhook_url") or "").strip()

    try:
        timeout_sec = int(blocco.get("timeout_sec", 10))
    except Exception:  # noqa: BLE001
        timeout_sec = 10
    timeout_sec = timeout_sec if timeout_sec > 0 else 10

    try:
        min_dpi_allarme = int(blocco.get("min_dpi_allarme", 1))
    except Exception:  # noqa: BLE001
        min_dpi_allarme = 1
    min_dpi_allarme = min_dpi_allarme if min_dpi_allarme >= 1 else 1

    return NotificheCfg(
        enabled=enabled, url=url, timeout_sec=timeout_sec, min_dpi_allarme=min_dpi_allarme
    )


def send_to_n8n(feed: dict[str, Any], notif: NotificheCfg) -> None:
    if not notif.enabled:
        log.info("[NOTIFIER] Notifiche DISABILITATE → nessun invio.")
        return
    if not notif.url or "TUO-N8N-HOST" in notif.url:
        log.warning("[NOTIFIER] URL n8n non configurato/placeholder → nessun invio.")
        return

    tot_alert = int(feed.get("totale_dpi_allarme", 0))
    if tot_alert < notif.min_dpi_allarme:
        log.info(
            "[NOTIFIER] DPI allarme=%s (< soglia %s) → nessuna chiamata n8n.",
            tot_alert,
            notif.min_dpi_allarme,
        )
        return

    try:
        resp = requests.post(notif.url, json=feed, timeout=notif.timeout_sec)
        resp.raise_for_status()
        log.info("[NOTIFIER] n8n OK: HTTP %s", resp.status_code)
    except Exception as exc:  # noqa: BLE001
        log.exception("[NOTIFIER] ERRORE invio n8n: %s", exc)


def main() -> None:
    try:
        repo_root = get_repo_root()
        cfg = load_config(repo_root)
        if not cfg:
            log.warning("[NOTIFIER] Config vuota/non trovata. Esco.")
            return

        paths = get_paths(repo_root, cfg)
        dashboard = load_dashboard(paths["dashboard_json"])
        feed = build_feed_from_dashboard(dashboard, paths["feed_notifiche_json"])

        notif_cfg = get_notifiche_cfg(cfg)
        send_to_n8n(feed, notif_cfg)
        log.info("[NOTIFIER] BLOCCO B completato.")
    except Exception as exc:  # noqa: BLE001
        log.exception("[NOTIFIER] ERRORE BLOCCO B: %s", exc)


def invia_notifiche() -> None:
    main()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    main()
