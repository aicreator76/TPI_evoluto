"""Genera docs/openapi.json a partire dalla FastAPI app."""

from pathlib import Path
import importlib
import json

CANDIDATE_MODULES = [
    "mini_app",  # esiste già nel repo TPI_evoluto
    "app.main",
    "app",
    "main",
]


def load_app():
    last_exc: Exception | None = None
    for name in CANDIDATE_MODULES:
        try:
            mod = importlib.import_module(name)
            app = getattr(mod, "app")
            return app
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            continue
    raise RuntimeError(
        f"FastAPI app not found. Tried: {CANDIDATE_MODULES}. Last error: {last_exc!r}"
    )


def main() -> None:
    app = load_app()
    schema = app.openapi()

    out_path = Path("docs") / "openapi.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[generate_openapi] wrote {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
