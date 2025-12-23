from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from HillSide.forms.register_form import RegisterForm
from HillSide.forms.login_form import LoginForm
from HillSide.forms.forgot_password_form import ForgotPasswordForm
from HillSide.forms.reset_password_form import ResetPasswordForm
from HillSide.extensions import db, bcrypt
from HillSide.models import User, Enrollment
import os
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from HillSide.utils import send_reset_email, send_verification_email
from HillSide.config import Config

from itsdangerous import URLSafeTimedSerializer

def get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    print("Register route accessed")
    form = RegisterForm()

    if form.validate_on_submit():
        print("Register route accessed - form validated")
        # Hash password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        # Create user object (unverified by default)
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            phone_number=form.phone_number.data,
            address=form.address.data,
            gender=form.gender.data if form.gender.data else None,
            education_qualification=form.education_qualification.data,
            is_verified=False  # 🔥 IMPORTANT
        )

        # Handle profile photo upload
        if form.photo.data:
            photo_filename = secure_filename(form.photo.data.filename)
            form.photo.data.save(os.path.join(current_app.root_path, "static/uploads/photos", photo_filename))
            user.photo = photo_filename

        # Handle resume upload
        if form.resume.data:
            resume_filename = secure_filename(form.resume.data.filename)
            form.resume.data.save(os.path.join(current_app.root_path, "static/uploads/resumes", resume_filename))
            user.resume = resume_filename

        # Save user to DB
        try:
            db.session.add(user)
            db.session.commit()

            if current_app.config.get("TESTING") or not current_app.config.get("ENABLE_EMAIL_VERIFICATION", True):
                user.is_verified = True   # auto-verify in tests
                print("Auto-verified user in testing mode.")
            else:
                send_verification_email(user)
                print("sent verification email")


            flash("Registration successful! Please check your email to verify your account.", "info")
            return redirect(url_for('auth.login'))

        except IntegrityError as e:
            db.session.rollback()

            if "email" in str(e.orig):
                flash("Email already exists. Please use a different one.", "danger")
            elif "username" in str(e.orig):
                flash("Username already exists. Please choose a different one.", "danger")
            else:
                flash("A database error occurred. Please try again.", "danger")

    return render_template("register.html", form=form)



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        # ---- 1. User does not exist ----
        if not user:
            flash('Invalid email or password', 'danger')
            return render_template('login.html', form=form)

        # ---- 2. User exists but email NOT verified ----
        if not user.is_verified:
            flash(
                'Your account is not verified yet. Please check your email.',
                'warning'
            )
            return render_template(
                'login.html',
                form=form,
                show_resend=True,   # <-- appears ONLY when needed
                email=email         # <-- used by button
            )

        # ---- 3. Wrong password ----
        if not bcrypt.check_password_hash(user.password, password):
            flash('Invalid email or password', 'danger')
            return render_template('login.html', form=form)

        # ---- 4. Everything OK, log in ----
        login_user(user)
        return redirect(url_for('main.index'))

    return render_template('login.html', form=form)



@auth_bp.route("/dashboard")
@login_required
def dashboard():
    enrollments = Enrollment.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', enrollments=enrollments)

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        current_user.first_name = request.form['first_name']
        current_user.last_name = request.form['last_name']
        current_user.username = request.form['username']
        current_user.email = request.form['email']
        current_user.phone_number = request.form.get('phone_number') or None
        current_user.gender = request.form.get('gender') or None
        current_user.education_qualification = request.form.get('education_qualification') or None
        current_user.address = request.form.get('address') or None

        # Handle photo upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.root_path, "static/uploads/photos", filename))
                current_user.photo = filename

        # Handle resume upload
        if 'resume' in request.files:
            file = request.files['resume']
            if file and file.filename.lower().endswith('.pdf'):
                filename = secure_filename(f"resume_{current_user.id}.pdf")
                file.save(os.path.join(current_app.root_path, "static/uploads/resumes", filename))
                current_user.resume = filename

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.dashboard'))

    return redirect(url_for('auth.dashboard'))  # GET just shows the tab

@auth_bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
        flash("If this email exists, a reset link has been sent.", "info")
        return redirect(url_for("auth.login"))
    return render_template("forgot_password.html", form=form)


@auth_bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    print("Reset password route accessed")
    user = User.verify_reset_token(token)
    if not user:
        print("No user available")
        flash("Invalid or expired token.", "warning")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        print("token form validated")
        hashed_pw = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_pw
        db.session.commit()
        flash("Your password has been updated!", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", form=form)

@auth_bp.route('/verify/<token>')
def verify_email(token):
    try:
        email = get_serializer().loads(token, salt="email-verify", max_age=3600)
    except Exception:
        flash("The verification link is invalid or expired.", "danger")
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('auth.login'))

    if user.is_verified:
        flash("Your account is already verified. Please log in.", "info")
        return redirect(url_for('auth.login'))

    user.is_verified = True
    db.session.commit()

    flash("Your email has been verified! You can now log in.", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email')

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("No account found with that email.", "danger")
            return redirect(url_for('auth.resend_verification'))

        if user.is_verified:
            flash("Your account is already verified. Please log in.", "info")
            return redirect(url_for('auth.login'))

        # Send email again
        send_verification_email(user)

        flash("A new verification email has been sent.", "success")
        return redirect(url_for('auth.login'))

    return render_template("resend_verification.html")
