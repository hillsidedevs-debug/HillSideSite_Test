# tests/conftest.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from HillSide import create_app
from HillSide.extensions import db, bcrypt
from HillSide.models import User, RoleEnum, Course



@pytest.fixture(scope="function")
def app(tmp_path):
    db_path = tmp_path / "test_db.sqlite"

    app_config = {
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "WTF_CSRF_ENABLED": False,
        "UPLOAD_FOLDER": "/tmp/uploads",
        "UPLOAD_PHOTO_FOLDER": "/tmp/uploads/photos",
        "UPLOAD_RESUME_FOLDER": "/tmp/uploads/resumes",
        "SESSION_COOKIE_SECURE": False,
        "REMEMBER_COOKIE_SECURE": False,
        "RATELIMIT_STORAGE_URI": "memory://",
    }

    app = create_app(app_config)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
        db.session.remove()
@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


# Helper to log in any user (useful and reliable)
def _login(client, email, password="password"):
    return client.post("/login", data={
        "email": email,
        "password": password,
        "remember": "y"
    }, follow_redirects=True)

@pytest.fixture
def sample_image(tmp_path):
    file_path = tmp_path / "test.jpg"
    file_path.write_bytes(b"fake image data")
    return file_path

@pytest.fixture
def sample_user():
    from HillSide.models import User, RoleEnum
    user = User(
        first_name="Test",
        last_name="User",
        username="testuser",
        email="user@example.com",
        password="hashed",
        role=RoleEnum.USER,
        is_verified=True,
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def sample_course(app):
    course = Course(
        title="Sample Course",
        description="Test desc",
        start_date=None,
        duration_weeks=4,
        total_seats=20,
        image=None,
    )
    db.session.add(course)
    db.session.commit()
    return course.id

@pytest.fixture
def regular_user(client, app):
    user = User(
        first_name="Charlie",
        last_name="Brown",
        username="charlie",
        email="charlie@example.com",
        password=bcrypt.generate_password_hash("testpass123").decode("utf-8"),
        role=RoleEnum.USER,
        is_verified=True,
    )
    db.session.add(user)
    db.session.commit()

    client.post("/login", data={
        "email": "charlie@example.com",
        "password": "testpass123"
    }, follow_redirects=True)

    yield user


@pytest.fixture
def admin_user(app):
    user = User(
        username="admin",
        email="admin@test.com",
        password=bcrypt.generate_password_hash("password").decode("utf-8"),
        first_name="Admin",
        last_name="User",
        role=RoleEnum.ADMIN,
        is_verified=True,
    )
    db.session.add(user)
    db.session.commit()
    yield user


@pytest.fixture
def logged_in_admin(client, admin_user):
    _login(client, "admin@test.com")
    return admin_user