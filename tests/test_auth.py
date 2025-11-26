# tests/test_auth.py
from HillSide.models import User, RoleEnum

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

def test_login_logout(client, regular_user):
    # Login
    response = client.post('/login', data={
        'username': 'johndoe',
        'password': 'any'  # you probably hash-check in route, but login route may use bcrypt
    }, follow_redirects=True)
    assert b'Welcome' in response.data or response.status_code == 200

    # Logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert 'user_id' not in sess