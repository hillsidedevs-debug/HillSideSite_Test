import pytest
from HillSide.models import Course, Enrollment


# ---------------------------------------------------
# allowed_file() tests
# ---------------------------------------------------
def test_allowed_file(app):
    from HillSide.routes.courses_routes import allowed_file

    assert allowed_file("test.jpg") is True
    assert allowed_file("test.PNG") is True
    assert allowed_file("test.gif") is True
    assert allowed_file("test.pdf") is False  # not allowed
    assert allowed_file("test") is False      # no extension
    assert allowed_file("") is False

# ---------------------------------------------------
# /add-course (GET)
# ---------------------------------------------------
def test_add_course_get_admin(client, logged_in_admin):
    response = client.get("/add-course")
    assert response.status_code == 200
    assert b"course" in response.data.lower()


def test_add_course_get_regular_user_denied(client, regular_user):
    # This should either forbid access (302 -> redirect) or show a forbidden page
    response = client.get("/add-course", follow_redirects=False)
    assert response.status_code in (302, 403)

# ---------------------------------------------------
# /add-course (POST) – successful creation
# ---------------------------------------------------
def test_add_course_post_success(client, logged_in_admin, sample_image, app):
    data = {
        "title": "Python Course",
        "description": "Learn Python fast",
        "start_date": "2025-01-01",
        "duration_weeks": "6",
        "total_seats": "25",
    }

    # Attach image
    with open(sample_image, "rb") as img:
        data["image"] = (img, "test.jpg")

        response = client.post(
            "/add-course",
            data=data,
            content_type="multipart/form-data",
            follow_redirects=True
        )

    # Should redirect to /courses
    assert response.status_code == 200
    assert b"course added successfully" in response.data.lower()

    # Verify DB contents
    with app.app_context():
        course = Course.query.filter_by(title="Python Course").first()
        assert course is not None
        assert course.duration_weeks == 6
        assert course.total_seats == 25
        #assert course.image == "test.jpg"

# ---------------------------------------------------
# /courses (pagination)
# ---------------------------------------------------
def test_list_courses_pagination(client, logged_in_admin):
    # Create 15 courses through the real /add-course route
    for i in range(15):
        response = client.post(
            "/add-course",
            data={
                "title": f"Course {i}",
                "description": "test",
                "total_seats": 10,
            },
            follow_redirects=True
        )
        assert response.status_code == 200

    # Request page 1
    response = client.get("/courses?page=1")
    data = response.data

    for i in range(14, 5, -1):
        assert f"Course {i}".encode() in data
    # # Page 1 should contain the first 9 courses (newest first, so reversed order)
    # for i in range(6, -1, -1):  # because pagination sorts DESC by id
    #     assert f"Course {i}".encode() in data

    # Request page 2
    response2 = client.get("/courses?page=2")
    data2 = response2.data

    # Page 2 should contain remaining courses
    for i in range(5, -1, -1):
        assert f"Course {i}".encode() in data2



# # ---------------------------------------------------
# # /courses/<id> (course details)
# # ---------------------------------------------------
def test_course_details(client, sample_course):
    response = client.get(f"/courses/{sample_course}")
    assert response.status_code == 200
    assert b"Sample Course" in response.data



# # ---------------------------------------------------
# # Enrollment tests
# # ---------------------------------------------------
def test_enroll_course_success(client, regular_user, sample_course, app):
    """User enrolls successfully."""
    response = client.post(f"/courses/{sample_course}/enroll", follow_redirects=True)

    assert response.status_code == 200
    assert b"successfully enrolled" in response.data.lower()

    with app.app_context():
        enrollment = Enrollment.query.filter_by(
            user_id=regular_user.id,
            course_id=sample_course
        ).first()
        assert enrollment is not None


def test_enroll_course_already_enrolled(client, regular_user, sample_course, app):
    """User tries to enroll twice."""

    # First enrollment
    client.post(f"/courses/{sample_course}/enroll", follow_redirects=True)

    # Second attempt
    response = client.post(f"/courses/{sample_course}/enroll", follow_redirects=True)

    assert b"already enrolled" in response.data.lower()


def test_enroll_course_requires_login(client, sample_course):
    """Anonymous users should be redirected to login."""
    response = client.post(f"/courses/{sample_course}/enroll", follow_redirects=False)

    # Flask-Login normally redirects with 302
    assert response.status_code == 302
    assert "/login" in response.location