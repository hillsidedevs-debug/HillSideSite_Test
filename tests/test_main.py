import pytest
from unittest.mock import patch
from flask import url_for
from HillSide.extensions import mail


# -----------------------------
# INDEX ROUTE
# -----------------------------
def test_index_get(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"we build" in response.data.lower()


# -----------------------------
# STATIC TEMPLATE ROUTES
# -----------------------------

def test_about_route(client):
    response = client.get("/about")
    assert response.status_code == 200
    assert b"about" in response.data.lower()


def test_services_route(client):
    response = client.get("/services")
    assert response.status_code == 200
    assert b"service" in response.data.lower()


# -----------------------------
# CONTACT ROUTE
# -----------------------------
def test_contact_get(client):
    """Ensure GET /contact loads the form."""
    response = client.get("/contact")
    assert response.status_code == 200
    assert b"name" in response.data.lower()
    assert b"email" in response.data.lower()
    assert b"message" in response.data.lower()


@patch("HillSide.extensions.mail.send")
def test_contact_valid_submission(mock_send, client):
    """Valid contact form should send email and flash success."""
    response = client.post("/contact", data={
        "name": "Alice",
        "email": "alice@example.com",
        "message": "Hello, this is a test!"
    }, follow_redirects=True)

    # Should redirect back with success message
    assert response.status_code == 200
    assert b"success" in response.data.lower()
    mock_send.assert_called_once()


@patch("HillSide.extensions.mail.send")
def test_contact_invalid_form(mock_send, client):
    """Missing required fields should prevent email from sending."""
    response = client.post("/contact", data={
        "name": "",
        "email": "not-an-email",
        "message": ""
    }, follow_redirects=True)

    # Should remain on page with validation messages
    assert response.status_code == 200
    assert b"invalid" in response.data.lower()

    # Email should NOT be sent
    mock_send.assert_not_called()


@patch("HillSide.extensions.mail.send", side_effect=Exception("SMTP Failure"))
def test_contact_email_fails(mock_send, client):
    """If email fails, app should show error flash and stay stable."""
    response = client.post("/contact", data={
        "name": "Bob",
        "email": "bob@example.com",
        "message": "This should fail."
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"something went wrong" in response.data.lower()
    mock_send.assert_called_once()
