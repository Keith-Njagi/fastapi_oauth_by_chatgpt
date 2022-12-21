import pytest
from fastapi.testclient import TestClient
from tortoise.contrib.fastapi import register_tortoise

from main import app
from models import User

client = TestClient(app)

@pytest.fixture(autouse=True)
async def setup():
    # Set up the database and register the models with Tortoise
    await register_tortoise(
        app,
        db_url="sqlite://:memory:",
        modules={"models": ["app.models"]},
        generate_schemas=True,
    )
    yield
    # Tear down the database
    await User.drop_table()

def test_register():
    data = {"username": "testuser", "full_name": "Test User", "email": "test@example.com", "phone": "1234567890", "password": "password"}
    response = client.post("/api/v1/register", json=data)
    assert response.status_code == 201
    assert response.json() == {"id": 1, "username": "testuser", "full_name": "Test User", "email": "test@example.com", "phone": "1234567890", "password": "hashed_password", "is_active": True, "created_at": "2022-12-21T00:00:00+00:00", "updated_at": "2022-12-21T00:00:00+00:00"}

def test_login():
    # Register a user first
    data = {"username": "testuser", "full_name": "Test User", "email": "test@example.com", "phone": "1234567890", "password": "password"}
    client.post("/api/v1/register", json=data)
    # Login with the correct credentials
    data = {"username": "testuser", "password": "password"}
    response = client.post("/api/v1/login", json=data)
    assert response.status_code == 200
    assert response.json() == {"access_token": "access_token", "token_type": "bearer"}
    # Login with incorrect password
    data = {"username": "testuser", "password": "incorrect"}
    response = client.post("/api/v1/login", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect username or password"}
    # Login with non-existent username
    data = {"username": "nonexistent", "password": "password"}
    response = client.post("/api/v1/login", json=data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect username or password"}

def test_password_reset():
    # Register a user first
    data = {"username": "testuser", "full_name": "Test User", "email": "test@example.com", "phone": "1234567890", "password": "password"}
    client.post("/api/v1/register", json=data)
    # Request password reset for a registered email
    data = {"email": "test@example.com"}
    response = client.post("/api/v1/password/reset", json=data)
    assert response.status_code == 200
    assert response.json() == {"message": "Password reset email sent"}
    # Request password reset for a non-registered email
    data = {"email": "nonexistent@example.com"}
    response = client.post("/api/v1/password/reset", json=data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Email not found"}

def test_password_reset_confirm():
    # Confirm password reset with a valid token
    response = client.get("/api/v1/password/reset/valid_token")
    assert response.status_code == 302
    assert response.headers["location"] == "/reset_password.html"
    # Confirm password reset with an invalid token
    response = client.get("/api/v1/password/reset/invalid_token")
    assert response.status_code == 404
    assert response.json() == {"detail": "Invalid token"}

def test_password_reset_complete():
    # Complete password reset with a valid token
    data = {"username": "testuser", "full_name": "Test User", "email": "test@example.com", "phone": "1234567890", "password": "newpassword"}
    response = client.post("/api/v1/password/reset/valid_token", json=data)
    assert response.status_code == 200
    assert response.json() == {"message": "Password reset successfully"}
    # Complete password reset with an invalid token
    data = {"username": "testuser", "full_name": "Test User", "email": "test@example.com", "phone": "1234567890", "password": "newpassword"}

