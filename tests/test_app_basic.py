from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz_ok() -> None:
    """La probe /healthz deve rispondere 200 e contenere uno status ok e un timestamp."""
    resp = client.get("/healthz")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok"
    assert "time" in data
    assert isinstance(data["time"], str)


def test_version_shape() -> None:
    """L'endpoint /version deve esporre metadati base dell'app."""
    resp = client.get("/version")
    assert resp.status_code == 200
    data = resp.json()

    # Valori chiave attesi
    assert data.get("app") == "TPI_evoluto"

    # Campi presenti, anche se vuoti in dev
    assert "version" in data
    assert "git_sha" in data
    assert "build_time" in data
