from HillSide.models import RoleEnum, GenderEnum

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




