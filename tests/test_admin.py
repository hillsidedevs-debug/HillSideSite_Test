from HillSide.models import RoleEnum, GenderEnum, User, Course, Enrollment, Review
from HillSide.extensions import db, bcrypt

def test_admin_dashboard(logged_in_admin, client):
    response = client.get("/admin-dashboard")
    assert response.status_code == 200
    assert b"total_users" not in response.data  # template renders HTML, not JSON

def test_manage_courses(logged_in_admin, client):
    response = client.get("/manage_courses")
    assert response.status_code == 200

def test_manage_users(logged_in_admin, client, sample_user):
    response = client.get("/manage_users")
    assert response.status_code == 200
    assert b"testuser" in response.data

def test_admin_course_details(logged_in_admin, client, sample_course):
    response = client.get(f"/course/{sample_course}")
    assert response.status_code == 200
    assert b"Sample Course" in response.data

def test_delete_course(logged_in_admin, client, sample_course):
    response = client.post(f"/course/delete/{sample_course}", follow_redirects=True)
    assert response.status_code == 200

    from HillSide.models import Course
    assert Course.query.get(sample_course) is None

def test_remove_enrollment(logged_in_admin, client, sample_user, sample_course):
    from HillSide.models import Enrollment
    from HillSide.extensions import db
    e = Enrollment(user_id=sample_user.id, course_id=sample_course)
    db.session.add(e)
    db.session.commit()

    response = client.post(f"/enrollment/remove/{e.id}", follow_redirects=True)
    assert response.status_code == 200
    assert Enrollment.query.get(e.id) is None

def test_add_staff_simple(logged_in_admin, client):
    from HillSide.models import User, RoleEnum
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "staffuser",
        "email": "staff@example.com",
        "password": "Password123",
        "password_confirm": "Password123",
        "role": RoleEnum.STAFF.value,
    }

    response = client.post("/add-staff", data=data, follow_redirects=True)
    assert response.status_code == 200
    #assert b"success" in response.data.lower() or b"welcome" in response.data.lower()

    new_staff = User.query.filter_by(username="staffuser").first()
    
    assert new_staff is not None
    assert new_staff.role == RoleEnum.STAFF

def test_staff_details(logged_in_admin, client, sample_user):
    sample_user.role = RoleEnum.STAFF  # STAFF enum value
    from HillSide.extensions import db
    db.session.commit()

    response = client.get(f"/staff/{sample_user.id}")
    assert response.status_code == 200


# ---------------------------------------------------
# Access control
# ---------------------------------------------------

def test_admin_dashboard_requires_login(client):
    response = client.get("/admin-dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.location


def test_admin_dashboard_regular_user_forbidden(client, regular_user):
    response = client.get("/admin-dashboard")
    assert response.status_code == 403


# ---------------------------------------------------
# Manage staff
# ---------------------------------------------------

def test_manage_staff_get(logged_in_admin, client):
    response = client.get("/manage-staff")
    assert response.status_code == 200


# ---------------------------------------------------
# User details and delete
# ---------------------------------------------------

def test_user_details_get(logged_in_admin, client, app):
    with app.app_context():
        user = User(
            first_name="Detail",
            last_name="Test",
            username="detailuser",
            email="detail@example.com",
            password=bcrypt.generate_password_hash("pass").decode("utf-8"),
            role=RoleEnum.USER,
            is_verified=True,
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    response = client.get(f"/user/{user_id}")
    assert response.status_code == 200


def test_delete_user(logged_in_admin, client, app):
    with app.app_context():
        user = User(
            first_name="Delete",
            last_name="Me",
            username="deleteme",
            email="deleteme@example.com",
            password=bcrypt.generate_password_hash("pass").decode("utf-8"),
            role=RoleEnum.USER,
            is_verified=True,
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    response = client.post(f"/user/delete/{user_id}", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        assert User.query.get(user_id) is None


def test_delete_own_account_forbidden(logged_in_admin, client, app):
    with app.app_context():
        admin = User.query.filter_by(username="admin").first()
        admin_id = admin.id

    response = client.post(f"/user/delete/{admin_id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"cannot delete your own account" in response.data.lower()

    with app.app_context():
        assert User.query.get(admin_id) is not None


def test_delete_user_404(logged_in_admin, client):
    response = client.post("/user/delete/99999")
    assert response.status_code == 404


# ---------------------------------------------------
# Edit course
# ---------------------------------------------------

def test_edit_course_get(logged_in_admin, client, sample_course):
    response = client.get(f"/course/edit/{sample_course}")
    assert response.status_code == 200


def test_edit_course_post(logged_in_admin, client, app, sample_course):
    response = client.post(f"/course/edit/{sample_course}", data={
        "title": "Updated Course Title",
        "description": "Updated description",
        "duration_weeks": 8,
        "total_seats": 25,
    }, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        course = Course.query.get(sample_course)
        assert course.title == "Updated Course Title"
        assert course.duration_weeks == 8


def test_delete_course_404(logged_in_admin, client):
    response = client.post("/course/delete/99999")
    assert response.status_code == 404


# ---------------------------------------------------
# Reviews moderation
# ---------------------------------------------------

def _make_review(app, approved=False):
    """Helper: create a user, course, and review. Returns review_id."""
    with app.app_context():
        user = User(
            first_name="Review",
            last_name="Author",
            username=f"reviewer_{id(app)}",
            email=f"reviewer_{id(app)}@example.com",
            password=bcrypt.generate_password_hash("pass").decode("utf-8"),
            role=RoleEnum.USER,
            is_verified=True,
        )
        course = Course(title="Review Course", description="desc", duration_weeks=4, total_seats=10)
        db.session.add_all([user, course])
        db.session.flush()
        review = Review(user_id=user.id, course_id=course.id, rating=4, comment="Good", approved=approved)
        db.session.add(review)
        db.session.commit()
        return review.id


def test_reviews_list_get(logged_in_admin, client):
    response = client.get("/reviews")
    assert response.status_code == 200


def test_approve_review(logged_in_admin, client, app):
    review_id = _make_review(app, approved=False)

    response = client.post(f"/review/{review_id}/approve", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        review = Review.query.get(review_id)
        assert review.approved is True


def test_approve_already_approved_review(logged_in_admin, client, app):
    review_id = _make_review(app, approved=True)

    response = client.post(f"/review/{review_id}/approve", follow_redirects=True)
    assert response.status_code == 200
    assert b"already approved" in response.data.lower()


def test_reject_review(logged_in_admin, client, app):
    review_id = _make_review(app, approved=False)

    response = client.post(f"/review/{review_id}/reject", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        assert Review.query.get(review_id) is None


def test_delete_review(logged_in_admin, client, app):
    review_id = _make_review(app, approved=True)

    response = client.post(f"/review/{review_id}/delete", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        assert Review.query.get(review_id) is None




