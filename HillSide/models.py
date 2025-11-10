# from extensions import db
from HillSide.extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    role = db.Column(db.String(50), default='user')

    enrollments = db.relationship('Enrollment', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'
    
    def is_admin(self):
        return self.role == 'admin'


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

    user = db.relationship('User', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')

    def __repr__(self):
        return f'<Enrollment user={self.user_id} course={self.course_id}>'
