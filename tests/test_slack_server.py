from fastapi.testclient import TestClient

from api.slack_server import app

client = TestClient(app)


def test_slack_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Slack server is running."}
