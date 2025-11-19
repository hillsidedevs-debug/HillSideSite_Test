# from HillSide.extensions import db
# from HillSide.models import RoleEnum

# def test_user_login(client, app):
#     from HillSide.models import User
#     from HillSide.extensions import bcrypt
#     from flask import url_for

#     # Create fake user
#     with app.app_context():
#         user = User(
#             first_name="Test",
#             last_name="User",
#             username="testuser",
#             email="test@example.com",
#             password=bcrypt.generate_password_hash("secret").decode("utf-8"),
#             role=RoleEnum.USER
#         )
#         db.session.add(user)
#         db.session.commit()

#     login_data = {
#         "email": "test@example.com",
#         "password": "secret"
#     }

#     response = client.post(
#         "/login",
#         data=login_data,
#         follow_redirects=True   # This is important!
#     )

#     # Option A: Check you're redirected to the expected landing page
#     assert response.request.path == "/"                  # or "/dashboard", "/profile", etc.
#     # or more robust using url_for if you have a named route
#     #assert response.request.path == url_for("main.index", _external=False)

#     # Optional: also verify status code
#     assert response.status_code == 200