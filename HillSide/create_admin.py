from app import app
from extensions import db
from models import User
import bcrypt  # Importing bcrypt

with app.app_context():
    # Generating a salt and hashing the password using bcrypt
    hashed_password = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt())
    
    # Create new user with hashed password
    admin = User(username='admin', email='admin@admin.com', password=hashed_password.decode('utf-8'), role='admin')
    
    db.session.add(admin)
    db.session.commit()
    print("Admin added successfully!")
