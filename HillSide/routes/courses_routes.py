from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from datetime import datetime
import os


from HillSide.extensions import db
from HillSide.models import Course, Enrollment
from HillSide.utils import admin_required


# from utils import admin_required
# from models import Course, Enrollment
# from extensions import db

courses_bp = Blueprint('courses', __name__)

UPLOAD_FOLDER = 'static/uploads/courses'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@courses_bp.route('/add-course', methods=['GET', 'POST'])
@login_required
@admin_required
def add_course():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        start_date_str = request.form.get('start_date')
        duration_weeks = request.form.get('duration_weeks')
        total_seats = request.form.get('total_seats')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None

        image_file = request.files.get('image')
        image_filename = None
        if image_file and image_file.filename:
            image_filename = image_file.filename
            image_file.save(f'static/uploads/courses/{image_filename}')

        course = Course(
            title=title,
            description=description,
            start_date=start_date,
            duration_weeks=int(duration_weeks) if duration_weeks else None,
            total_seats=int(total_seats) if total_seats else None,
            image=image_filename
        )
        db.session.add(course)
        db.session.commit()

        flash('✅ Course added successfully!', 'success')
        return redirect(url_for('courses.list_courses'))

    return render_template('add_course.html')


@courses_bp.route('/courses')
def list_courses():
    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses)

@courses_bp.route('/courses/<int:course_id>')
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_details.html', course=course)


@courses_bp.route('/courses/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll_course(course_id):
    course = Course.query.get_or_404(course_id)

    existing = Enrollment.query.filter_by(user_id=current_user.id, course_id=course.id).first()
    if existing:
        flash('⚠️ You are already enrolled in this course.', 'warning')
        return redirect(url_for('courses.course_details', course_id=course.id))

    enrollment = Enrollment(user_id=current_user.id, course_id=course.id)
    db.session.add(enrollment)
    db.session.commit()

    flash('🎉 Successfully enrolled in the course!', 'success')
    return redirect(url_for('courses.course_details', course_id=course.id))
