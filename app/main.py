from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI

from app.routers import demo_real, inox, linee_vita


def create_app() -> FastAPI:
    app = FastAPI(title="TPI_evoluto", version="0.1.0")

    @app.get("/healthz", tags=["system"])
    def healthz() -> dict:
        return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

    # demo + 2 cataloghi
    demo_real.mount(app)
    linee_vita.mount(app)
    inox.mount(app)

    return app


app = create_app()
