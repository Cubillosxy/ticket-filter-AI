from fastapi.testclient import TestClient

from app.main import app


def test_simulate_ai_failure_triggers_fallback():
    client = TestClient(app)
    payload = {
        "id": "t_1",
        "subject": "Something odd",
        "description": "Not sure what is happening but it fails sometimes",
        "created_at": "2025-12-29T10:00:00Z",
    }
    r = client.post("/v1/tickets/classify?simulate_ai_failure=true", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "metadata" in data
    assert data["metadata"]["fallback_used"] is True
