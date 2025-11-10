def test_contact_form_submission(client, monkeypatch):
    """Test submitting the contact form"""

    class MockMail:
        def send(self, msg):
            print("Mock send called")

    from HillSide.extensions import mail
    monkeypatch.setattr(mail, 'send', MockMail().send)

    response = client.post('/contact', data={
        'name': 'John Doe',
        'email': 'john@example.com',
        'message': 'Hello from test!'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Your message has been sent successfully' in response.data
