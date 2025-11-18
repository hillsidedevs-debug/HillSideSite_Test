from HillSide import create_app
from HillSide.extensions import db, bcrypt
from HillSide.models import User, RoleEnum

def create_admin():
    app = create_app()

    with app.app_context():
        # Check if an admin already exists
        if User.query.filter_by(username='admin').first():
            print("Admin already exists!")
            return

        hashed_password = bcrypt.generate_password_hash('admin').decode('utf-8')

        admin = User(
            first_name="Admin",
            last_name="User",
            username="admin",
            email="admin@admin.com",
            password=hashed_password,
            role=RoleEnum.ADMIN
        )

        db.session.add(admin)
        db.session.commit()
        print("Admin created successfully!")

if __name__ == "__main__":
    create_admin()
