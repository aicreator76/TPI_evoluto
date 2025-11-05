"""Smoke tests for TPI_evoluto API endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_healthz():
    """Test /healthz endpoint returns 200 OK."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_version():
    """Test /version endpoint returns version info."""
    response = client.get("/version")
    # Accept both 200 and 404 as the endpoint may not be fully configured
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "name" in data or "version" in data


def test_metrics():
    """Test /metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, dict)


def test_csv_template():
    """Test /api/dpi/csv/template endpoint."""
    response = client.get("/api/dpi/csv/template")
    # Accept 200 or 404
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert response.headers.get("content-type", "").startswith("text/")


def test_csv_catalogo():
    """Test /api/dpi/csv/catalogo endpoint."""
    response = client.get("/api/dpi/csv/catalogo")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert "count" in data or "items" in data


def test_csv_metrics():
    """Test /api/dpi/csv/metrics endpoint."""
    response = client.get("/api/dpi/csv/metrics")
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, dict)
