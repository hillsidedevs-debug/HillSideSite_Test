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



from flask import current_app
from werkzeug.utils import secure_filename
import uuid
import os

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

        # Parse date
        start_date = (
            datetime.strptime(start_date_str, '%Y-%m-%d').date()
            if start_date_str else None
        )

        # ---------------------------
        # SAFE IMAGE HANDLING
        # ---------------------------
        image_file = request.files.get('image')
        image_filename = None

        if image_file and image_file.filename:
            # Validate extension
            ext = image_file.filename.rsplit('.', 1)[-1].lower()
            if ext not in {'png', 'jpg', 'jpeg', 'gif'}:
                flash("❌ Invalid image format.", "danger")
                return redirect(url_for("courses.add_course"))

            # Ensure upload folder exists
            upload_folder = os.path.join(current_app.root_path, "static/uploads/courses")
            os.makedirs(upload_folder, exist_ok=True)

            # Generate safe + unique filename
            original = secure_filename(image_file.filename)
            unique_name = f"{uuid.uuid4().hex}_{original}"

            # Save file
            save_path = os.path.join(upload_folder, unique_name)
            image_file.save(save_path)

            image_filename = unique_name

        # ---------------------------
        # CREATE COURSE
        # ---------------------------
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
    #all_courses = Course.query.all()
    print("ROUTE DB URI:", db.engine.url)


    page = request.args.get('page', 1, type=int)
    pagination = Course.query.order_by(Course.id.desc()).paginate(
        page = page,
        per_page=9,
        error_out=False
    )
    return render_template('courses.html', courses=pagination.items, pagination=pagination)

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
