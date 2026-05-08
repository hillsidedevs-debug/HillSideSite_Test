from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from datetime import datetime
import os


from HillSide.extensions import db
from HillSide.models import Course, Enrollment, Review
from HillSide.utils import admin_required, staff_required, is_valid_file, generate_secure_filename
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
from werkzeug.utils  import secure_filename
import uuid
import os 


@courses_bp.route('/add-course', methods=['GET', 'POST'])
@login_required
@staff_required
def add_course():
    form = CourseForm()
    
    if form.validate_on_submit():
        image_relative_path = None
        
        if form.image.data:
            # ── 1. Prepare filename (same style as your correct example) ──
            original_filename = secure_filename(form.image.data.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            
            # Relative path stored in DB (this is the key part)
            relative_path = os.path.join('courses', unique_filename)
            
            # Full save path on disk
            # Using UPLOAD_FOLDER if set, otherwise fallback to static/uploads/courses
            upload_base = current_app.config.get(
                'UPLOAD_FOLDER',
                os.path.join(current_app.root_path, 'static', 'uploads')
            )
            full_save_path = os.path.join(upload_base, relative_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(full_save_path), exist_ok=True)
            
            # Save the file
            form.image.data.save(full_save_path)
            
            # This goes into the database
            image_relative_path = relative_path
        
        # ── Create course ────────────────────────────────────────
        course = Course(
            title=form.title.data,
            description=form.description.data,
            start_date=form.start_date.data,
            duration_weeks=form.duration_weeks.data,
            total_seats=form.total_seats.data,
            image=image_relative_path,                    # ← now 'courses/abc1234d-name.jpg'
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
    
    # Get the 10 most recent approved reviews
    approved_reviews = (
        Review.query
        .filter_by(course_id=course.id, approved=True)
        .order_by(Review.created_at.desc())
        .limit(10)
        .all()
    )
    
    is_enrolled = False
    if current_user.is_authenticated:
        enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
        if enrollment:
            is_enrolled=True
    return render_template(
        'course_details.html',
        course=course,
        approved_reviews=approved_reviews,
        is_enrolled=is_enrolled
    )

@courses_bp.route('/courses/<int:course_id>/upload-video', methods=['POST'])
@login_required
@admin_required
def upload_course_video(course_id):
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

    if not is_valid_file(file, 'video'):
        flash('Invalid video file.', 'danger')
        return redirect(url_for('courses.course_details', course_id=course_id))

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = generate_secure_filename("video", ext)

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


@courses_bp.route('/courses/<int:course_id>/delete-video', methods=['POST'])
@login_required
@admin_required
def delete_course_video(course_id):
    course = Course.query.get_or_404(course_id)

    if course.video:
        video_path = os.path.join(
            current_app.root_path,
            'static/uploads/courses/videos',
            course.video
        )
        if os.path.exists(video_path):
            os.remove(video_path)
        course.video = None
        db.session.commit()
        flash('Course intro video removed.', 'success')
    else:
        flash('No video to remove.', 'warning')

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

    city_town = request.form.get('city_town', '').strip() or None

    enrollment = Enrollment(
        user_id=current_user.id,
        course_id=course.id,
        city_town=city_town,
    )

    db.session.add(enrollment)
    db.session.commit()

    flash('Successfully enrolled in the course!', 'success')
    return redirect(url_for('courses.course_details', course_id=course.id))

@courses_bp.route('/courses/<int:course_id>/review', methods=['GET', 'POST'])
@login_required
def submit_review(course_id):
    course = Course.query.get_or_404(course_id)

    # Only allow review if enrolled and course is completed (or dropped, your choice)
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course.id
    ).first()

    if not enrollment:
        flash("You must be enrolled in this course to leave a review.", "warning")
        return redirect(url_for('courses.course_details', course_id=course.id))

    # if enrollment.status not in ['completed', 'dropped']:
    #     flash("You can only review courses you've completed.", "warning")
    #     return redirect(url_for('courses.course_details', course_id=course.id))

    # Prevent duplicate reviews
    existing_review = Review.query.filter_by(
        user_id=current_user.id,
        course_id=course.id
    ).first()

    if existing_review:
        flash("You have already submitted a review for this course.", "info")
        return redirect(url_for('courses.course_details', course_id=course.id))

    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment', '').strip()

        try:
            rating = int(rating)
            if not 1 <= rating <= 5:
                raise ValueError
        except (ValueError, TypeError):
            flash("Please select a valid rating (1–5 stars).", "danger")
            return redirect(request.url)

        # Create pending review
        review = Review(
            user_id=current_user.id,
            course_id=course.id,
            rating=rating,
            comment=comment if comment else None,
            approved=False  # pending moderation
        )

        db.session.add(review)
        db.session.commit()

        flash("Thank you! Your review has been submitted and is pending approval.", "success")
        return redirect(url_for('courses.course_details', course_id=course.id))

    # GET: show the form
    return render_template('submit_review.html', course=course)