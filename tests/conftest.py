# tests/conftest.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from HillSide import create_app
from HillSide.extensions import db, bcrypt
from HillSide.models import User, RoleEnum, Course



@pytest.fixture(scope="function")
def app(tmp_path): # 👈 ADD tmp_path as an argument here

    # --- Start of new/modified code ---
    # 1. Create a temporary SQLite file path
    db_path = tmp_path / "test_db.sqlite"

    app_config = {
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        # 2. Use the file path instead of :memory:
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        # ... rest of config ...
        "WTF_CSRF_ENABLED": False,
        "UPLOAD_FOLDER_PHOTOS": "/tmp/photos",
        "UPLOAD_FOLDER_RESUMES": "/tmp/resumes",
    }
    # --- End of new/modified code ---

    app = create_app(app_config)
    # ... rest of fixture ...

    with app.app_context():
        print("Creating database tables for test...")
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
    with app.app_context():
        course = Course(
            title="Sample Course",
            description="Test desc",
            start_date=None,
            duration_weeks=4,
            total_seats=20,
            image=None,
        )
        from HillSide.extensions import db
        db.session.add(course)
        db.session.commit()
        return course.id

@pytest.fixture
def regular_user(client, app):
    with app.app_context():
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

        # Log the user in
        client.post("/login", data={
            "email": "charlie@example.com",
            "password": "testpass123"
        }, follow_redirects=True)

        yield user

        # Cleanup
        db.session.delete(user)
        db.session.commit()



@pytest.fixture
def admin_user(app):
    with app.app_context():
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
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def logged_in_admin(client, admin_user):
    _login(client, "admin@test.com")
    return admin_user