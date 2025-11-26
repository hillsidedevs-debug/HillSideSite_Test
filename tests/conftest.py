# tests/conftest.py
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from HillSide import create_app
from HillSide.extensions import db, bcrypt
from HillSide.models import User, RoleEnum

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,           # Important for form posts
        "UPLOAD_FOLDER_PHOTOS": "/tmp/photos",
        "UPLOAD_FOLDER_RESUMES": "/tmp/resumes",
    })

    with app.app_context():
        db.create_all()

        # Create a default admin if none exists (your app might do this via script)
        if not User.query.filter_by(role=RoleEnum.ADMIN).first():
            admin = User(
                first_name="Admin",
                last_name="User",
                username="admin",
                email="admin@test.com",
                password=bcrypt.generate_password_hash("password").decode("utf-8"),  # "password"
                role=RoleEnum.ADMIN
            )
            db.session.add(admin)
            db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


# Helper: log in as any user
def login(client, email="admin@test.com", password="password"):
    return client.post("/login", data={
        "email": email,
        "password": password
    }, follow_redirects=True)


@pytest.fixture
def logged_in_admin(client):
    return login(client, "admin@test.com", "password")


@pytest.fixture
def logged_in_staff(client, app):
    with app.app_context():
        staff = User(
            first_name="Staff",
            last_name="One",
            username="staff1",
            email="staff@test.com",
            password="$2b$12$W8hJntk4oZh8Xz5e0k3Y8u9q1w2e3r4t5y6u7i8o9p0a1s2d3f4g5h",  # "password"
            role=RoleEnum.STAFF
        )
        db.session.add(staff)
        db.session.commit()
        login(client, "staff@test.com", "password")
        return staff