# from extensions import db
from HillSide.extensions import db
from flask_login import UserMixin
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Enum



class RoleEnum(PyEnum):
    USER = 'user'
    STAFF = 'staff'
    ADMIN = 'admin'

class StatusEnum(PyEnum):
    ACTIVE = 'active'
    COMPLETED = 'completed'
    DROPPED = 'dropped'

# New enum for gender
class GenderEnum(PyEnum):
    MALE = 'M'
    FEMALE = 'F'
    OTHER = 'Other'
    PREFER_NOT_TO_SAY = 'Prefer not to say'

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)

    username = db.Column(db.String(150), nullable=False, unique=True, index=True)
    email = db.Column(db.String(150), nullable=False, unique=True, index=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(Enum(RoleEnum, native_enum=False), default=RoleEnum.USER)

    phone_number = db.Column(db.String(20), nullable=True)
    photo = db.Column(db.String(255), nullable=True)
    resume = db.Column(db.String(255), nullable=True)
    address = db.Column(db.Text, nullable=True)
    gender = db.Column(
    Enum(GenderEnum, values_callable=lambda obj: [e.value for e in obj], native_enum=False),
    nullable=True
    )

    education_qualification = db.Column(db.String(200), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    enrollments = db.relationship(
        'Enrollment',
        back_populates='user',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<User {self.username}>'

    def is_admin(self):
        return self.role == RoleEnum.ADMIN

    def is_staff(self):
        return self.role in (RoleEnum.STAFF, RoleEnum.ADMIN)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)

    start_date = db.Column(db.Date, nullable=True)
    duration_weeks = db.Column(db.Integer, nullable=True)
    total_seats = db.Column(db.Integer, nullable=True)

    enrollments = db.relationship('Enrollment', back_populates='course', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Course {self.title}>'

    @property
    def seats_left(self):
        """Returns how many seats are still available."""
        return self.total_seats - len(self.enrollments) if self.total_seats else None

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    enrolled_on = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.Column(db.Float, default=0.0)  
    status = db.Column(db.String(50), default='active') 

    city_town = db.Column(db.String(100), nullable=True)

    user = db.relationship('User', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')

    def __repr__(self):
        return f'<Enrollment user={self.user_id} course={self.course_id}>'
