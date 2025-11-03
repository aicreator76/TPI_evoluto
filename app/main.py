import importlib
import logging
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("tpi.app")

app = FastAPI()


def try_include_router():
    try:
        mod = importlib.import_module("app.dpi_csv")
        router = getattr(mod, "router", None)
        if router is None:
            log.warning("app.dpi_csv importato ma 'router' non trovato")
        else:
            app.include_router(router)
            log.info("Router CSV registrato: /api/dpi/csv/*")
    except Exception as e:
        log.exception("Impossibile importare app.dpi_csv: %s", e)


try_include_router()


@app.get("/health")
def health():
    return {"status": "ok"}
