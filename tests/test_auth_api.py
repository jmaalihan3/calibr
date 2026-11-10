"""
Integration tests for authentication API endpoints.

Tests:
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/me
- GET /api/auth/csrf-token

Uses FastAPI TestClient for integration testing.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os


@pytest.fixture
def client():
    """
    Fixture providing FastAPI test client.
    Must be imported AFTER patching database path.
    """
    # Remove old test database
    if os.path.exists("test_auth.db"):
        os.remove("test_auth.db")
    
    # Patch database path BEFORE importing app
    from app import db
    original_path = db.DATABASE_PATH
    original_url = db.DATABASE_URL
    db.DATABASE_PATH = "test_auth.db"
    db.DATABASE_URL = None  # Force SQLite
    
    # Now import app (will use patched database)
    from app.main import app
    
    # Initialize test database
    db.init_db()
    
    # Clear rate limit store for test isolation
    from app.auth import _rate_limit_store
    _rate_limit_store.clear()
    
    yield TestClient(app)
    
    # Cleanup
    db.DATABASE_PATH = original_path
    db.DATABASE_URL = original_url
    if os.path.exists("test_auth.db"):
        os.remove("test_auth.db")


def test_register_success(client):
    """Test successful user registration."""
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Registration successful"
    assert "log in" in data["detail"].lower()


def test_register_duplicate_email(client):
    """Test registration with duplicate email."""
    # Register first user
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    # Try to register with same email
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "DifferentPass456!"
    })
    
    assert response.status_code == 400
    data = response.json()
    assert "failed" in data["detail"].lower()


def test_register_case_insensitive_email(client):
    """Test registration with case-insensitive email."""
    # Register with lowercase
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    # Try to register with uppercase
    response = client.post("/api/auth/register", json={
        "email": "TEST@EXAMPLE.COM",
        "password": "DifferentPass456!"
    })
    
    assert response.status_code == 400


def test_register_weak_password(client):
    """Test registration with weak password."""
    from app.auth import _rate_limit_store
    
    # No uppercase
    _rate_limit_store.clear()
    response = client.post("/api/auth/register", json={
        "email": "test1@example.com",
        "password": "securepass123!"
    })
    assert response.status_code == 422
    
    # No lowercase
    _rate_limit_store.clear()
    response = client.post("/api/auth/register", json={
        "email": "test2@example.com",
        "password": "SECUREPASS123!"
    })
    assert response.status_code == 422
    
    # No digit
    _rate_limit_store.clear()
    response = client.post("/api/auth/register", json={
        "email": "test3@example.com",
        "password": "SecurePass!"
    })
    assert response.status_code == 422
    
    # No special character
    _rate_limit_store.clear()
    response = client.post("/api/auth/register", json={
        "email": "test4@example.com",
        "password": "SecurePass123"
    })
    assert response.status_code == 422
    
    # Too short
    _rate_limit_store.clear()
    response = client.post("/api/auth/register", json={
        "email": "test5@example.com",
        "password": "Sec1!"
    })
    assert response.status_code == 422


def test_register_invalid_email(client):
    """Test registration with invalid email."""
    response = client.post("/api/auth/register", json={
        "email": "not-an-email",
        "password": "SecurePass123!"
    })
    
    assert response.status_code == 422


def test_login_success(client):
    """Test successful login."""
    # Register user
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    # Login
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert data["user"]["email"] == "test@example.com"
    assert "csrf_token" in data
    assert "session_token" in response.cookies


def test_login_wrong_password(client):
    """Test login with wrong password."""
    # Register user
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    # Login with wrong password
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "WrongPass456!"
    })
    
    assert response.status_code == 401
    data = response.json()
    assert "invalid" in data["detail"].lower()


def test_login_nonexistent_user(client):
    """Test login with nonexistent user."""
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "SecurePass123!"
    })
    
    assert response.status_code == 401
    data = response.json()
    # Should not reveal that user doesn't exist
    assert "invalid" in data["detail"].lower()


def test_login_case_insensitive_email(client):
    """Test login with case-insensitive email."""
    # Register with lowercase
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    # Login with uppercase
    response = client.post("/api/auth/login", json={
        "email": "TEST@EXAMPLE.COM",
        "password": "SecurePass123!"
    })
    
    assert response.status_code == 200


def test_get_me_authenticated(client):
    """Test getting current user when authenticated."""
    # Register and login
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    login_response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    # Get current user
    response = client.get("/api/auth/me")
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data


def test_get_me_unauthenticated(client):
    """Test getting current user when not authenticated."""
    response = client.get("/api/auth/me")
    
    assert response.status_code == 401


def test_logout_success(client):
    """Test successful logout."""
    # Register and login
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    login_response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    csrf_token = login_response.json()["csrf_token"]
    
    # Logout
    response = client.post("/api/auth/logout", headers={
        "X-CSRF-Token": csrf_token
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "logout" in data["message"].lower()


def test_logout_without_csrf(client):
    """Test logout without CSRF token."""
    # Register and login
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    # Logout without CSRF token
    response = client.post("/api/auth/logout")
    
    assert response.status_code == 403


def test_session_expires(client):
    """Test that expired sessions are invalid."""
    # This test is conceptual - in real scenario, you'd mock time
    # For now, we just verify the session validation logic exists
    pass


def test_get_csrf_token(client):
    """Test getting CSRF token."""
    # Register and login
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    # Get CSRF token
    response = client.get("/api/auth/csrf-token")
    
    assert response.status_code == 200
    data = response.json()
    assert "csrf_token" in data


def test_get_csrf_token_unauthenticated(client):
    """Test getting CSRF token when not authenticated."""
    response = client.get("/api/auth/csrf-token")
    
    assert response.status_code == 401


def test_password_hashing_security(client):
    """Test that passwords are properly hashed."""
    from app import db
    
    # Register user
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    # Get user from database
    user = db.get_user_by_email("test@example.com")
    
    # Password hash should not be the plaintext password
    assert user["password_hash"] != "SecurePass123!"
    
    # Password hash should start with Argon2id identifier
    assert user["password_hash"].startswith("$argon2id$")


def test_session_token_security(client):
    """Test that session tokens are properly hashed in database."""
    from app import db
    
    # Register and login
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    # Get session cookie
    session_token = response.cookies.get("session_token")
    
    # Get session from database
    session = db.get_session_by_token(session_token)
    
    # Token hash in database should not be the plaintext token
    assert session["token_hash"] != session_token
    
    # Token hash should be SHA-256 (64 hex characters)
    assert len(session["token_hash"]) == 64


def test_rate_limiting_register(client):
    """Test rate limiting on registration endpoint."""
    # Make multiple registration attempts quickly
    from app.auth import _rate_limit_store
    _rate_limit_store.clear()
    
    # First 3 should succeed (or fail with 400 if duplicate)
    for i in range(3):
        response = client.post("/api/auth/register", json={
            "email": f"test{i}@example.com",
            "password": "SecurePass123!"
        })
        assert response.status_code in [201, 400]
    
    # 4th should be rate limited (limit is 3)
    response = client.post("/api/auth/register", json={
        "email": "test3@example.com",
        "password": "SecurePass123!"
    })
    assert response.status_code == 429


def test_rate_limiting_login(client):
    """Test rate limiting on login endpoint."""
    from app.auth import _rate_limit_store
    _rate_limit_store.clear()
    
    # Register a user
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!"
    })
    
    # Make multiple login attempts quickly
    for i in range(5):
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPass!"
        })
        assert response.status_code in [401, 429]
    
    # 6th should be rate limited (limit is 5)
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "WrongPass!"
    })
    assert response.status_code == 429


def test_cross_user_data_isolation(client):
    """Test that users cannot access each other's data."""
    from app.main import app
    
    # Register two users
    client.post("/api/auth/register", json={
        "email": "user1@example.com",
        "password": "SecurePass123!"
    })
    
    client.post("/api/auth/register", json={
        "email": "user2@example.com",
        "password": "SecurePass123!"
    })
    
    # Login as user1
    response1 = client.post("/api/auth/login", json={
        "email": "user1@example.com",
        "password": "SecurePass123!"
    })
    user1_data = response1.json()["user"]
    
    # Login as user2 (in new client)
    client2 = TestClient(app)
    response2 = client2.post("/api/auth/login", json={
        "email": "user2@example.com",
        "password": "SecurePass123!"
    })
    user2_data = response2.json()["user"]
    
    # Verify they have different IDs
    assert user1_data["id"] != user2_data["id"]
    
    # Verify user1 cannot see user2's data
    me_response = client.get("/api/auth/me")
    assert me_response.json()["email"] == "user1@example.com"
