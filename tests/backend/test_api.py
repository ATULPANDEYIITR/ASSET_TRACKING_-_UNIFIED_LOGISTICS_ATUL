from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["application"] == "ATUL"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_system():
    response = client.get("/api/v1/system")

    assert response.status_code == 200
    assert response.json()["database"] == "PostgreSQL"


def test_database_health():
    response = client.get("/api/v1/health/database")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_assets_endpoint():
    response = client.get("/api/v1/assets")

    assert response.status_code == 200
    assert "total" in response.json()
    assert "items" in response.json()
