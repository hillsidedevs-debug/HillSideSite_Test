from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from HillSide.forms.register_form import RegisterForm
from HillSide.forms.login_form import LoginForm
from HillSide.extensions import db
from flask_bcrypt import Bcrypt
from HillSide.models import User, Enrollment, Course
from HillSide.utils import admin_required
from datetime import datetime

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
    courses = Course.query.all()
    return render_template('admin_manage_courses.html', courses=courses)

@admin_bp.route('/manage_users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin_manage_users.html', users=users)

@admin_bp.route('/user/<int:user_id>')
@login_required
@admin_required
def user_details(user_id):
    user = User.query.get_or_404(user_id)
    enrollments = Enrollment.query.filter_by(user_id=user.id).all()
    return render_template('admin_user_details.html', user=user, enrollments=enrollments)


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
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    db.session.delete(enrollment)
    db.session.commit()
    flash(f'🧹 {enrollment.user.username} has been removed from {enrollment.course.title}.', 'info')
    return redirect(url_for('admin.course_details', course_id=enrollment.course_id))



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
        return redirect(url_for('manage_courses'))

    return render_template('edit_course.html', course=course)

@admin_bp.route('/course/delete/<int:course_id>', methods=['POST'])
@login_required
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('🗑️ Course deleted successfully!', 'success')
    return redirect(url_for('manage_courses'))



@admin_bp.route("/users")
def list_users():
    from HillSide.models import User
    users = User.query.all()
    return "<br>".join([f"{u.id} - {u.username} - {u.email}" for u in users])