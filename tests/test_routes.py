def assert_accessible(response, route):
    assert response.status_code in (200, 302, 401), f"{route} returned {response.status_code}"

def test_index_accessible(client):
    res = client.get('/')
    assert_accessible(res, '/')


def test_about_accessible(client):
    res = client.get('/about')
    assert_accessible(res, '/about')


def test_admin_dashboard_accessible(client):
    res = client.get('/admin-dashboard')
    assert_accessible(res, '/admin-dashboard')


def test_contact_get_accessible(client):
    res = client.get('/contact')
    assert_accessible(res, '/contact (GET)')


def test_contact_post_accessible(client):
    res = client.post('/contact', data={})
    assert_accessible(res, '/contact (POST)')


def test_course_details_accessible(client):
    res = client.get('/course/1')
    assert_accessible(res, '/course/<int:course_id>')


def test_courses_add_course_get_accessible(client):
    res = client.get('/add-course')
    assert_accessible(res, '/add-course (GET)')


def test_courses_add_course_post_accessible(client):
    res = client.post('/add-course', data={})
    assert_accessible(res, '/add-course (POST)')


def test_courses_course_details_accessible(client):
    res = client.get('/courses/1')
    assert_accessible(res, '/courses/<int:course_id>')


def test_courses_enroll_course_accessible(client):
    res = client.post('/courses/1/enroll')
    assert_accessible(res, '/courses/<int:course_id>/enroll')


def test_courses_list_courses_accessible(client):
    res = client.get('/courses')
    assert_accessible(res, '/courses')


def test_dashboard_accessible(client):
    res = client.get('/dashboard')
    assert_accessible(res, '/dashboard')


def test_delete_course_accessible(client):
    res = client.post('/course/delete/1')
    assert_accessible(res, '/course/delete/<int:course_id>')


def test_edit_course_get_accessible(client):
    res = client.get('/course/edit/1')
    assert_accessible(res, '/course/edit/<int:course_id> (GET)')


def test_edit_course_post_accessible(client):
    res = client.post('/course/edit/1', data={})
    assert_accessible(res, '/course/edit/<int:course_id> (POST)')


def test_list_users_accessible(client):
    res = client.get('/users')
    assert_accessible(res, '/users')


def test_login_get_accessible(client):
    res = client.get('/login')
    assert_accessible(res, '/login (GET)')


def test_login_post_accessible(client):
    res = client.post('/login', data={})
    assert_accessible(res, '/login (POST)')


def test_logout_accessible(client):
    res = client.get('/logout')
    assert_accessible(res, '/logout')


def test_manage_courses_accessible(client):
    res = client.get('/manage_courses')
    assert_accessible(res, '/manage_courses')


def test_manage_users_accessible(client):
    res = client.get('/manage_users')
    assert_accessible(res, '/manage_users')


def test_register_get_accessible(client):
    res = client.get('/register')
    assert_accessible(res, '/register (GET)')


def test_register_post_accessible(client):
    res = client.post('/register', data={})
    assert_accessible(res, '/register (POST)')


def test_remove_enrollment_accessible(client):
    res = client.post('/enrollment/remove/1')
    assert_accessible(res, '/enrollment/remove/<int:enrollment_id>')


def test_services_accessible(client):
    res = client.get('/services')
    assert_accessible(res, '/services')


def test_user_details_accessible(client):
    res = client.get('/user/1')
    assert_accessible(res, '/user/<int:user_id>')