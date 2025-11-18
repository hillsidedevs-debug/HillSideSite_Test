def test_admin_requires_login(client):
    response = client.get("/admin-dashboard", follow_redirects=True)
    assert b"Login" in response.data  # redirected to login
