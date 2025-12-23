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
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'mov'}

def allowed_video(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS


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
        description = request.form.get('description')

        start_date_str = request.form.get('start_date')
        duration_weeks = request.form.get('duration_weeks')
        total_seats = request.form.get('total_seats')

        who_is_this_for = request.form.get('who_is_this_for')
        learning_outcomes = request.form.get('learning_outcomes')
        course_structure = request.form.get('course_structure')

        instructor_name = request.form.get('instructor_name')
        instructor_bio = request.form.get('instructor_bio')

        faqs = request.form.get('faqs')

        # ---------------------------
        # PARSE DATE
        # ---------------------------
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
            ext = image_file.filename.rsplit('.', 1)[-1].lower()
            if ext not in {'png', 'jpg', 'jpeg', 'gif'}:
                flash("❌ Invalid image format.", "danger")
                return redirect(url_for("courses.add_course"))

            upload_folder = os.path.join(
                current_app.root_path, "static/uploads/courses"
            )
            os.makedirs(upload_folder, exist_ok=True)

            original = secure_filename(image_file.filename)
            unique_name = f"{uuid.uuid4().hex}_{original}"

            image_file.save(os.path.join(upload_folder, unique_name))
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
            image=image_filename,

            who_is_this_for=who_is_this_for,
            learning_outcomes=learning_outcomes,
            course_structure=course_structure,

            instructor_name=instructor_name,
            instructor_bio=instructor_bio,

            faqs=faqs
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

@courses_bp.route('/courses/<int:course_id>/upload-video', methods=['POST'])
@login_required
def upload_course_video(course_id):
    # if not current_user.is_staff():
    #     flash('Unauthorized', 'danger')
    #     return redirect(url_for('courses.course_details', course_id=course_id))

    course = Course.query.get_or_404(course_id)

    if 'video' not in request.files:
        flash('No video file provided', 'danger')
        return redirect(url_for('courses.course_details', course_id=course_id))

    file = request.files['video']

    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('courses.course_details', course_id=course_id))

    if not allowed_video(file.filename):
        flash('Invalid video format', 'danger')
        return redirect(url_for('courses.course_details', course_id=course_id))

    filename = secure_filename(file.filename)

    upload_folder = os.path.join(
        current_app.root_path,
        'static/uploads/courses/videos'
    )
    os.makedirs(upload_folder, exist_ok=True)

    file.save(os.path.join(upload_folder, filename))

    course.video = filename
    db.session.commit()

    flash('Course intro video uploaded successfully', 'success')
    return redirect(url_for('courses.course_details', course_id=course_id))

@courses_bp.route('/courses/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll_course(course_id):
    course = Course.query.get_or_404(course_id)

    # Prevent double enrollment
    existing = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course.id
    ).first()
    if existing:
        flash('You are already enrolled in this course.', 'warning')
        return redirect(url_for('courses.course_details', course_id=course.id))

    # Get the city/town from the form (the dropdown or text input you added)
    city_town = request.form.get('city_town', '').strip()
    if city_town == '':
        city_town = None

    # Create enrollment with the new field
    enrollment = Enrollment(
        user_id=current_user.id,
        course_id=course.id,
        city_town=city_town
    )

    db.session.add(enrollment)
    db.session.commit()

    flash('Successfully enrolled in the course!', 'success')
    return redirect(url_for('courses.course_details', course_id=course.id))
