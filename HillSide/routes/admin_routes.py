from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from flask_login import login_user, logout_user, login_required, current_user
from HillSide.forms.register_form import RegisterForm
from HillSide.forms.login_form import LoginForm
from HillSide.forms.add_staff_form import AddStaffForm
from HillSide.extensions import db, bcrypt
from HillSide.models import User, Enrollment, Course, RoleEnum, GenderEnum
import os
from flask import current_app
from werkzeug.utils import secure_filename
from HillSide.utils import admin_required
from datetime import datetime
from sqlalchemy.orm import joinedload

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin-dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_courses = Course.query.count()
    total_enrollments = Enrollment.query.count()
    recent_enrollments = Enrollment.query.order_by(Enrollment.enrolled_on.desc()).limit(5).all()
    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_courses=total_courses,
                           total_enrollments=total_enrollments,
                           recent_enrollments=recent_enrollments)

@admin_bp.route('/manage_courses')
@login_required
@admin_required
def manage_courses():

    page = request.args.get('page', 1, type=int)
    pagination = Course.query.order_by(Course.id.desc()).paginate(
        page = page,
        per_page=25,
        error_out=False
    )
    return render_template('admin_manage_courses.html', courses=pagination.items, pagination=pagination)

@admin_bp.route('/manage_users')
@login_required
@admin_required
# def manage_users():
#     users = User.query.filter_by(role=RoleEnum.USER).all()
#     return render_template('admin_manage_users.html', users=users)
def manage_users():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '').strip()
    role = request.args.get('role', '').strip()

    filters = [User.role.in_([RoleEnum.USER])]

    if query:
        search = f"%{query}%"
        filters.append(db.or_(
            User.username.ilike(search),
            User.email.ilike(search)
        ))
    if role:
        filters.append(User.role == role)

    pagination = User.query.filter(*filters)\
        .order_by(User.id.desc())\
        .paginate(page=page, per_page=20, error_out=False)
   
    return render_template(
        'admin_manage_users.html',      # your template
        users=pagination.items,  # only the users for this page
        pagination=pagination    # the pagination object
    )
@admin_bp.route('/manage-staff', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_staff():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '').strip()
    role = request.args.get('role', '').strip()

    filters = [User.role.in_([RoleEnum.STAFF])]

    if query:
        search = f"%{query}%"
        filters.append(db.or_(
            User.username.ilike(search),
            User.email.ilike(search)
        ))
    if role:
        filters.append(User.role == role)

    pagination = User.query.filter(*filters)\
        .order_by(User.id.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    return render_template('admin_manage_staff.html', users=pagination.items, pagination=pagination)

@admin_bp.route('/user/<int:user_id>')
@login_required
@admin_required
def user_details(user_id):
    user = User.query.get_or_404(user_id)
    enrollments = Enrollment.query.filter_by(user_id=user.id).all()
    return render_template('admin_user_details.html', user=user, enrollments=enrollments)

@admin_bp.route('/staff/<int:staff_id>')
@login_required
@admin_required
def staff_details(staff_id):
    user = User.query.get_or_404(staff_id)
    enrollments = Enrollment.query.filter_by(user_id=user.id).all()
    return render_template('admin_staff_details.html', staff=user, enrollments=enrollments)


@admin_bp.route('/course/<int:course_id>')
@login_required
@admin_required
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    enrollments = Enrollment.query.filter_by(course_id=course.id).all()
    return render_template('admin_course_details.html', course=course, enrollments=enrollments)

@admin_bp.route('/enrollment/remove/<int:enrollment_id>', methods=['POST'])
@login_required
@admin_required
def remove_enrollment(enrollment_id):
    # Eager-load user and course to avoid lazy loads later
    enrollment = Enrollment.query.options(
        joinedload(Enrollment.user),
        joinedload(Enrollment.course)
    ).get_or_404(enrollment_id)
    
    user_username = enrollment.user.username  # Access early, while in session
    course_title = enrollment.course.title   # Access early too
    
    db.session.delete(enrollment)
    db.session.commit()
    
    flash(f'🧹 {user_username} has been removed from {course_title}.', 'info')
    return redirect(request.referrer or url_for('admin.manage_users'))
# def remove_enrollment(enrollment_id):
#     enrollment = Enrollment.query.get_or_404(enrollment_id)
#     db.session.delete(enrollment)
#     db.session.commit()
#     flash(f'🧹 {enrollment.user.username} has been removed from {enrollment.course.title}.', 'info')
#     return redirect(url_for('admin.course_details', course_id=enrollment.course_id))



@admin_bp.route('/course/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)

    if request.method == 'POST':
        course.title = request.form['title']
        course.description = request.form['description']
        course.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        course.duration_weeks = request.form['duration']
        course.total_seats = int(request.form['total_seats'])
        db.session.commit()
        flash('✅ Course updated successfully!', 'success')
        return redirect(url_for('admin.manage_courses'))

    return render_template('edit_course.html', course=course)

# @admin_bp.route('/staff/edit/<int:staff_id>', methods=['GET', 'POST'])
# @login_required
# @admin_required
# def edit_staff(staff_id):
#     user = User.query.get_or_404(staff_id)

#     form = AddStaffForm()
#     if(form.validate_on_submit()):
#         user.username = form.username.data
#         user.email = form.email.data
#         user.password = bcrypt.generate_password_hash(form.password.data)
#         return redirect(url_for('admin.admin_manage_staff'))
#     return render_template('edit_staff.html', form=form)

@admin_bp.route('/course/delete/<int:course_id>', methods=['POST'])
@login_required
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('🗑️ Course deleted successfully!', 'success')
    return redirect(url_for('admin.manage_courses'))

@admin_bp.route('/add-staff', methods=['GET', 'POST'])
@login_required
@admin_required
def add_staff():
    form = AddStaffForm()

    if form.validate_on_submit():

        # basic uniqueness checks
        if User.query.filter_by(username=form.username.data).first() or User.query.filter_by(email=form.email.data).first():
            flash("Username or email already exists.", "error")
            return render_template('add_staff.html', form=form)

        # Hash & decode password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        # create user instance
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            phone_number=form.phone_number.data or None,
            address=form.address.data or None,
            education_qualification=form.education_qualification.data or None,
        )

        # map role safely (accept either value or name)
        role_input = form.role.data
        try:
            # try by value first
            user.role = RoleEnum(role_input)
        except Exception:
            try:
                user.role = RoleEnum[role_input]
            except Exception:
                # fallback to default
                user.role = RoleEnum.STAFF

        # map gender safely (accept either value or name)
        gender_input = (form.gender.data or "").strip()
        if gender_input:
            try:
                user.gender = GenderEnum(gender_input)      # by value
            except Exception:
                try:
                    user.gender = GenderEnum[gender_input]  # by name (may fail)
                except Exception:
                    user.gender = None
        else:
            user.gender = None

        # Handle file uploads
        photos_folder = current_app.config.get("UPLOAD_FOLDER_PHOTOS", "static/uploads/photos")
        resumes_folder = current_app.config.get("UPLOAD_FOLDER_RESUMES", "static/uploads/resumes")
        os.makedirs(photos_folder, exist_ok=True)
        os.makedirs(resumes_folder, exist_ok=True)

        if form.photo.data:
            photo_file = form.photo.data
            photo_filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(photos_folder, photo_filename)
            photo_file.save(photo_path)
            # store a relative/path or filename depending on your preference
            user.photo = photo_filename

        if form.resume.data:
            resume_file = form.resume.data
            resume_filename = secure_filename(resume_file.filename)
            resume_path = os.path.join(resumes_folder, resume_filename)
            resume_file.save(resume_path)
            user.resume = resume_filename

        # persist user and any enrollments
        db.session.add(user)
        db.session.flush()  # to populate user.id

        selected_course_ids = session.pop('assigned_course_ids', [])
        for course_id in selected_course_ids:
            try:
                # optional: validate course_id exists
                course = Course.query.get(int(course_id))
                if course:
                    enrollment = Enrollment(user_id=user.id, course_id=course.id)
                    db.session.add(enrollment)
            except Exception:
                continue

        db.session.commit()
        flash("Staff user created successfully!", "success")
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('add_staff.html', form=form)

@admin_bp.route('/staff/<int:staff_id>/courses', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_staff(staff_id):
    staff = User.query.get_or_404(staff_id)

    all_courses = Course.query.all()
    assigned_ids = {e.course_id for e in staff.enrollments}

    unassigned = [c for c in all_courses if c.id not in assigned_ids]
    assigned = [c for c in all_courses if c.id in assigned_ids]

    # POST — Save updated course assignments
    if request.method == 'POST':
        new_assigned_ids = request.json.get('assigned', [])

        # Clear current enrollments
        Enrollment.query.filter_by(user_id=staff.id).delete()

        # Add new ones
        for cid in new_assigned_ids:
            db.session.add(Enrollment(user_id=staff.id, course_id=cid))

        db.session.commit()
        return {"status": "success"}, 200

    return render_template('edit_staff_courses.html',
                           assigned=assigned,
                           unassigned=unassigned)

@admin_bp.route('/add-staff/assgin-course/', methods=[ 'GET', 'POST'])
@login_required
@admin_required
def new_staff_assign_course():

    unassigned_courses = Course.query.all()
    assigned_courses = []

    if request.method == 'POST':
        assigned_ids = request.json.get('assigned', [])
        session['assigned_course_ids'] = assigned_ids
        return {"status": "success"}, 200
    
    return render_template('staff_course_assgn.html', assigned = assigned_courses, unassigned=unassigned_courses)
        

@admin_bp.route("/users")
def list_users():
    from HillSide.models import User
    users = User.query.all()
    return "<br>".join([f"{u.id} - {u.username} - {u.email} - {u.is_staff()}" for u in users])