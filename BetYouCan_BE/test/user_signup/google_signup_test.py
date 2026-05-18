from fastapi.testclient import TestClient
from src.main import app
from ...src.helpers import db
from ...src.models import auth_schemas


client = TestClient(app)

def test_google_signup():
    response = client.post("/auth/google/signup", json={
        "id_token": "test_id_token"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()