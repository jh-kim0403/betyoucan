import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.helpers import db
from src.models import auth_models
from datetime import datetime, timezone

client = TestClient(app)
"""
def test_manual_signup():
    signup_data = {
        "email": "kjh9643@gmail.com",
        "password": "temporary",
        "first_name": "jae",
        "last_name": "kim"
    }

    response = client.post("/api/v1/auth/manual/signup", json=signup_data)
    assert response.status_code == 200

    # Parse into your Pydantic model
    user_out = user_models.SignUpResponse(**response.json())

    assert user_out.email == signup_data["email"]
    assert user_out.first_name == signup_data["first_name"]
    assert user_out.last_name == signup_data["last_name"]
"""
def test_manual_signup_existing_email():
    signup_data = {
        "email": "kjh9643@gmail.com",
        "password": "temporary",
        "first_name": "jae",
        "last_name": "kim"
    }
    dup = client.post("/api/v1/auth/manual/signup", json=signup_data)
    assert dup.status_code == 400

def test_login():
    # 1. LOGIN to get an access token
    login_response = client.post(
        "/api/v1/auth/manual/login",
        json={"email": "kjh9643@gmail.com", "password": "temporary"}
    )
    assert login_response.status_code == 200

def test_refresh():
    payload = {
        "user_id": str("a5113ff2-5ab4-496c-b841-0479dee393b5"),
        "refresh_token": "Read the Bible"
    }

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json=payload
    )
    assert refresh_response.status_code == 200

def test_goal_types():

       # 1. LOGIN to get an access token
    login_response = client.post(
        "/api/v1/auth/manual/login",
        json={"email": "kjh9643@gmail.com", "password": "temporary"}
    )
    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]
    print(access_token)
    # 2. CALL PROTECTED ENDPOINT with Authorization header
    response = client.get(
        "/api/v1/goals/goaltypes",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    print("STATUS:", response.status_code)
    print("RESPONSE JSON:", response.json())

    assert response.status_code == 200

def test_make_goal():
    payload = {
        "goal_type_id": str("a5113ff2-5ab4-496c-b841-0479dee393b5"),
        "title": "Read the Bible",
        "description": "Read a passage",
        "user_input": "Genesis 1",
        "bounty_amount": 100,
        "deadline": datetime.now(timezone.utc).isoformat()
    }

    login_response = client.post(
        "/api/v1/auth/manual/login",
        json={"email": "kjh9643@gmail.com", "password": "temporary"}
    )
    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]
    # 2. CALL PROTECTED ENDPOINT with Authorization header
    response = client.post(
        "/api/v1/goals/newgoal", json=payload,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
