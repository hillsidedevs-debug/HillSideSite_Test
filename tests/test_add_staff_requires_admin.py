def test_add_staff_requires_admin(client):
    response = client.get("/add-staff", follow_redirects=True)
    assert b"Login" in response.data
