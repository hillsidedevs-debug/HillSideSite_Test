# from HillSide.models import User

# def test_user_registration(client, app):
#     response = client.post('/register', data={
#         'first_name': 'John',
#         'last_name': 'Doe',
#         'username': 'johndoe',
#         'email' : 'john@example.com',
#         'password': 'password123'
#     }, follow_redirects=True)

#     assert response.status_code == 200

#     with app.app_context():
#         user = User.query.filter_by(username='johndoe').first()
#         assert user is not None
#         assert user.username == 'johndoe'
