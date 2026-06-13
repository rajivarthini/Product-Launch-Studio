from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_full_workflow_missing_file():
    response = client.post("/api/full-workflow", data={})
    assert response.status_code == 422  # validation error for missing fields

