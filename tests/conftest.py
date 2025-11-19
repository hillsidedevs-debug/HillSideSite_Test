# import pytest
# import sys, os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from run import app

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from HillSide import create_app
from HillSide.extensions import db

@pytest.fixture
def app():
    app = create_app()

    # Override config for testing
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,  # Disable CSRF for tests
    })

    if app.config.get("TESTING"):
        print("⚠️ Running in TEST MODE — using in-memory database")
    else:
        print("🚀 Running in NORMAL MODE")

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
