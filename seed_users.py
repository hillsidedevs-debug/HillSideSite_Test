from HillSide.extensions import db, bcrypt
from HillSide.models import User, RoleEnum, GenderEnum
from faker import Faker
from random import choice
import hashlib

fake = Faker()

roles = [
    RoleEnum.USER] * 42 + \
    [RoleEnum.STAFF] * 7 + \
    [RoleEnum.ADMIN]

genders = [None] * 10 + list(GenderEnum)


def seed_users(n=50):
    users = []
    for i in range(n):
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = f"{first_name.lower()}{last_name.lower()}{fake.random_int(1, 999)}"
        base_email = f"{first_name.lower()}{last_name.lower()}"
        email = f"{base_email}{fake.random_int(1, 999)}@example.com"
        plain_password = "password123"
        password_hash = bcrypt.generate_password_hash(plain_password).decode("utf-8")

        user = User(first_name=first_name, 
                    last_name=last_name,
                    username=username,
                    email=email,
                    password=password_hash,
                    role=choice(roles),
                    phone_number=fake.phone_number()[:20] if fake.boolean(chance_of_getting_true=70) else None,
                    photo=None,
                    resume=None,
                    address=fake.address().replace("\n", ", ") if fake.boolean(chance_of_getting_true=60) else None,
                    gender=choice(genders),
                    education_qualification=choice([
                        None,
                        "Bachelor's in Computer Science",
                        "Master's in Business Administration",
                        "High School Diploma",
                        "PhD in Physics",
                        "Associate Degree in Nursing"
            ]))
        users.append(user)
    
    db.session.bulk_save_objects(users)
    db.session.commit()
    print(f"Seeded {n} users")


if __name__ == "__main__":
    from HillSide import create_app
    app = create_app()

    with app.app_context():
        seed_users(50)