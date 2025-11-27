# tests/test_auth.py
import pytest
from HillSide.models import User, RoleEnum
from HillSide.extensions import bcrypt, db


def test_registration(client, app):
    response = client.post("/register", data={
        "first_name": "Alice",
        "last_name": "Smith",
        "username": "alice123",
        "email": "alice@example.com",
        "password": "securepassword",
        "confirm_password": "securepassword",
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"success" in response.data.lower() or b"welcome" in response.data.lower()

    with app.app_context():
        user = User.query.filter_by(username="alice123").first()
        assert user is not None
        assert user.email == "alice@example.com"
        assert bcrypt.check_password_hash(user.password, "securepassword")

def test_registration_unique_constraints(client, app):
    """Ensure duplicate username/email triggers IntegrityError handling."""

    # 1. First successful registration
    response = client.post("/register", data={
        "first_name": "John",
        "last_name": "Doe",
        "username": "john123",
        "email": "john@example.com",
        "password": "password123",
        "confirm_password": "password123",
    }, follow_redirects=True)

    assert response.status_code == 200

    # 2. Attempt duplicate username
    response = client.post("/register", data={
        "first_name": "Jane",
        "last_name": "Smith",
        "username": "john123",              # <-- duplicate
        "email": "jane@example.com",
        "password": "password123",
        "confirm_password": "password123",
    }, follow_redirects=True)

    # Check for flash message
    assert b"username" in response.data.lower()
    assert b"exists" in response.data.lower()

    # 3. Attempt duplicate email
    response = client.post("/register", data={
        "first_name": "Jane",
        "last_name": "Smith",
        "username": "jane123",
        "email": "john@example.com",        # <-- duplicate
        "password": "password123",
        "confirm_password": "password123",
    }, follow_redirects=True)

    # Check for flash message
    assert b"email" in response.data.lower()
    assert b"exists" in response.data.lower()

    # 4. Ensure database still contains only ONE user
    with app.app_context():
        users = User.query.filter_by(email="john@example.com").all()
        assert len(users) == 1


def test_login_logout(regular_user, client):
    # Should have access to protected page
    response = client.get("/dashboard", follow_redirects=True)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert any(name in html for name in ["Charlie", "Brown", "charlie", "Dashboard"])

    # Logout
    client.get("/logout", follow_redirects=True)

    # Should be redirected to login
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.location
