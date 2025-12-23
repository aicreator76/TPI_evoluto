from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_formazione_in_openapi():
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json().get("paths", {})
    assert "/api/formazione/overview" in paths
    assert "/api/formazione/products" in paths


def test_formazione_endpoints():
    r = client.get("/api/formazione/overview")
    assert r.status_code == 200
    j = r.json()
    assert "items" in j

    r = client.get("/api/formazione/products?limit=5&offset=0")
    assert r.status_code == 200
    j = r.json()
    assert "items" in j and "count" in j
