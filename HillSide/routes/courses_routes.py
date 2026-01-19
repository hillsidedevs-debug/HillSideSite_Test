from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from datetime import datetime
import os


from HillSide.extensions import db
from HillSide.models import Course, Enrollment
from HillSide.utils import admin_required, is_valid_file
from HillSide.forms.add_course_form import CourseForm


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
    form = CourseForm()
    
    if form.validate_on_submit():
        # Handle Image Saving
        image_filename = None
        if form.image.data:
            image_file = form.image.data
            upload_folder = os.path.join(current_app.root_path, "static/uploads/courses")
            os.makedirs(upload_folder, exist_ok=True)
            
            original = secure_filename(image_file.filename)
            unique_name = f"{uuid.uuid4().hex}_{original}"
            image_file.save(os.path.join(upload_folder, unique_name))
            image_filename = unique_name

        # Create Course using form.data
        course = Course(
            title=form.title.data,
            description=form.description.data,
            start_date=form.start_date.data,
            duration_weeks=form.duration_weeks.data,
            total_seats=form.total_seats.data,
            image=image_filename,
            who_is_this_for=form.who_is_this_for.data,
            learning_outcomes=form.learning_outcomes.data,
            course_structure=form.course_structure.data,
            instructor_name=form.instructor_name.data,
            instructor_bio=form.instructor_bio.data,
            faqs=form.faqs.data
        )

        db.session.add(course)
        db.session.commit()

        flash('✅ Course added successfully!', 'success')
        return redirect(url_for('courses.list_courses'))

    return render_template('add_course.html', form=form)




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
