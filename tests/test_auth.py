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
        "password_confirm": "securepassword",
    }, follow_redirects=True)
    print("user added")

    # assert response.status_code == 200
    # assert b"success" in response.data.lower() or b"welcome" in response.data.lower()

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
        "password_confirm": "password123",
    }, follow_redirects=True)

    assert response.status_code == 200

    # 2. Attempt duplicate username
    response = client.post("/register", data={
        "first_name": "Jane",
        "last_name": "Smith",
        "username": "john123",              # <-- duplicate
        "email": "jane@example.com",
        "password": "password123",
        "password_confirm": "password123",
    }, follow_redirects=True)

    # Check for flash message
    assert b"username" in response.data.lower()
    # assert b"exists" in response.data.lower()

    # 3. Attempt duplicate email
    response = client.post("/register", data={
        "first_name": "Jane",
        "last_name": "Smith",
        "username": "jane123",
        "email": "john@example.com",        # <-- duplicate
        "password": "password123",
        "password_confirm": "password123",
    }, follow_redirects=True)

    # Check for flash message
    assert b"email" in response.data.lower()
    # assert b"exists" in response.data.lower()

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


def test_forgot_password_post(client, mocker):
    # Create a valid user
    user = User(
        first_name="Test",
        last_name="User",
        username="testuser",
        email="test@example.com",
        password="hashed-password"  # can be fake, not used here
    )
    db.session.add(user)
    db.session.commit()

    # Mock send email
    mock_send = mocker.patch("HillSide.utils.send_reset_email")

    response = client.post(
        "/forgot_password",
        data={"email": "test@example.com"},
        follow_redirects=True
    )

    # mock_send.assert_called_once_with(user)
    assert b"If this email exists, a reset link has been sent." in response.data
    assert response.status_code == 200



def test_forgot_password_no_user(client, app, mocker):
    with app.app_context():
        # Ensure no user with this email exists (clean slate)
        User.query.filter_by(email="nosuch@example.com").delete()
        db.session.commit()

    # Mock the email function — we already know the correct path from the previous test
    mock_send = mocker.patch("HillSide.utils.send_reset_email")

    response = client.post(
        "/forgot_password",
        data={"email": "nosuch@example.com"},
        follow_redirects=True
    )

    # The function should NOT have been called
    mock_send.assert_not_called()

    # User should see the generic safe message (same as when user exists)
    assert b"If this email exists, a reset link has been sent." in response.data

    # Usually a 200 on success (or 302 if redirecting, but with follow_redirects=True it's 200)
    assert response.status_code == 200
def test_reset_password_valid_token(client, app, mocker):
    with app.app_context():
        # Create a real user with a hashed password
        user = User(
            first_name="Reset",
            last_name="Test",
            username="resettester",
            email="reset@example.com",
            password=bcrypt.generate_password_hash("oldpassword").decode('utf-8')
        )
        db.session.add(user)
        db.session.commit()

        # Store old password hash for later comparison
        old_password_hash = user.password

        # Mock the class method User.verify_reset_token (static or class method)
        # The correct path is almost certainly HillSide.models.User.verify_reset_token
        mock_verify = mocker.patch("HillSide.models.User.verify_reset_token")
        mock_verify.return_value = user  # When called with token, return the user

        # Submit the reset form
        response = client.post(
            "/reset_password/faketoken",  # your route likely uses <token> param
            data={
                "password": "newpass123",
                "confirm_password": "newpass123"  # assuming your form requires confirmation
            },
            follow_redirects=True
        )

        # Check success message (adjust if your exact message differs slightly)
        assert b"password has been updated" in response.data.lower()
        assert response.status_code == 200

        # Verify the password was actually changed in the DB
        assert user.password != old_password_hash
        assert bcrypt.check_password_hash(user.password, "newpass123")

        # Optional: ensure the mock was called exactly once with the token
        mock_verify.assert_called_once_with("faketoken")


def test_reset_password_invalid_token(client, mocker):
    mock_verify = mocker.patch("HillSide.models.User.verify_reset_token")
    mock_verify.return_value = None

    response = client.get("/reset_password/badtoken", follow_redirects=True)

    assert b"Invalid or expired token." in response.data


def test_verify_email_valid(client, mocker):
    user = User(email="verify@example.com", is_verified=False)
    db.session.add(user)
    db.session.commit()

    # Mock serializer output
    mock_serializer = mocker.patch("HillSide.utils.serializer.loads")
    mock_serializer.return_value = user.email

    response = client.get("/verify/validtoken", follow_redirects=True)

    assert b"Your email has been verified!" in response.data
    assert user.is_verified is True


# def test_verify_email_invalid(client, mocker):
#     mock_serializer = mocker.patch("yourapp.auth.routes.serializer.loads",
#                                    side_effect=Exception("Invalid token"))

#     response = client.get("/verify/badtoken", follow_redirects=True)

#     assert b"The verification link is invalid or expired." in response.data


# def test_resend_verification(client, db, mocker):
#     user = User(email="needverify@example.com", is_verified=False)
#     db.session.add(user)
#     db.session.commit()

#     mock_send = mocker.patch("yourapp.auth.routes.send_verification_email")

#     response = client.post("/resend-verification",
#                            data={"email": "needverify@example.com"},
#                            follow_redirects=True)

#     mock_send.assert_called_once_with(user)
#     assert b"A new verification email has been sent." in response.data


# def test_resend_verification_already_verified(client, db):
#     user = User(email="verified@example.com", is_verified=True)
#     db.session.add(user)
#     db.session.commit()

#     response = client.post("/resend-verification",
#                            data={"email": "verified@example.com"},
#                            follow_redirects=True)

#     assert b"Your account is already verified" in response.data


# def test_resend_verification_no_user(client):
#     response = client.post("/resend-verification",
#                            data={"email": "nosuch@example.com"},
#                            follow_redirects=True)

#     assert b"No account found with that email." in response.data
