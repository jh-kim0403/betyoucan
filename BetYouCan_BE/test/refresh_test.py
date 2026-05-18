import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.helpers import db
from src.models import auth_models
from datetime import datetime, timezone

client = TestClient(app)

@pytest.fixture(scope="module")
def test_login():
    # 1. LOGIN to get an access token

    login_response = client.post(
        "/api/v1/auth/manual/login",
        json={"email": "kjh9643@gmail.com", "password": "temporary"}
    )
    assert login_response.status_code == 200
    refresh_token = login_response.json()
    return refresh_token["refresh_token"], refresh_token["user_id"]


def test_refresh(test_login):
    refresh_token, user_id = test_login
    print(refresh_token)
    print(user_id)
    payload = {
        "user_id": user_id,
        "refresh_token": refresh_token
    }

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json=payload
    )
    if refresh_response.status_code != 200:
        print(refresh_response.status_code)
        print(refresh_response.text)  

def test_openai():
    refresh_response = client.post(
        "/api/v1/openai/test"
    )

    print(refresh_response.status_code)
    print(refresh_response.text)  
    