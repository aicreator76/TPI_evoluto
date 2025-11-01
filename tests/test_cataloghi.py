from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_template_ok():
    r = client.get("/v1/cataloghi/csv/template")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/vnd.openxmlformats")


def test_import_oversize_413():
    r = client.post(
        "/v1/cataloghi/csv/import",
        files={"file": ("x.csv", b"x" * (5 * 1024 * 1024 + 1), "text/csv")},
    )
    assert r.status_code == 413


def test_import_header_mancante_400():
    csv_data = "codice;descrizione\nA1;prova"  # delimitatore sbagliato + header incompleto -> 400
    r = client.post(
        "/v1/cataloghi/csv/import",
        files={"file": ("bad.csv", csv_data.encode(), "text/csv")},
    )
    assert r.status_code == 400
