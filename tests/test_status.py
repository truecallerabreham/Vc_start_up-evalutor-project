from fastapi.testclient import TestClient

from app.api.main import app


client = TestClient(app)


def test_status() -> None:
    response = client.get("/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


def test_ui() -> None:
    response = client.get("/ui")
    assert response.status_code == 200
    assert "VentureLens AI" in response.text
