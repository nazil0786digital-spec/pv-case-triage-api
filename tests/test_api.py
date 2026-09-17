from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_request_id() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    UUID(response.headers["X-Request-ID"])


def test_valid_caller_request_id_is_propagated() -> None:
    request_id = "8f2d6fb8-f73f-4b9c-a5c8-68d442da93b4"

    response = client.get("/health", headers={"X-Request-ID": request_id})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id


def test_invalid_caller_request_id_is_replaced() -> None:
    response = client.get("/health", headers={"X-Request-ID": "not-a-valid-uuid"})

    assert response.status_code == 200
    generated_id = response.headers["X-Request-ID"]
    UUID(generated_id)
    assert generated_id != "not-a-valid-uuid"
