import sys
import secrets
import string
import getpass
from HillSide import create_app
from HillSide.extensions import db, bcrypt
from HillSide.models import User, RoleEnum


def generate_strong_password(length=20):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    while True:
        pw = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in pw)
            and any(c.isupper() for c in pw)
            and any(c.isdigit() for c in pw)
            and any(c in "!@#$%^&*()-_=+" for c in pw)
        ):
            return pw


def validate_password(pw):
    errors = []
    if len(pw) < 12:
        errors.append("at least 12 characters")
    if not any(c.isupper() for c in pw):
        errors.append("an uppercase letter")
    if not any(c.islower() for c in pw):
        errors.append("a lowercase letter")
    if not any(c.isdigit() for c in pw):
        errors.append("a digit")
    if not any(c in string.punctuation for c in pw):
        errors.append("a special character (!@#$... etc.)")
    return errors


def prompt_password():
    suggestion = generate_strong_password()
    print(f"\nSuggested strong password: {suggestion}")
    use_suggested = input("Use this password? [Y/n]: ").strip().lower()
    if use_suggested in ("", "y", "yes"):
        return suggestion

    while True:
        pw = getpass.getpass("Enter password: ")
        errors = validate_password(pw)
        if errors:
            print(f"Password must contain: {', '.join(errors)}")
            continue
        confirm = getpass.getpass("Confirm password: ")
        if pw != confirm:
            print("Passwords do not match. Try again.")
            continue
        return pw


def delete_existing_admins(app):
    with app.app_context():
        admins = User.query.filter_by(role=RoleEnum.ADMIN).all()
        if not admins:
            print("No existing admin accounts found.")
            return
        print("\nExisting admin accounts:")
        for u in admins:
            print(f"  - username={u.username}  email={u.email}")
        confirm = input("\nDelete all of the above? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes"):
            print("Skipping deletion.")
            return
        for u in admins:
            db.session.delete(u)
        db.session.commit()
        print("Existing admin accounts deleted.")


def create_admin():
    app = create_app()

    print("=== Admin Account Setup ===")

    if "--delete" in sys.argv:
        delete_existing_admins(app)
        return

    with app.app_context():
        existing = User.query.filter_by(role=RoleEnum.ADMIN).all()
        if existing:
            print("\nExisting admin accounts:")
            for u in existing:
                print(f"  - username={u.username}  email={u.email}")
            choice = input("\nDelete existing admin(s) before creating new one? [y/N]: ").strip().lower()
            if choice in ("y", "yes"):
                for u in existing:
                    db.session.delete(u)
                db.session.commit()
                print("Existing admins removed.")

        username = input("\nAdmin username: ").strip()
        if not username:
            print("Username cannot be empty.")
            sys.exit(1)
        if User.query.filter_by(username=username).first():
            print(f"Username '{username}' is already taken.")
            sys.exit(1)

        email = input("Admin email: ").strip()
        if not email or "@" not in email:
            print("Invalid email.")
            sys.exit(1)
        if User.query.filter_by(email=email).first():
            print(f"Email '{email}' is already in use.")
            sys.exit(1)

        first_name = input("First name: ").strip() or "Admin"
        last_name = input("Last name: ").strip() or "User"

        password = prompt_password()

        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        admin = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=hashed,
            role=RoleEnum.ADMIN,
            is_verified=True,
        )
        db.session.add(admin)
        db.session.commit()
        print(f"\nAdmin '{username}' created successfully.")


if __name__ == "__main__":
    create_admin()
