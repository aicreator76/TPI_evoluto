from __future__ import annotations

import os
import subprocess
import logging
from fastapi import FastAPI
from app.dpi_csv import router as csv_router, compute_metrics as csv_compute_metrics

log = logging.getLogger("tpi.app")


def _git_short_sha() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return out or None
    except Exception:
        return None


app = FastAPI(title="TPI Evoluto", version=os.getenv("APP_VERSION", "0.1.0"))


@app.on_event("startup")
async def _on_startup():
    log.info("Router CSV registrato: /api/dpi/csv/*")


# CSV router
app.include_router(csv_router)


# Meta
@app.get("/healthz", tags=["meta"])
async def healthz():
    return {"status": "ok"}


@app.get("/version", tags=["meta"])
async def version():
    return {
        "name": "tpi_evoluto",
        "version": app.version,
        "git": _git_short_sha() or os.getenv("GIT_SHA", "unknown"),
    }


@app.get("/metrics", tags=["meta"])
async def metrics():
    return {"csv": csv_compute_metrics()}
