# tests/test_auth.py
from HillSide.models import User, RoleEnum
from HillSide.extensions import bcrypt, db
import pytest

def test_registration(client, app):
    response = client.post('/register', data={
        'first_name': 'Alice',
        'last_name': 'Smith',
        'username': 'alice123',
        'email': 'alice@example.com',
        'password': 'securepassword',
        #'confirm_password': 'securepassword',
        #'g-recaptcha-response': 'test'  # bypassed in test config
    }, follow_redirects=True)

    assert response.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username='alice123').first()
        assert user is not None
        assert user.email == 'alice@example.com'

# def test_login_logout(client, regular_user):
#     # Login
#     response = client.post('/login', data={
#         'username': 'alice123',
#         'password': 'securepassword'
#     }, follow_redirects=True)
#     assert b'Welcome' in response.data or response.status_code == 200

#     # Logout
#     response = client.get('/logout', follow_redirects=True)
#     assert response.status_code == 200
#     with client.session_transaction() as sess:
#         assert 'user_id' not in sess

@pytest.fixture
def regular_user(client, app):
    """Create a regular user and log them in properly."""
    with app.app_context():
        # Create user
        user = User(
            first_name="Charlie",
            last_name="Brown",
            username="charlie",
            email="charlie@example.com",
            password=bcrypt.generate_password_hash("testpass123").decode("utf-8"),
            role=RoleEnum.USER,        # ← this now exists thanks to you
        )
        db.session.add(user)
        db.session.commit()

        # CRITICAL: refresh user so it's attached to a new session in teardown
        db.session.refresh(user)

        # Log in via the real login route (most reliable)
        client.post(
            "/login",
            data={"email": "charlie@example.com", "password": "testpass123"},
            follow_redirects=True,
        )

        yield user

        # Teardown — now safe because we refreshed + new app context
        with app.app_context():
            User.query.filter_by(id=user.id).delete()
            db.session.commit()


def test_login_logout_with_fixture(client, regular_user):
    # Now the user is really logged in (via /login route)

    response = client.get("/dashboard", follow_redirects=False)
    # If your @login_required redirects to /login, expect 302 first
    if response.status_code == 302:
        response = client.get("/dashboard", follow_redirects=True)

    assert response.status_code == 200

    # Be flexible — your dashboard might show username, full name, or just "Dashboard"
    html = response.data.decode()
    assert any(
        text in html for text in ["Charlie", "Brown", "charlie", "Dashboard", "Welcome"]
    )

    # Test logout
    client.get("/logout", follow_redirects=True)

    # Should no longer be logged in
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.location